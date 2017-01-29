import cherrypy
import logging
from cherrypy import url

from future.backports.urllib.parse import urlparse

from jwkest import as_bytes
from jwkest import as_unicode

from otest.events import Events
from otest.events import EV_REQUEST
from otest.events import Operation

logger = logging.getLogger(__name__)


def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        "<html><body>Sorry, an error occured</body></html>"
    ]


def conv_response(resp):
    _stat = int(resp._status.split(' ')[0])
    #  if self.mako_lookup and self.mako_template:
    #    argv["message"] = message
    #    mte = self.mako_lookup.get_template(self.mako_template)
    #    return [mte.render(**argv)]
    if _stat < 300:
        for key, val in resp.headers:
            cherrypy.response.headers[key] = val
        return as_bytes(resp.message)
    elif 300 <= _stat < 400:
        raise cherrypy.HTTPRedirect(resp.message)
    else:
        raise cherrypy.HTTPError(_stat, resp.message)


def store_request(op, where):
    _ev = Operation(where, path=url)

    try:
        op.events.store(EV_REQUEST, _ev)
    except Exception as err:
        raise


class WebFinger(object):
    def __init__(self, srv):
        self.srv = srv

    @cherrypy.expose
    def index(self, resource, rel):
        if rel != 'http://openid.net/specs/connect/1.0/issuer':
            raise cherrypy.NotFound()

        p = urlparse(resource)
        if p[0] == 'acct':
            loc, dom = p[2].split('@')  # Should I check dom ?
            ids = loc.split('.')
            if len(ids) != 2:
                raise cherrypy.HTTPError(
                    400, "local part must consist of <rp_id>.<test_id>")

            _path = '/'.join(ids)
        elif p[0] in ['http', 'https']:
            _path = p[2][1:]  # skip leading '/'
        else:
            raise cherrypy.HTTPError(400,
                                     'unknown scheme in webfinger resource')

        cnf = cherrypy.request.config
        subj = resource
        _base = cnf['base_url']
        if _base.endswith('/'):
            href = '{}{}'.format(_base, _path)
        else:
            href = '{}/{}'.format(_base, _path)

        return self.srv.response(subj, href)


class Configuration(object):
    @cherrypy.expose
    def index(self, op):
        store_request(op, 'ProviderInfo')
        resp = op.providerinfo_endpoint()
        # cherrypy.response.headers['Content-Type'] = 'application/json'
        # return as_bytes(resp.message)
        return conv_response(resp)


class Registration(object):
    @cherrypy.expose
    def index(self, op):
        store_request(op, 'ClientRegistration')
        if cherrypy.request.process_request_body is True:
            _request = cherrypy.request.body.read()
        else:
            raise cherrypy.HTTPError(400, 'Missing Client registration body')
        resp = op.registration_endpoint(as_unicode(_request))
        # cherrypy.response.status = 201
        # cherrypy.response.headers['Content-Type'] = 'application/json'
        return conv_response(resp)


class Authorization(object):
    @cherrypy.expose
    def index(self, op, **kwargs):
        store_request(op, 'AuthorizationRequest')
        resp = op.authorization_endpoint(kwargs)
        return conv_response(resp)


class Token(object):
    _cp_config = {"request.methods_with_bodies": ("POST", "PUT")}

    @cherrypy.expose
    def index(self, op, **kwargs):
        store_request(op, 'AccessTokenRequest')
        try:
            authn = cherrypy.request.headers['Authorization']
        except KeyError:
            authn = None
        resp = op.token_endpoint(as_unicode(kwargs), authn, 'dict')
        return conv_response(resp)


class UserInfo(object):
    @cherrypy.expose
    def index(self, op, **kwargs):
        store_request(op, 'UserinfoRequest')
        resp = op.userinfo_endpoint(kwargs)
        return conv_response(resp)


class Provider(object):
    _cp_config = {'request.error_response': handle_error}

    def __init__(self, op_handler, flows):
        self.op_handler = op_handler
        self.flows = flows
        self.configuration = Configuration()
        self.registration = Registration()
        self.authorization = Authorization()
        self.token = Token()
        self.userinfo = UserInfo()

    @cherrypy.expose
    def index(self, **kwargs):
        return "<html><body>Welcome to the JRA3T3 fed RP lib " \
               "tester</body></html>"

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip

        if vpath[0] == 'static':
            return self

        if len(vpath) >= 2:
            oper_id = vpath.pop(0)
            test_id = vpath.pop(0)

            # verify test_id
            try:
                self.flows[test_id]
            except KeyError:
                raise cherrypy.HTTPError(400, 'Unknown TestID')

            if len(vpath):

                if len(vpath) == 1:
                    endpoint = vpath.pop(0)
                    op = self.op_handler.get(oper_id, test_id, Events(),
                                             endpoint)[0]
                    cherrypy.request.params['op'] = op
                    if endpoint == 'registration':
                        return self.registration
                    elif endpoint == 'authorization':
                        return self.authorization
                    elif endpoint == 'token':
                        return self.token
                    elif endpoint == 'userinfo':
                        return self.userinfo
                    else:  # Shouldn't be any other
                        raise cherrypy.NotFound()
                if len(vpath) == 2:
                    a = vpath.pop(0)
                    b = vpath.pop(0)
                    endpoint = '{}/{}'.format(a,b)
                    op = self.op_handler.get(oper_id, test_id, Events(),
                                             endpoint)[0]
                    cherrypy.request.params['op'] = op
                    return self.configuration

        return self
