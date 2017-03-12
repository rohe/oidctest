import json

import cherrypy
from jwkest import as_bytes, as_unicode
from fedoidc import MetadataStatement
from oic.oauth2 import MessageException
from oic.oauth2 import VerificationError


class Who(object):
    def __init__(self, fos):
        self.fos = fos

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return as_bytes(json.dumps(list(self.fos.values())))


class Sign(object):
    def __init__(self, signer):
        self.signer = signer

    @cherrypy.expose
    def index(self, signer='', **kwargs):
        if not signer:
            raise cherrypy.HTTPError(400, 'Missing signer')
        if signer not in self.signer:
            raise cherrypy.HTTPError(400, 'unknown signer')

        if cherrypy.request.process_request_body is True:
            _json_doc = cherrypy.request.body.read()
        else:
            raise cherrypy.HTTPError(400, 'Missing Client registration body')

        if _json_doc == b'':
            raise cherrypy.HTTPError(400, 'Missing Client registration body')

        _args = json.loads(as_unicode(_json_doc))
        _mds = MetadataStatement(**_args)

        try:
            _mds.verify()
        except (MessageException, VerificationError) as err:
            raise cherrypy.CherryPyException(str(err))
        else:
            _sign = self.signer[signer]
            _jwt = _sign.create_signed_metadata_statement(_mds)
            cherrypy.response.headers['Content-Type'] = 'application/jwt'
            return as_bytes(_jwt)


class FoKeys(object):
    def __init__(self, bundle):
        self.bundle = bundle

    @cherrypy.expose
    def index(self, iss=''):
        cherrypy.response.headers['Content-Type'] = 'application/jwt'
        if iss:
            if isinstance(iss, list):
                return as_bytes(self.bundle.create_signed_bundle(iss_list=iss))
            else:
                return as_bytes(
                    self.bundle.create_signed_bundle(iss_list=[iss]))
        else:
            return as_bytes(self.bundle.create_signed_bundle())

    @cherrypy.expose
    def sigkey(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return as_bytes(json.dumps(self.bundle.sign_keys.export_jwks()))

    @cherrypy.expose
    def signer(self):
        return as_bytes(self.bundle.iss)


def named_kc(config, iss):
    _kc = config.KEYDEFS[:]
    for kd in _kc:
        if 'key' in kd:
            kd['key'] = iss
    return _kc
