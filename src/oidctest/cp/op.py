import cherrypy
import logging
from cherrypy import url

from future.backports.urllib.parse import urlparse

from jwkest import as_bytes
from jwkest import as_unicode
from oic.oauth2 import Message

from otest.events import Events
from otest.events import EV_FAULT
from otest.events import EV_REQUEST
from otest.events import EV_RESPONSE
from otest.events import FailedOperation
from otest.events import Operation
from otest.flow import ABBR

from oidctest.cp import write_events
from oidctest.cp import init_events

logger = logging.getLogger(__name__)


def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        "<html><body>Sorry, an error occured</body></html>"
    ]


def conv_response(op, resp):
    _stat = int(resp._status.split(' ')[0])
    #  if self.mako_lookup and self.mako_template:
    #    argv["message"] = message
    #    mte = self.mako_lookup.get_template(self.mako_template)
    #    return [mte.render(**argv)]
    if _stat < 300:
        op.events.store(EV_RESPONSE, resp.message)
        for key, val in resp.headers:
            cherrypy.response.headers[key] = val
        return as_bytes(resp.message)
    elif 300 <= _stat < 400:
        op.events.store('Redirect', resp.message)
        raise cherrypy.HTTPRedirect(resp.message)
    else:
        op.events.store(EV_FAULT, resp.message)
        raise cherrypy.HTTPError(_stat, resp.message)


def store_request(op, where):
    _ev = Operation(where, path=url())

    try:
        op.events.store(EV_REQUEST, _ev)
    except Exception as err:
        raise


def parse_resource(resource):
    p = urlparse(resource)
    if p[0] == 'acct':
        loc, dom = p[2].split('@')  # Should I check the domain part ?
        return loc.split('.')
    elif p[0] in ['http', 'https']:
        return p[2][1:].split('/')  # skip leading '/'
    else:
        return None


class WebFinger(object):
    def __init__(self, srv):
        self.srv = srv

    @cherrypy.expose
    def index(self, resource, rel):
        ev = init_events('/.well-known/webfinger')
        ev.store(EV_REQUEST, Operation('WebFinger', resource=resource, rel=rel))

        if rel != 'http://openid.net/specs/connect/1.0/issuer':
            ev.store(EV_FAULT,
                     FailedOperation('Webfinger', error='unknown rel',rel=rel))
            try:
                op_id, test_id = parse_resource(resource)
            except (ValueError, TypeError):
                logger.error('webfinger resource specification faulty')
                raise cherrypy.HTTPError(
                    400, 'webfinger resource specification faulty')
            else:
                write_events(ev, op_id, test_id)
            raise cherrypy.NotFound()

        try:
            op_id, test_id = parse_resource(resource)
        except (ValueError, TypeError):
            logger.error('webfinger resource specification faulty')
            raise cherrypy.HTTPError(
                400, 'webfinger resource specification faulty')
        else:
            _path = '/'.join([op_id, test_id])

        cnf = cherrypy.request.config
        subj = resource
        _base = cnf['base_url']

        # introducing an error
        if 'rp-discovery-webfinger-http-href' in resource:
            _base = _base.replace('https', 'http')

        if _base.endswith('/'):
            href = '{}{}'.format(_base, _path)
        else:
            href = '{}/{}'.format(_base, _path)

        ev.store(EV_RESPONSE, Operation('Webfinger', href=href, subj=resource))
        write_events(ev, op_id, test_id)
        return self.srv.response(subj, href)


class Configuration(object):
    @cherrypy.expose
    def index(self, op):
        store_request(op, 'ProviderInfo')
        resp = op.providerinfo_endpoint()
        # cherrypy.response.headers['Content-Type'] = 'application/json'
        # return as_bytes(resp.message)
        return conv_response(op, resp)


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
        return conv_response(op, resp)


class Authorization(object):
    @cherrypy.expose
    def index(self, op, **kwargs):
        store_request(op, 'AuthorizationRequest')
        resp = op.authorization_endpoint(kwargs)
        return conv_response(op, resp)


class Token(object):
    _cp_config = {"request.methods_with_bodies": ("POST", "PUT")}

    @cherrypy.expose
    def index(self, op, **kwargs):
        store_request(op, 'AccessTokenRequest')
        try:
            authn = cherrypy.request.headers['Authorization']
        except KeyError:
            authn = None
        logger.debug('Authorization: {}'.format(authn))
        resp = op.token_endpoint(as_unicode(kwargs), authn, 'dict')
        return conv_response(op, resp)


