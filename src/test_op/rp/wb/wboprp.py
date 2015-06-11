#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import importlib
import json
import os
from urllib import quote_plus
from urlparse import urlparse
import argparse
import logging
import sys
from oic.utils.keyio import build_keyjar
from oidctest.utils import setup_logging
from oidctest.io import WebIO
from oidctest.tool import WebTester

SERVER_LOG_FOLDER = "server_log"
if not os.path.isdir(SERVER_LOG_FOLDER):
    os.makedirs(SERVER_LOG_FOLDER)

def setup_common_log():
    global COMMON_LOGGER, hdlr, base_formatter
    COMMON_LOGGER = logging.getLogger("common")
    hdlr = logging.FileHandler("%s/common.log" % SERVER_LOG_FOLDER)
    base_formatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s %(message)s")
    hdlr.setFormatter(base_formatter)
    COMMON_LOGGER.addHandler(hdlr)
    COMMON_LOGGER.setLevel(logging.DEBUG)

setup_common_log()

try:
    from mako.lookup import TemplateLookup
    from oic.oic.message import factory as message_factory
    from oic.oauth2 import ResponseError
    from oic.utils import exception_trace
    from oic.utils.http_util import Redirect
    from oic.utils.http_util import get_post
    from oic.utils.http_util import BadRequest
    from oidctest.session import SessionHandler
except Exception as ex:
    COMMON_LOGGER.exception(ex)
    raise ex

LOGGER = logging.getLogger("")

ENV = None

def pick_args(args, kwargs):
    return dict([(k, kwargs[k]) for k in args])


def application(environ, start_response):
    LOGGER.info("Connection from: %s" % environ["REMOTE_ADDR"])
    session = environ['beaker.session']

    path = environ.get('PATH_INFO', '').lstrip('/')
    LOGGER.info("path: %s" % path)

    io = WebIO(**ENV)
    io.environ = environ
    io.start_response = start_response

    sh = SessionHandler(session, **ENV)

    tester = WebTester(io, sh, **ENV)

    if path == "robots.txt":
        return io.static("static/robots.txt")
    elif path == "favicon.ico":
        return io.static("static/favicon.ico")
    elif path.startswith("static/"):
        return io.static(path)
    elif path.startswith("export/"):
        return io.static(path)


    if path == "":  # list
        return tester.display_test_list()
    elif "flow_names" not in session:
        sh.session_init()

    if path == "logs":
        return io.display_log("log", issuer="", profile="", testid="")
    elif path.startswith("log"):
        if path == "log" or path == "log/":
            _cc = io.conf.CLIENT
            try:
                _iss = _cc["srv_discovery_url"]
            except KeyError:
                _iss = _cc["provider_info"]["issuer"]
            parts = [quote_plus(_iss)]
        else:
            parts = []
            while path != "log":
                head, tail = os.path.split(path)
                # tail = tail.replace(":", "%3A")
                # if tail.endswith("%2F"):
                #     tail = tail[:-3]
                parts.insert(0, tail)
                path = head

        return io.display_log("log", *parts)
    elif path.startswith("tar"):
        path = path.replace(":", "%3A")
        return io.static(path)

    if path == "reset":
        sh.reset_session(sh.session)
        return io.flow_list(session)
    elif path == "pedit":
        try:
            return io.profile_edit(session)
        except Exception as err:
            return io.err_response(session, "pedit", err)
    elif path == "profile":
        return tester.set_profile(environ)
    elif path.startswith("test_info"):
        p = path.split("/")
        try:
            return io.test_info(p[1], sh.session)
        except KeyError:
            return io.not_found()
    elif path == "continue":
        return tester.cont(environ)
    elif path == "opresult":
        if tester.conv is None:
            return io.sorry_response("", "No result to report")

        return io.opresult(tester.conv, sh.session)
    # expected path format: /<testid>[/<endpoint>]
    elif path in session["flow_names"]:
        return tester.run(path, **ENV)
    elif path in ["authz_cb", "authz_post"]:
        if path == "authz_cb":
            _conv = session["conv"]
            try:
                response_mode = _conv.req.req_args["response_mode"]
            except KeyError:
                response_mode = ""

            # Check if fragment encoded
            if response_mode == "form_post":
                pass
            else:
                try:
                    response_type = _conv.req.req_args["response_type"]
                except KeyError:
                    response_type = ""

                if response_type != ["code"]:
                    # but what if it's all returned as a query anyway ?
                    try:
                        qs = environ["QUERY_STRING"]
                    except KeyError:
                        pass
                    else:
                        _conv.trace.response("QUERY_STRING:%s" % qs)
                        _conv.query_component = qs

                    return io.opresult_fragment()

        try:
            tester.async_response(ENV["conf"])
        except Exception as err:
            return io.err_response(session, "authz_cb", err)
        else:
            return io.flow_list(session)
    else:
        resp = BadRequest()
        return resp(environ, start_response)


