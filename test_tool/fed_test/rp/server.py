#!/usr/bin/env python3
import json
import os

import cherrypy
import logging
from jwkest import as_unicode, as_bytes
from oic.exception import MessageException
from oic.federation import MetadataStatement
from oic.federation.operator import FederationOperator
from oic.oauth2 import VerificationError
from oic.utils import webfinger

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


class Who(object):
    def __init__(self, fos):
        self.fos = fos

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return as_bytes(json.dumps(list(self.fos.keys())))


class Sign(object):
    def __init__(self, fos, me):
        self.fos = fos
        self.me = me

    @cherrypy.expose
    def index(self, **kwargs):
        if cherrypy.request.process_request_body is True:
            _json_doc = cherrypy.request.body.read()
        else:
            raise cherrypy.HTTPError(400, 'Missing Client registration body')

        _args = json.loads(as_unicode(_json_doc))
        _mds = MetadataStatement(**_args)

        try:
            _mds.verify()
        except (MessageException, VerificationError) as err:
            raise cherrypy.CherryPyException(str(err))
        else:
            try:
                _fo_iss = kwargs['fo']
            except KeyError:
                _fo_iss = self.me

            fo = self.fos[_fo_iss]
            _jwt = fo.pack_metadata_statement(_mds)
            cherrypy.response.headers['Content-Type'] = 'application/jwt'
            return as_bytes(_jwt)


class FoKeys(object):
    def __init__(self, fo):
        self.fo = fo

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'application/jwt'
        return as_bytes(self.fo.export_bundle())

    @cherrypy.expose
    def sigkey(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return as_bytes(json.dumps(self.fo.keyjar.export_jwks()))

    @cherrypy.expose
    def signer(self):
        return as_bytes(self.fo.iss)


def named_kc(config, iss):
    _kc = config.KEYDEFS[:]
    for kd in _kc:
        if 'key' in kd:
            kd['key'] = iss
    return _kc


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

    _fos = {}

    me = FederationOperator(iss=args.iss, bundle_sign_alg='RS256',
                            keyconf=named_kc(config, args.iss),
                            jwks_file='{}.json'.format(args.iss))
    _fos[args.iss] = me

    for fo in config.FOS:
        _fo = FederationOperator(iss=fo, keyconf=named_kc(config, fo),
                                 jwks_file='{}.json'.format(fo))
        me.add_to_bundle(fo, _fo.export_jwks())
        _fos[fo] = _fo

    fp = open(args.bundle, 'w')
    fp.write(me.export_bundle())
    fp.close()

    # sign_key = get_signing_keys(args.iss, KEYDEFS, args.sign_key)
    # jb = get_bundle(args.iss, config.FOS, sign_key, args.bundle,
    #                 config.KEYDEFS, config.BASE_PATH)

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

    cherrypy.tree.mount(Sign(_fos, args.iss), '/sign')
    cherrypy.tree.mount(FoKeys(me), '/bundle')
    cherrypy.tree.mount(Who(_fos), '/who')
    cherrypy.tree.mount(WebFinger(webfinger.WebFinger()),
                        '/.well-known/webfinger', webfinger_config)
    cherrypy.tree.mount(Provider(op_handler, _flows), '/', provider_config)

    if args.tls:
        cherrypy.server.ssl_certificate = config.SERVER_CERT
    cherrypy.server.ssl_private_key = config.SERVER_KEY

    cherrypy.engine.start()
    cherrypy.engine.block()
