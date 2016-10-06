import logging
from mako.lookup import TemplateLookup
from oic.utils.http_util import Response
from oic.utils.http_util import ServiceError
from oic.utils.http_util import NotFound

from oidctest.common import main_setup
from oidctest.common import make_client
from oidctest.common import make_list
from oidctest.common import Conversation
from oidctest.common import run_flow
from oidctest.common import node_dict

__author__ = 'roland'

logger = logging.getLogger("")

LOOKUP = TemplateLookup(directories=['templates', 'htdocs'],
                        module_directory='modules',
                        input_encoding='utf-8',
                        output_encoding='utf-8')


# =============================================================================

def static(environ, start_response, path):
    logger.info("[static]sending: %s" % (path,))

    try:
        text = open(path).read()
        if path.endswith(".ico"):
            start_response('200 OK', [('Content-Type', "image/x-icon")])
        elif path.endswith(".html"):
            start_response('200 OK', [('Content-Type', 'text/html')])
        elif path.endswith(".json"):
            start_response('200 OK', [('Content-Type', 'application/json')])
        elif path.endswith(".jwt"):
            start_response('200 OK', [('Content-Type', 'application/jwt')])
        elif path.endswith(".txt"):
            start_response('200 OK', [('Content-Type', 'text/plain')])
        elif path.endswith(".css"):
            start_response('200 OK', [('Content-Type', 'text/css')])
        else:
            start_response('200 OK', [('Content-Type', "text/plain")])
        return [text]
    except IOError:
        resp = NotFound()
        return resp(environ, start_response)


def flow_list(environ, start_response, flows, done):
    resp = Response(mako_template="flowlist.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    argv = {"base": KW_ARGS["conf"].BASE, "flows": flows, "done": done}

    return resp(environ, start_response, **argv)


def opresult_fragment(environ, start_response):
    resp = Response(mako_template="opresult_repost.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    argv = {}
    return resp(environ, start_response, **argv)


# -----------------------------------------------------------------------------

def application(environ, start_response):
    session = environ['beaker.session']
    path = environ.get('PATH_INFO', '').lstrip('/')

    try:
        _cli = session["client"]
    except KeyError:
        _cli = session["client"] = make_client(**KW_ARGS)
        session["done"] = []

    _flows = KW_ARGS["flows"]

    if path == "robots.txt":
        return static(environ, start_response, "static/robots.txt")
    elif path.startswith("static/"):
        return static(environ, start_response, path)
    elif path.startswith("export/"):
        return static(environ, start_response, path)

    if path == "":  # list
        session["done"] = []
        session["flows"] = make_list(**KW_ARGS)
        return flow_list(environ, start_response,
                         node_dict(_flows, session["flows"]),
                         session["done"])
    elif path in list(_flows.keys()):
        try:
            redirs = KW_ARGS["cinfo"]["client"]["redirect_uris"]
        except KeyError:
            redirs = KW_ARGS["cinfo"]["registered"]["redirect_uris"]

        conversation = Conversation(_flows[path], _cli, redirs)
        session["rf_args"] = {
            "profiles": KW_ARGS["profiles"], "test_id": path,
            "conv": conversation, "conf": KW_ARGS["conf"],
            "profile": KW_ARGS["profile"]}

        try:
            resp = run_flow(**session["rf_args"])
        except Exception as err:
            resp = ServiceError("%s" % err)
            return resp(environ, start_response)
        else:
            if resp:
                return resp(environ, start_response)
            else:
                session["done"].append(path)
                return flow_list(environ, start_response,
                                 node_dict(_flows, session["flows"]),
                                 session["done"])
    else:
        logger.debug("unknown side: %s" % path)
        resp = NotFound("Couldn't find the side you asked for!")
        return resp(environ, start_response)


# =============================================================================

if __name__ == '__main__':
    from beaker.middleware import SessionMiddleware
    from cherrypy import wsgiserver

    KW_ARGS = main_setup(logger)

    _conf = KW_ARGS["conf"]
    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': True,
        'session.auto': True,
        'session.timeout': 900
    }

    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', _conf.PORT),
                                        SessionMiddleware(application,
                                                          session_opts))

    if _conf.BASE.startswith("https"):
        from cherrypy.wsgiserver import ssl_pyopenssl

        SRV.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(
            _conf.SERVER_CERT, _conf.SERVER_KEY, _conf.CA_BUNDLE)

    logger.info("RP server starting listening on port:%s" % _conf.PORT)
    print("RP server starting listening on port:%s" % _conf.PORT)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
