#!/usr/bin/env python3
import json
import os

import cherrypy
import logging
from oic.exception import MessageException
from oic.federation import MetadataStatement
from oic.federation.bundle import get_bundle
from oic.federation.bundle import get_signing_keys
from oic.utils import webfinger
from oic.utils.jwt import JWT

from oidctest.cp.op import Provider
from oidctest.cp.op import WebFinger
from oidctest.cp.op_handler import OPHandler
from otest.flow import Flow
from otest.prof_util import SimpleProfileHandler
from src.oidctest.cp.setup import cb_setup

logger = logging.getLogger("")
LOGFILE_NAME = 'rp_test.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]


class Sign(object):
    def __init__(self, sign_keys, iss):
        self.sign_keys = sign_keys
        self.iss = iss

    @cherrypy.expose
    def index(self, mds):
        _mds = MetadataStatement(**json.loads(mds))
        try:
            _mds.verify()
        except MessageException as err:
            raise cherrypy.CherryPyException()
        else:
            _jwt = JWT(self.sign_keys, lifetime=3600, iss=self.iss)
            jws = _jwt.pack(data=_mds)
            cherrypy.response.headers['Content-Type'] = 'application/jwt'
            return jws


class FoKeys(object):
    def __init__(self, sign_keys):
        self.sign_keys = sign_keys

    @cherrypy.expose
    def index(self, mds):
        pass


if __name__ == '__main__':
    import argparse
    from oidctest.rp import provider

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', dest='bundle', required=True)
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('-f', dest='flowsdir', required=True)
    parser.add_argument('-i', dest='iss', required=True)
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-P', dest='path')
    parser.add_argument('-s', dest='sign_key', required=True)
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _com_args, _op_arg, config = cb_setup(args)

    sign_key = get_signing_keys(args.iss, KEYDEFS, args.sign_key)
    jb = get_bundle(args.iss, config.FOS, sign_key, args.bundle,
                    config.KEYDEFS, config.BASE_PATH)

    folder = os.path.abspath(os.curdir)
    _flows = Flow(args.flowsdir, profile_handler=SimpleProfileHandler)
    op_handler = OPHandler(provider.Provider, _op_arg, _com_args, _flows)

    cherrypy.config.update(
        {'environment': 'production',
         'log.error_file': 'site.log',
         'tools.trailing_slash.on': False,
         'server.socket_host': '0.0.0.0',
         'log.screen': True,
         'tools.sessions.on': True,
         'tools.encode.on': True,
         'tools.encode.encoding': 'utf-8'
         })

    provider_config = {
        '/': {
            'root_path': 'localhost',
            'log.screen': True,
        },
        '/static': {
            'tools.staticdir.dir': os.path.join(folder, 'static'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True
        }}

    webfinger_config = {'/': {'base_url': _op_arg['baseurl']}}

    cherrypy.tree.mount(Sign(sign_key, args.iss), '/sign')
    cherrypy.tree.mount(FoKeys(jb), '/fokeys')
    cherrypy.tree.mount(WebFinger(webfinger.WebFinger()),
                        '/.well-known/webfinger', webfinger_config)
    cherrypy.tree.mount(Provider(op_handler, _flows), '/', provider_config)

    if args.tls:
        cherrypy.server.ssl_certificate = config.SERVER_CERT
    cherrypy.server.ssl_private_key = config.SERVER_KEY

    cherrypy.engine.start()
    cherrypy.engine.block()
