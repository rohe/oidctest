import json

import cherrypy
from jwkest import as_bytes, as_unicode
from oic.exception import MessageException
from oic.federation import MetadataStatement
from oic.oauth2 import VerificationError


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