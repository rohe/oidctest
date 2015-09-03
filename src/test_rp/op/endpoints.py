import logging
import os
from urlparse import urlparse, parse_qs
from oic.utils.http_util import extract_from_request, Response, Unauthorized, \
    NotFound
from oic.utils.http_util import ServiceError
from oic.utils.http_util import BadRequest
from oic.utils.webfinger import OIC_ISSUER, WebFinger

import pathmap

__author__ = 'roland'

LOGGER = logging.getLogger(__name__)

HEADER = "---------- %s ----------"


def dump_log(session_info, trace):
    file_name = os.path.join("log", session_info["addr"],
                             session_info["test_id"])
    fp = open(file_name, "a+")
    fp.write("{0}".format(trace))
    fp.write("\n\n")
    fp.close()


def find_identifier(uri):
    if uri.startswith("http"):
        p = urlparse(uri)
        return p.path[1:]  # Skip leading "/"
    elif uri.startswith("acct:"):
        a = uri[5:]
        l, d = a.split("@")
        return l


def wsgi_wrapper(environ, start_response, func, session_info, trace, **kwargs):
    kwargs = extract_from_request(environ)
    trace.request(kwargs["request"])
    args = func(**kwargs)

    try:
        resp, state = args
        trace.reply(resp.message)
        dump_log(session_info, trace)
        return resp(environ, start_response)
    except TypeError:
        resp = args
        trace.reply(resp.message)
        dump_log(session_info, trace)
        return resp(environ, start_response)
    except Exception as err:
        # LOGGER.error("%s" % err)
        trace.error("%s" % err)
        dump_log(session_info, trace)
        raise


# noinspection PyUnusedLocal
def token(environ, start_response, session_info, trace, **kwargs):
    trace.info(HEADER % "AccessToken")
    _op = session_info["op"]

    return wsgi_wrapper(environ, start_response, _op.token_endpoint,
                        session_info,
                        trace)


# noinspection PyUnusedLocal
def authorization(environ, start_response, session_info, trace, **kwargs):
    trace.info(HEADER % "Authorization")
    _op = session_info["op"]

    return wsgi_wrapper(environ, start_response, _op.authorization_endpoint,
                        session_info, trace)


# noinspection PyUnusedLocal
def userinfo(environ, start_response, session_info, trace, **kwargs):
    trace.info(HEADER % "UserInfo")
    _op = session_info["op"]
    return wsgi_wrapper(environ, start_response, _op.userinfo_endpoint,
                        session_info, trace)


# noinspection PyUnusedLocal
def op_info(environ, start_response, session_info, trace, **kwargs):
    trace.info(HEADER % "ProviderConfiguration")
    trace.request("PATH: %s" % environ["PATH_INFO"])
    try:
        trace.request("QUERY: %s" % environ["QUERY_STRING"])
    except KeyError:
        pass
    _op = session_info["op"]
    return wsgi_wrapper(environ, start_response, _op.providerinfo_endpoint,
                        session_info, trace)


# noinspection PyUnusedLocal
def registration(environ, start_response, session_info, trace, **kwargs):
    trace.info(HEADER % "ClientRegistration")
    _op = session_info["op"]

    if environ["REQUEST_METHOD"] == "POST":
        return wsgi_wrapper(environ, start_response, _op.registration_endpoint,
                            session_info, trace)
    elif environ["REQUEST_METHOD"] == "GET":
        return wsgi_wrapper(environ, start_response, _op.read_registration,
                            session_info, trace)
    else:
        resp = ServiceError("Method not supported")
        return resp(environ, start_response)


# noinspection PyUnusedLocal
def check_id(environ, start_response, session_info, trace, **kwargs):
    _op = session_info["op"]

    return wsgi_wrapper(environ, start_response, _op.check_id_endpoint,
                        session_info, trace)


# noinspection PyUnusedLocal
def endsession(environ, start_response, session_info, trace, **kwargs):
    _op = session_info["op"]
    return wsgi_wrapper(environ, start_response, _op.endsession_endpoint,
                        session_info=session_info, trace=trace)


def webfinger(environ, start_response, session_info, trace, **kwargs):
    query = parse_qs(environ["QUERY_STRING"])

    # Find the identifier
    session_info["test_id"] = find_identifier(query["resource"][0])

    trace.info(HEADER % "WebFinger")
    trace.request(environ["QUERY_STRING"])
    trace.info("QUERY: %s" % (query,))

    try:
        assert query["rel"] == [OIC_ISSUER]
        resource = query["resource"][0]
    except AssertionError:
        errmsg = "Wrong 'rel' value: %s" % query["rel"][0]
        trace.error(errmsg)
        resp = BadRequest(errmsg)
    except KeyError:
        errmsg = "Missing 'rel' parameter in request"
        trace.error(errmsg)
        resp = BadRequest(errmsg)
    else:
        wf = WebFinger()
        p = urlparse(resource)

        if p.scheme == "acct":
            l, _ = p.path.split("@")
            path = pathmap.IDMAP[l]
        else:  # scheme == http/-s
            try:
                path = pathmap.IDMAP[p.path[1:]]
            except KeyError:
                path = None

        if path:
            _url = os.path.join(kwargs["op_arg"]["baseurl"],
                                session_info["test_id"],
                                path[1:])
            resp = Response(wf.response(subject=resource, base=_url),
                            content="application/jrd+json")
        else:
            resp = BadRequest("Incorrect resource specification")

        trace.reply(resp.message)

    dump_log(session_info, trace)
    return resp(environ, start_response)


