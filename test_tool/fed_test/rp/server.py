#!/usr/bin/env python3
import json
import os

import cherrypy
from oic.exception import MessageException
from oic.federation import JWKSBundle, MetadataStatement
from oic.utils.jwt import JWT
from oic.utils.keyio import KeyJar, build_keyjar

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]


class Main(object):

    @cherrypy.expose
    def index(self):
        pass


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

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='sign_key')
    parser.add_argument('-i', dest='iss')
    parser.add_argument('-b', dest='bundle')
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

    cherrypy.tree.mount(Main(), '/')
    cherrypy.tree.mount(Sign(kj, args.iss), '/sign')
    cherrypy.tree.mount(FoKeys(jb), '/fokeys')

    cherrypy.engine.start()
    cherrypy.engine.block()