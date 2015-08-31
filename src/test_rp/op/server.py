#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import sys
import traceback
import logging

from exceptions import KeyError
from exceptions import Exception
from exceptions import IndexError
from exceptions import AttributeError
from exceptions import KeyboardInterrupt
from urlparse import parse_qs
from urlparse import urlparse

from oic.utils.client_management import CDB
from oic.utils.http_util import BadRequest
from oic.utils.http_util import Response
from oic.utils.http_util import NotFound
from oic.utils.http_util import ServiceError

from aatest import Trace
from oidctest.mode import extract_mode
from oidctest.mode import setup_op
from oidctest.mode import mode2path

from response_encoder import ResponseEncoder
from endpoints import static
from endpoints import display_log
from endpoints import URLS

__author__ = 'rohe0002'

from mako.lookup import TemplateLookup

LOGGER = logging.getLogger("")
LOGFILE_NAME = 'oc.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

CPC = ('%(asctime)s %(name)s:%(levelname)s '
       '[%(client)s,%(path)s,%(cid)s] %(message)s')
cpc_formatter = logging.Formatter(CPC)

hdlr.setFormatter(base_formatter)
LOGGER.addHandler(hdlr)
LOGGER.setLevel(logging.DEBUG)

URLMAP = {}
NAME = "pyoic"
OP = {}

PASSWD = {
    "diana": "krall",
    "babs": "howes",
    "upper": "crust"
}

# ----------------------------------------------------------------------------

ROOT = './'

LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')


# ----------------------------------------------------------------------------