# noinspection PyUnusedLocal
def verify(environ, start_response, session_info, trace, **kwargs):
    _op = session_info["op"]
    return wsgi_wrapper(environ, start_response, _op.verify_endpoint,
                        session_info, trace)


def static_file(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


# noinspection PyUnresolvedReferences
def static(environ, start_response, path):
    LOGGER.info("[static]sending: %s" % (path,))

    try:
        text = open(path).read()
        if path.endswith(".ico"):
            start_response('200 OK', [('Content-Type', "image/x-icon")])
        elif path.endswith(".html"):
            start_response('200 OK', [('Content-Type', 'text/html')])
        elif path.endswith(".json"):
            start_response('200 OK', [('Content-Type', 'application/json')])
        elif path.endswith(".txt"):
            start_response('200 OK', [('Content-Type', 'text/plain')])
        elif path.endswith(".css"):
            start_response('200 OK', [('Content-Type', 'text/css')])
        else:
            start_response('200 OK', [('Content-Type', 'text/plain')])
        return [text]
    except IOError:
        resp = NotFound()
        return resp(environ, start_response)


# noinspection PyUnusedLocal
def safe(environ, start_response):
    _op = environ["oic.oas"]
    _srv = _op.server
    _log_info = _op.logger.info

    _log_info("- safe -")
    # _log_info("env: %s" % environ)
    # _log_info("handle: %s" % (handle,))

    try:
        _authz = environ["HTTP_AUTHORIZATION"]
        (_typ, code) = _authz.split(" ")
        assert _typ == "Bearer"
    except KeyError:
        resp = BadRequest("Missing authorization information")
        return resp(environ, start_response)

    try:
        _sinfo = _srv.sdb[code]
    except KeyError:
        resp = Unauthorized("Not authorized")
        return resp(environ, start_response)

    _info = "'%s' secrets" % _sinfo["sub"]
    resp = Response(_info)
    return resp(environ, start_response)


# noinspection PyUnusedLocal
def css(environ, start_response):
    try:
        _info = open(environ["PATH_INFO"]).read()
        resp = Response(_info)
    except (OSError, IOError):
        resp = NotFound(environ["PATH_INFO"])

    return resp(environ, start_response)


# ----------------------------------------------------------------------------


def display_log(environ, start_response, lookup):
    path = environ.get('PATH_INFO', '').lstrip('/')
    if path == "log":
        tail = environ["REMOTE_ADDR"]
        path = os.path.join(path, tail)
    elif path == "logs":
        path = "log"

    if os.path.isfile(path):
        return static(environ, start_response, path)
    elif os.path.isdir(path):
        item = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            if dirnames:
                # item = [(fn, os.path.join(path, fn)) for fn in dirnames]
                item = [(fn, fn) for fn in dirnames]
                break
            if filenames:
                # item = [(fn, os.path.join(path, fn)) for fn in filenames]
                item = [(fn, fn) for fn in filenames]
                break

        item.sort()
        resp = Response(mako_template="logs.mako",
                        template_lookup=lookup,
                        headers=[])
        argv = {"logs": item}

        return resp(environ, start_response, **argv)
    else:
        resp = Response("No saved logs")
        return resp(environ, start_response)


# All endpoints the OpenID Connect Provider should answer on
from oic.oic.provider import AuthorizationEndpoint
from oic.oic.provider import EndSessionEndpoint
from oic.oic.provider import TokenEndpoint
from oic.oic.provider import UserinfoEndpoint
from oic.oic.provider import RegistrationEndpoint

ENDPOINTS = [
    AuthorizationEndpoint(authorization),
    TokenEndpoint(token),
    UserinfoEndpoint(userinfo),
    RegistrationEndpoint(registration),
    EndSessionEndpoint(endsession),
]

URLS = [
    (r'^verify', verify),
    (r'.well-known/openid-configuration', op_info),
    (r'.well-known/webfinger', webfinger),
    (r'.+\.css$', css),
    (r'safe', safe),
    (r'log', display_log)
]


def add_endpoints(extra):
    global URLS

    for endp in extra:
        URLS.append(("^%s" % endp.etype, endp))