if __name__ == '__main__':
    from beaker.middleware import SessionMiddleware
    from cherrypy import wsgiserver
    from oictest.check import factory as check_factory
    from oic.oic.message import factory as oic_message_factory

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', dest='mailaddr')
    parser.add_argument('-o', dest='operations')
    parser.add_argument('-f', dest='testflows')
    parser.add_argument('-d', dest='directory')
    parser.add_argument('-p', dest='profile')
    parser.add_argument('-P', dest='profiles')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    # global ACR_VALUES
    # ACR_VALUES = CONF.ACR_VALUES

    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': True,
        'session.auto': True,
        'session.timeout': 900
    }

    sys.path.insert(0, ".")
    CONF = importlib.import_module(args.config)

    setup_logging("%s/rp_%s.log" % (SERVER_LOG_FOLDER, CONF.PORT), LOGGER)

    # Flow definitions
    if "/" in args.testflows:
        head, tail = os.path.split(args.testflows)
        sys.path.insert(0, head)
        if tail.endswith(".py"):
            tail = tail[:-3]
        FLOWS = importlib.import_module(tail)
    else:
        FLOWS = importlib.import_module(args.testflows)

    if args.profiles:
        profiles = importlib.import_module(args.profiles)
    else:
        from oidctest import profiles

    if args.operations:
        operations = importlib.import_module(args.operations)
    else:
        from oidctest import oper as operations

    if args.directory:
        _dir = args.directory
        if not _dir.endswith("/"):
            _dir += "/"
    else:
        _dir = "./"

    if args.profile:
        TEST_PROFILE = args.profile
    else:
        TEST_PROFILE = "C.T.T.ns"

    # Add own keys for signing/encrypting JWTs
    jwks, keyjar, kidd = build_keyjar(CONF.keys)

    # export JWKS
    p = urlparse(CONF.KEY_EXPORT_URL)
    f = open("."+p.path, "w")
    f.write(json.dumps(jwks))
    f.close()
    jwks_uri = p.geturl()

    LOOKUP = TemplateLookup(directories=[_dir + 'templates', _dir + 'htdocs'],
                            module_directory=_dir + 'modules',
                            input_encoding='utf-8',
                            output_encoding='utf-8')

    ENV = {"base_url": CONF.BASE, "kidd": kidd, "keyjar": keyjar,
           "jwks_uri": jwks_uri, "flows": FLOWS.FLOWS, "conf": CONF,
           "cinfo": CONF.INFO, "orddesc": FLOWS.ORDDESC,
           "profiles": profiles, "operation": operations,
           "profile": args.profile, "msg_factory": oic_message_factory,
           "check_factory": check_factory, "lookup": LOOKUP,
           "desc": FLOWS.DESC, "cache": {}}

    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', CONF.PORT),
                                        SessionMiddleware(application,
                                                          session_opts))

    if CONF.BASE.startswith("https"):
        import cherrypy
        from cherrypy.wsgiserver import ssl_pyopenssl
        # from OpenSSL import SSL

        SRV.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(
            CONF.SERVER_CERT, CONF.SERVER_KEY, CONF.CA_BUNDLE)
        # SRV.ssl_adapter.context = SSL.Context(SSL.SSLv23_METHOD)
        # SRV.ssl_adapter.context.set_options(SSL.OP_NO_SSLv3)
        try:
            cherrypy.server.ssl_certificate_chain = CONF.CERT_CHAIN
        except AttributeError:
            pass
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "RP server starting listening on port:%s%s" % (CONF.PORT, extra)
    LOGGER.info(txt)
    print(txt)
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