def rp_support_3rd_party_init_login(environ, start_response):
    resp = Response(mako_template="rp_support_3rd_party_init_login.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    return resp(environ, start_response)


def rp_test_list(environ, start_response):
    resp = Response(mako_template="rp_test_list.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    return resp(environ, start_response)


def registration(environ, start_response):
    resp = Response(mako_template="registration.mako",
                    template_lookup=LOOKUP,
                    headers=[])
    return resp(environ, start_response)


def generate_static_client_credentials(parameters):
    redirect_uris = parameters['redirect_uris']
    jwks_uri = str(parameters['jwks_uri'][0])
    _cdb = CDB(config.CLIENT_DB)
    static_client = _cdb.create(redirect_uris=redirect_uris,
                                # policy_uri="example.com",
                                # logo_uri="example.com",
                                jwks_uri=jwks_uri)
    return static_client['client_id'], static_client['client_secret']


def op_setup(environ, mode, trace):
    addr = environ.get("REMOTE_ADDR", '')
    path = mode2path(mode)

    key = "{}:{}".format(addr, path)
    LOGGER.debug("OP key: {}".format(key))
    try:
        _op = OP[key]
    except KeyError:
        if mode["test_id"] == 'rp-id_token-kid_absent_multiple_jwks':
            _op_args = {}
            for param in ['baseurl', 'cookie_name', 'cookie_ttl', 'endpoints']:
                _op_args[param] = OP_ARG[param]
            for param in ["jwks", "keys"]:
                _op_args[param] = OP_ARG["marg"][param]
            _op = setup_op(mode, COM_ARGS, _op_args, trace)
        else:
            _op = setup_op(mode, COM_ARGS, OP_ARG, trace)
        OP[key] = _op

    return _op, path


def application(environ, start_response):
    """
    :param environ: The HTTP application environment
    :param start_response: The application to run when the handling of the
        request is done
    :return: The response as a list of lines
    """

    kaka = environ.get("HTTP_COOKIE", '')
    LOGGER.debug("Cookie: {}".format(kaka))

    path = environ.get('PATH_INFO', '').lstrip('/')
    response_encoder = ResponseEncoder(environ=environ,
                                       start_response=start_response)
    parameters = parse_qs(environ["QUERY_STRING"])

    session_info = {
        "addr": environ.get("REMOTE_ADDR", '')}

    if path == "robots.txt":
        return static(environ, start_response, "static/robots.txt")

    if path.startswith("static/"):
        return static(environ, start_response, path)
    elif path.startswith("log"):
        return display_log(environ, start_response, lookup=LOOKUP)
    elif path.startswith("_static/"):
        return static(environ, start_response, path)
    elif path.startswith("jwks.json"):
        try:
            mode, endpoint = extract_mode(OP_ARG["baseurl"])
            op, path = op_setup(environ, mode)
            jwks = op.generate_jwks(mode)
            resp = Response(jwks,
                            headers=[('Content-Type', 'application/json')])
            return resp(environ, start_response)
        except KeyError:
            # Try to load from static file
            return static(environ, start_response, "static/jwks.json")

    trace = Trace(absolut_start=True)

    if path == "test_list":
        return rp_test_list(environ, start_response)
    elif path == "":
        return registration(environ, start_response)
    elif path == "generate_client_credentials":
        client_id, client_secret = generate_static_client_credentials(
            parameters)
        return response_encoder.return_json(
            json.dumps({"client_id": client_id,
                        "client_secret": client_secret}))
    elif path == "claim":
        authz = environ["HTTP_AUTHORIZATION"]
        try:
            assert authz.startswith("Bearer")
        except AssertionError:
            resp = BadRequest()
        else:
            tok = authz[7:]
            mode, endpoint = extract_mode(OP_ARG["baseurl"])
            _op, _ = op_setup(environ, mode)
            try:
                _claims = _op.claim_access_token[tok]
            except KeyError:
                resp = BadRequest()
            else:
                del _op.claim_access_token[tok]
                resp = Response(json.dumps(_claims), content='application/json')
        return resp(environ, start_response)
    elif path == "3rd_party_init_login":
        return rp_support_3rd_party_init_login(environ, start_response)

    mode, endpoint = extract_mode(path)

    if endpoint == ".well-known/webfinger":
        try:
            _p = urlparse(parameters["resource"][0])
        except KeyError:
            resp = ServiceError("No resource defined")
            return resp(environ, start_response)

        if _p.scheme in ["http", "https"]:
            mode = {"test_id": _p.path[1:]}
        elif _p.scheme == "acct":
            _l, _ = _p.path.split('@')
            mode = {"test_id": _l}
        else:
            resp = ServiceError("Unknown scheme: {}".format(_p.scheme))
            return resp(environ, start_response)

    if mode:
        session_info["test_id"] = mode["test_id"]

    _op, path = op_setup(environ, mode, trace)

    session_info["op"] = _op
    session_info["path"] = path

    for regex, callback in URLS:
        match = re.search(regex, endpoint)
        if match is not None:
            trace.request("PATH: %s" % endpoint)
            trace.request("METHOD: %s" % environ["REQUEST_METHOD"])
            try:
                trace.request(
                    "HTTP_AUTHORIZATION: %s" % environ["HTTP_AUTHORIZATION"])
            except KeyError:
                pass

            try:
                environ['oic.url_args'] = match.groups()[0]
            except IndexError:
                environ['oic.url_args'] = endpoint

            LOGGER.info("callback: %s" % callback)
            try:
                return callback(environ, start_response, session_info, trace,
                                op_arg=OP_ARG)
            except Exception as err:
                print >> sys.stderr, "%s" % err
                message = traceback.format_exception(*sys.exc_info())
                print >> sys.stderr, message
                LOGGER.exception("%s" % err)
                resp = ServiceError("%s" % err)
                return resp(environ, start_response)

    LOGGER.debug("unknown page: '{}'".format(endpoint))
    resp = NotFound("Couldn't find the side you asked for!")
    return resp(environ, start_response)


# ----------------------------------------------------------------------------



if __name__ == '__main__':
    import argparse

    from cherrypy import wsgiserver
    from cherrypy.wsgiserver import ssl_pyopenssl

    from setup import main_setup

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    COM_ARGS, OP_ARG, config = main_setup(args, LOOKUP)

    # Setup the web server
    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', args.port), application, )

    if OP_ARG["baseurl"].startswith("https"):
        import cherrypy
        from cherrypy.wsgiserver import ssl_pyopenssl
        # from OpenSSL import SSL

        SRV.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(
            config.SERVER_CERT, config.SERVER_KEY, config.CA_BUNDLE)
        # SRV.ssl_adapter.context = SSL.Context(SSL.SSLv23_METHOD)
        # SRV.ssl_adapter.context.set_options(SSL.OP_NO_SSLv3)
        try:
            cherrypy.server.ssl_certificate_chain = config.CERT_CHAIN
        except AttributeError:
            pass
        extra = " using SSL/TLS"
    else:
        extra = ""

    txt = "RP server starting listening on port:%s%s" % (args.port, extra)
    LOGGER.info(txt)
    print txt
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
