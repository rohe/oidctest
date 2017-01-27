#!/usr/bin/env python3
import json
import os

import cherrypy
from oic.exception import MessageException
from oic.federation import JWKSBundle, MetadataStatement
from oic.utils import webfinger
from oic.utils.jwt import JWT
from oic.utils.keyio import KeyJar, build_keyjar

from oidctest.cp.op import Provider
from oidctest.cp.op import WebFinger
from oidctest.cp.op_handler import OPHandler
from oidctest.cp.setup import main_setup

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]


def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        "<html><body>Sorry, an error occured</body></html>"
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
    parser.add_argument('-f', dest='flowsdir', required=True)
    parser.add_argument('-i', dest='iss', required=True)
    parser.add_argument('-k', dest='insecure', action='store_true')
    parser.add_argument('-p', dest='port', default=80, type=int)
    parser.add_argument('-P', dest='path')
    parser.add_argument('-s', dest='sign_key', required=True)
    parser.add_argument('-t', dest='tls', action='store_true')
    parser.add_argument(dest="config")
    args = parser.parse_args()

    if os.path.isfile(args.sign_key):
        kj = KeyJar()
        kj.import_jwks(json.loads(open(args.sign_key, 'r').read()), args.iss)
    else:
        kj = build_keyjar(KEYDEFS)[1]
        fp = open(args.sign_key, 'w')
        fp.write(json.dumps(kj.export_jwks()))
        fp.close()

    jb = JWKSBundle(iss=args.iss, sign_keys=kj)
    jb.loads(json.loads(open(args.bundle,'r').read()))

    cherrypy.tree.mount(Sign(kj, args.iss), '/sign')
    cherrypy.tree.mount(FoKeys(jb), '/fokeys')
    cherrypy.tree.mount(WebFinger(webfinger.WebFinger()),
                        '/.well-known/webfinger')

    _com_args, _op_arg, config = main_setup(args)

    op_handler = OPHandler(provider.Provider, _op_arg, _com_args, config)
    cherrypy.tree.mount(Provider(op_handler), '/')

    cherrypy.engine.start()
    cherrypy.engine.block()