class UserInfo(object):
    @cherrypy.expose
    def index(self, op, **kwargs):
        store_request(op, 'UserinfoRequest')
        if cherrypy.request.process_request_body is True:
            args = {'request': cherrypy.request.body.read()}
        else:
            args = {}
        try:
            args['authn'] = cherrypy.request.headers['Authorization']
        except KeyError:
            pass

        kwargs.update(args)
        resp = op.userinfo_endpoint(**kwargs)
        return conv_response(op, resp)


class Claims(object):
    @cherrypy.expose
    def index(self, op, **kwargs):
        try:
            authz = cherrypy.request.headers['Authorization']
        except KeyError:
            authz = None
        try:
            assert authz.startswith("Bearer")
        except AssertionError:
            op.events.store(EV_FAULT, "Bad authorization token")
            cherrypy.HTTPError(400, "Bad authorization token")

        tok = authz[7:]
        try:
            _claims = op.claim_access_token[tok]
        except KeyError:
            op.events.store(EV_FAULT, "Bad authorization token")
            cherrypy.HTTPError(400, "Bad authorization token")
        else:
            # one time token
            del op.claim_access_token[tok]
            _info = Message(**_claims)
            jwt_key = op.keyjar.get_signing_key()
            op.events.store(EV_RESPONSE, _info.to_dict())
            cherrypy.response.headers["content-type"] = 'application/jwt'
            return as_bytes(_info.to_jwt(key=jwt_key, algorithm="RS256"))


PRE_HTML = """<html>
  <head>
    <title>The OIDC RP library test documentation</title>
    <link rel="stylesheet" type="text/css" href="/static/theme.css">
  </head>
  <body>"""

POST = """</body></html>"""


def choice(profiles):
    keys = list(profiles.keys())
    keys.sort()

    line = [
        '<table>',
        '<tr><th>Response type</th><th></th></tr>']
    for k in keys:
        line.append('<tr><td>{}</td><td>'.format(k))
        line.append('<input type="radio" name="profile" value="{}">'.format(
            profiles[k]))
        line.append('</td></tr>')
    line.append('</table>')
    return '\n'.join(line)


class Root(object):
    @cherrypy.expose
    def index(self):
        response = [
            PRE_HTML,
            "<h1>Welcome to the OpenID Foundation RP library test site</h1>",
            '<h3>Before you start testing please read the ',
            '<a href="http://openid.net/certification/rp_testing/" '
            'target="_blank">',
            'how to use the RPtest </a>introduction guide</h3>',
            '<h3>For a list of OIDC RP library tests per response_type chose '
            'your preference:</h3>',
            '<form action="list">',
            choice(ABBR),
            '<p></p><input type="submit" value="Submit"></form>',
            POST
        ]
        return '\n'.join(response)


class Provider(Root):
    _cp_config = {'request.error_response': handle_error}

    def __init__(self, op_handler, flows):
        self.op_handler = op_handler
        self.flows = flows
        self.configuration = Configuration()
        self.registration = Registration()
        self.authorization = Authorization()
        self.token = Token()
        self.userinfo = UserInfo()
        self.claims = Claims()

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if vpath[0] == 'static':
            return self

        if len(vpath) >= 2:
            ev = init_events(cherrypy.request.path_info)
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
                    op = self.op_handler.get(oper_id, test_id, ev, endpoint)[0]
                    cherrypy.request.params['op'] = op
                    if endpoint == 'registration':
                        return self.registration
                    elif endpoint == 'authorization':
                        return self.authorization
                    elif endpoint == 'token':
                        return self.token
                    elif endpoint == 'userinfo':
                        return self.userinfo
                    elif endpoint == 'claim':
                        return self.claims
                    else:  # Shouldn't be any other
                        raise cherrypy.NotFound()
                if len(vpath) == 2:
                    a = vpath.pop(0)
                    b = vpath.pop(0)
                    endpoint = '{}/{}'.format(a, b)
                    if endpoint == ".well-known/openid-configuration":
                        op = self.op_handler.get(oper_id, test_id, Events(),
                                                 endpoint)[0]
                        cherrypy.request.params['op'] = op
                        return self.configuration

        return self
