import json

import cherrypy
from fedoidc import MetadataStatement
from fedoidc.operator import Operator
from fedoidc.signing_service import ServiceError
from jwkest import as_bytes
from jwkest import as_unicode
from oic.exception import MessageException
from oic.exception import ParameterError
from oic.exception import RegistrationError
from oic.oauth2.exception import VerificationError
from oic.oauth2.message import MissingSigningKey
from oic.utils.keyio import KeyJar


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
    def index(self, signer='', context='discovery', **kwargs):
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

        try:
            _args = json.loads(as_unicode(_json_doc))
        except json.JSONDecodeError as err:
            raise cherrypy.HTTPError(
                message="JSON decode error: {}".format(str(err)))
        _mds = MetadataStatement(**_args)

        try:
            _mds.verify()
        except (MessageException, VerificationError) as err:
            raise cherrypy.HTTPError(
                message="Message verification error: {}".format(str(err)))
        else:
            _sign = self.signer[signer]
            try:
                _jwt = _sign.create_signed_metadata_statement(_mds, context)
            except (KeyError, ServiceError) as err:
                raise cherrypy.HTTPError(message=str(err))
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


class Verify(object):
    def __init__(self):
        self.foo = True

    @cherrypy.expose
    def index(self, iss, jwks, ms, **kwargs):
        _kj = KeyJar()
        _kj.import_jwks(json.loads(jwks), iss)
        op = Operator()

        try:
            _pi = op.unpack_metadata_statement(jwt_ms=ms, keyjar=_kj,
                                               cls=MetadataStatement)
            response = json.dumps(_pi.result.to_dict(), sort_keys=True,
                                  indent=2, separators=(',', ': '))
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            return as_bytes(response)
        except (RegistrationError, ParameterError, MissingSigningKey) as err:
            raise cherrypy.HTTPError(
                400, as_bytes('Invalid Metadata statement: {}'.format(err)))


def named_kc(config, iss):
    _kc = config.KEYDEFS[:]
    for kd in _kc:
        if 'key' in kd:
            kd['key'] = iss
    return _kc


class MDSUrl(object):
    def __init__(self, mds):
        self.mds = mds

    @cherrypy.expose
    def index(self, key=''):
        cherrypy.response.headers['Content-Type'] = 'application/jwt'
        if key:
            try:
                return as_bytes(self.mds[key])
            except KeyError:
                raise cherrypy.HTTPError(404, 'Could not find {}'.format(key))
        else:
            raise cherrypy.HTTPError(400, 'Bad Request')
