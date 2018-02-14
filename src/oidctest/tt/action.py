import logging
import os
from urllib.parse import unquote_plus
from html import escape

import cherrypy
from jwkest import as_bytes
from oic.oauth2.message import list_serializer
from oic.utils.http_util import Response
from otest.prof_util import abbr_return_type
from otest.prof_util import do_discovery
from otest.prof_util import do_registration
from otest.prof_util import from_profile
from otest.prof_util import return_type
from otest.prof_util import to_profile
from otest.proc import kill_process
from otest.proc import isrunning

from oidctest.app_conf import TYPE2CLS
from oidctest.app_conf import create_model
from oidctest.cp import init_events
from oidctest.tt import conv_response
from oidctest.tt import unquote_quote

logger = logging.getLogger(__name__)

HEADLINE = {
    'tool': "Test tool configuration",
    "registration_response": "",
    "provider_info": ""
}

ball = '<button type="button" class="btn btn-warning"><span class="glyphicon ' \
       'glyphicon-plus"></span></button>'

_cline = '{} <input type="radio" name="{}:{}" value="{}" {}>'

_info = '<button type="button" class="btn btn-info" data-toggle="tooltip" title="{}"><span class="glyphicon ' \
       'glyphicon-info-sign"></span></button>'

TOOLTIPS = {
    'tool:return_type': {
        'type' :"space separated string",
        'desc' : "The response type that the test suite will use in the authentication request.",
        'example': "code id_token"
    },
    'tool:claims_locales': {
        'type' :"space separated list",
        'desc' : "End-User's preferred languages and scripts for Claims being returned, represented as a space-separated list of BCP47 [RFC5646] language tag values, ordered by preference.",
        'example': "fr-CA fr en"
    },
    'tool:contact_email': {
        'type' :"string",
        'desc' : "E-mail address on which the tester can be contacted.",
        'example': "director@oidf.org"
    },
    'tool:enc': {
        'type' :"JSON boolean",
        'desc' : "Enable tests that check support for encryption.",
        'example': "true"
    },
    'tool:extra': {
        'type' :"JSON boolean",
        'desc' : "Enable tests that are extra, not required for certification.",
        'example': "true"
    },
    'tool:form_post': {
        'type' :"JSON boolean",
        'desc' : "Enable tests that check support for the form_post response mode.",
        'example': "true"
    },
    'tool:insecure': {
        'type' :"JSON boolean",
        'desc' : "Enable support for OPs that don't run on https",
        'example': "true"
    },
    'tool:login_hint': {
        'type' :"string",
        'desc' : "Hint to the Authorization Server about the login identifier the End-User might use to log in (if necessary). ",
        'example': "john@example.org"
    },
    'tool:none': {
        'type' :"JSON boolean",
        'desc' : "Enable tests that check support for the \"none\" signature algorithm in the id_token.",
        'example': "true"
    },
    'tool:sig': {
        'type' :"JSON boolean",
        'desc' : "Enable tests that check support for signatures (other than in id_token) such as private key authentication, key rotation, signed userinfo responses, request URIs etc.",
        'example': "true"
    },
    'tool:webfinger_email': {
        'type' :"string",
        'desc' : "The e-mail address that the test suite will use in the webfinger request when performing OP discovery",
        'example': "john@example.org"
    },
    'tool:webfinger_url': {
        'type' :"string",
        'desc' : "The URL that the test suite will use in the webfinger request when performing OP discovery",
        'example': "https://example.com/joe"
    },
    'tool:acr_values': {
        'type' : "Space-separated string",
        'desc' : "Requested Authentication Context Class Reference values. Space-separated string that specifies the acr values that the Authorization Server is being requested to use for processing this Authentication Request, with the values appearing in order of preference.",
        'example' : "1 2"
    },
    'tool:ui_locales': {
        'type' : "Space-separated list",
        'desc' : "End-User's preferred languages and scripts for the user interface, represented as a space-separated list of BCP47 [RFC5646] language tag values, ordered by preference.",
        'example' : "fr-CA fr en"
    },
    'registration_response:redirect_uris': {
        'type' :"string",
        'desc' : "Redirection URI value used by the test suite.",
        'example': ""
    },
    'registration_response:client_id': {
        'type' :"string",
        'desc' : " Unique Client Identifier used by the test suite as registered at the OP",
        'example': "myclient"
    },
    'registration_response:client_secret': {
        'type' :"string",
        'desc' : "Client Secret used by the test suite as registered at the OP",
        'example': "mysecret"
    },
    'registration_response:application_type': {
        'type' :"string",
        'desc' : "Kind of the application. The default, if omitted, is web. The defined values are native or web.",
        'example': "web"
    },
    'registration_response:client_id_issued_at': {
        'type' :"JSON number",
        'desc' : " Time at which the Client Identifier was issued. Its value is a JSON number representing the number of seconds from 1970-01-01T0:0:0Z as measured in UTC until the date/time",
        'example': "1518533447"
    },
    'registration_response:client_name': {
        'type' :"string",
        'desc' : "Name of the Client to be presented to the End-User.",
        'example': "My Client"
    },
    'registration_response:client_secret_expires_at': {
        'type' :"JSON number",
        'desc' : "Time at which the client_secret will expire or 0 if it will not expire. Its value is a JSON number representing the number of seconds from 1970-01-01T0:0:0Z as measured in UTC until the date/time.",
        'example': "1518533447"
    },
    'registration_response:client_uri': {
        'type' :"string",
        'desc' : "URL of the home page of the Client. The value of this field MUST point to a valid Web page.",
        'example': "https://example.org/client"
    },
    'registration_response:contacts': {
        'type' :"JSON array or comma-separated list of strings",
        'desc' : "Array of e-mail addresses of people responsible for this Client.",
        'example': "director@oidf.org"
    },
    'registration_response:default_acr_values': {
        'type' :"JSON array or comma-separated list of strings",
        'desc' : "Default requested Authentication Context Class Reference values. Array of strings that specifies the default acr values that the OP is being requested to use for processing requests from this Client, with the values appearing in order of preference.",
        'example': "1, 2"
    },
    'registration_response:default_max_age': {
        'type' :"JSON number",
        'desc' : "Default Maximum Authentication Age. Specifies that the End-User MUST be actively authenticated if the End-User was authenticated longer ago than the specified number of seconds. ",
        'example': "1800"
    },
    'registration_response:grant_types': {
        'type' :"JSON array or comma-separated list of strings",
        'desc' : " JSON array containing a list of the OAuth 2.0 Grant Types that the Client is declaring that it will restrict itself to using.",
        'example': "authorization_code, implicit, refresh_token"
    },
    'registration_response:id_token_encrypted_response_alg': {
        'type' :"string",
        'desc' : "JWE alg algorithm [JWA] REQUIRED for encrypting the ID Token issued to this Client",
        'example': "RSA1_5"
    },
    'registration_response:id_token_encrypted_response_enc': {
        'type' :"string",
        'desc' : "JWE enc algorithm [JWA] REQUIRED for encrypting the ID Token issued to this Client.",
        'example': "A128CBC-HS256"
    },
    'registration_response:id_token_signed_response_alg': {
        'type' :"string",
        'desc' : "JWS alg algorithm [JWA] REQUIRED for signing the ID Token issued to this Client.",
        'example': "RS256"
    },
    'registration_response:initiate_login_uri': {
        'type' :"string",
        'desc' : "URI using the https scheme that a third party can use to initiate a login by the RP",
        'example': "https://example.org/login"
    },
    'registration_response:jwks': {
        'type' :"JSON object",
        'desc' : "Client's JSON Web Key Set [JWK] document, passed by value. ",
        'example': '{ "keys": [ {"kty":"RSA", "n": "blabla", "e": "AQAB", "kid", "1", "alg": "RS256" } ] }'
    },
    'registration_response:jwks_uri': {
        'type' :"string",
        'desc' : "URL for the Client's JSON Web Key Set [JWK] document.",
        'example': "https://example.org/jwks"
    },
    'registration_response:logo_uri': {
        'type' :"string",
        'desc' : "URL that references a logo for the Client application. If present, the server SHOULD display this image to the End-User during approval. ",
        'example': "https://example.org/logo.png"
    },
    'registration_response:policy_uri': {
        'type' :"string",
        'desc' : "URL that the Relying Party Client provides to the End-User to read about the how the profile data will be used.",
        'example': "https://example.org/policy.html"
    },
    'registration_response:post_logout_redirect_uris': {
        'type' :"JSON array or comma-separated list of strings",
        'desc' : " Array of URLs supplied by the RP to which it MAY request that the End-User's User Agent be redirected using the post_logout_redirect_uri parameter after a logout has been performed.",
        'example': "https://example.org/loggedout.html"
    },
    'registration_response:registration_access_token': {
        'type' :"string",
        'desc' : "Registration Access Token that can be used at the Client Configuration Endpoint to perform subsequent operations upon the Client registration.",
        'example': "QERQADFDAS"
    },
    'registration_response:registration_client_uri': {
        'type' :"string",
        'desc' : "Location of the Client Configuration Endpoint where the Registration Access Token can be used to perform subsequent operations upon the resulting Client registration. ",
        'example': "https://op.example.org/oidc/client/manage"
    },
    'registration_response:request_object_encryption_alg': {
        'type' :"string",
        'desc' : " JWE [JWE] alg algorithm [JWA] the RP is declaring that it may use for encrypting Request Objects sent to the OP.",
        'example': "RSA1_5"
    },
    'registration_response:request_object_encryption_enc': {
        'type' :"string",
        'desc' : "JWE enc algorithm [JWA] the RP is declaring that it may use for encrypting Request Objects sent to the OP.",
        'example': "A128CBC-HS256"
    },
    'registration_response:request_object_signing_alg': {
        'type' :"string",
        'desc' : " JWS [JWS] alg algorithm [JWA] that MUST be used for signing Request Objects sent to the OP.",
        'example': "RS256"
    },
    'registration_response:request_uris': {
        'type' :"JSON array or comma-separated list of strings",
        'desc' : "Array of request_uri values that are pre-registered by the RP for use at the OP. Servers MAY cache the contents of the files referenced by these URIs and not retrieve them at the time they are used in a request. ",
        'example': "https://example.org/request_uri"
    },
    'registration_response:require_auth_time': {
        'type' :"JSON boolean",
        'desc' : "Boolean value specifying whether the auth_time Claim in the ID Token is REQUIRED.",
        'example': "true"
    },
    'registration_response:response_types': {
        'type' :"JSON array or comma-separated list of strings",
        'desc' : 'JSON array containing a list of the OAuth 2.0 response_type values that the Client is declaring that it will restrict itself to using. If omitted, the default is that the Client will use only the code Response Type',
        'example': 'code, code id_token'
    },
    'registration_response:sector_identifier_uri': {
        'type' :"string",
        'desc' : "URL using the https scheme to be used in calculating Pseudonymous Identifiers by the OP. The URL references a file with a single JSON array of redirect_uri values.",
        'example': "https://other.example.net/file_of_redirect_uris.json"
    },
    'registration_response:subject_type': {
        'type' :"string",
        'desc' : "subject_type requested for responses to this Client. Valid types include pairwise and public.",
        'example': "pairwise"
    },
    'registration_response:token_endpoint_auth_method': {
        'type' :"string",
        'desc' : "Requested Client Authentication method for the Token Endpoint. The options are client_secret_post, client_secret_basic, client_secret_jwt, private_key_jwt, and none.",
        'example': "client_secret_post"
    },
    'registration_response:token_endpoint_auth_signing_alg': {
        'type' :"string",
        'desc' : ". JWS [JWS] alg algorithm [JWA] that MUST be used for signing the JWT [JWT] used to authenticate the Client at the Token Endpoint for the private_key_jwt and client_secret_jwt authentication methods. ",
        'example': "RS256"
    },
    'registration_response:tos_uri': {
        'type' :"string",
        'desc' : "URL that the Relying Party Client provides to the End-User to read about the Relying Party's terms of service. ",
        'example': "https://example.org/tos"
    },
    'registration_response:userinfo_encrypted_response_alg': {
        'type' :"string",
        'desc' : " JWE [JWE] alg algorithm [JWA] REQUIRED for encrypting UserInfo Responses.",
        'example': "RSA1_5"
    },
    'registration_response:userinfo_encrypted_response_enc': {
        'type' :"string",
        'desc' : " JWE enc algorithm [JWA] REQUIRED for encrypting UserInfo Responses.",
        'example': "A128CBC-HS256"
    },
    'registration_response:userinfo_signed_response_alg': {
        'type' :"string",
        'desc' : " JWS alg algorithm [JWA] REQUIRED for signing UserInfo Responses. If this is specified, the response will be JWT [JWT] serialized, and signed using JWS. The default, if omitted, is for the UserInfo Response to return the Claims as a UTF-8 encoded JSON object using the application/json content-type.",
        'example': "RS256"
    }
}

def get_tooltip_button(key):
    text = ""
    if key in TOOLTIPS:
        tip = TOOLTIPS[key];
        text = "[{}] {} Example: {}".format(tip['type'], tip['desc'], tip['example'])
        text = _info.format(escape(text))
    return text

def do_line(grp, key, val, req=False):
    if req:
        _ball = ball
    else:
        _ball = ''

    if val is False or val is True:
        if val is True:
            _choice = " ".join(
                [_cline.format('True', grp, key, 'True', 'checked'),
                 _cline.format('False', grp, key, 'False', '')])
        else:
            _choice = " ".join(
                [_cline.format('True', grp, key, 'True', ''),
                 _cline.format('False', grp, key, 'False', 'checked')])

        return '<tr><th width="35%">{}</th><td>{}</td><td width="10%">{}</td><td width="10%">{}</td></tr>'.format(
            key, _choice, _ball, get_tooltip_button('{}:{}'.format(grp, key)))
    else:
        return " ".join([
            '<tr><th width="35%">{}</th><td><input'.format(key),
            'type="text" name="{}:{}"'.format(grp, key),
            'value="{}" class="form-control"></td><td width="10%">{}</td><td width="10%">{}</td></tr>'.format(
                val, _ball, get_tooltip_button('{}:{}'.format(grp, key)))])


def comma_sep_list(key, val, multi):
    if key in multi:
        if isinstance(val, list):
            return ', '.join(val)
    return val


def display_form(head_line, grp, dic, state, multi):
    lines = ['<table class="table table-hover table-bordered">']
    if head_line:
        lines.append(
            '<thead><tr><th colspan="3" class="text-center info"><h3>{}</h3></th></tr></thead>'.format(
                head_line))
    lines.append('<tbody>')
    keys = list(dic.keys())
    keys.sort()
    if grp in state:
        for param in state[grp]['immutable']:
            val = comma_sep_list(param, dic[param], multi[grp])
            l = [
                '<tr><th>{}</th>'.format(param),
                '<td>{}</td><td>{}</td></tr>'.format(val, ball),
                '<input type="hidden" name="{}:{}" value="{}"'.format(grp,
                                                                      param,
                                                                      val)
            ]
            lines.append(''.join(l))
            keys.remove(param)
        for param in state[grp]['required']:
            try:
                _val = dic[param]
            except KeyError:
                lines.append(
                      do_line(grp, param, '**MISSING REQUIRED VALUE**', True))
            else:
                val = comma_sep_list(param, _val, multi[grp])
                lines.append(do_line(grp, param, val, True))
                keys.remove(param)
    for key in keys:
        val = comma_sep_list(key, dic[key], multi[grp])
        lines.append(do_line(grp, key, val, False))
    lines.append('</tbody></table>')
    return lines


def display(dicts, state, multi, notes, action):
    lines = [
        '<form class="col-md-10" action="{}" method="post">'.format(action)]
    for grp, info in dicts.items():
        lines.append('<br>')
        lines.extend(display_form(HEADLINE[grp], grp, info, state, multi))
    lines.append('<p>{}</p>'.format(notes))
    lines.append(
        '<div class="btn-toolbar">'
        '<button type="submit" value="configure" class="btn btn-primary">Save '
        '& Start</button>')
    lines.append(
        '<button type="submit" value="abort" class="btn '
        'btn-default">Abort</button>'
        '</div>')
    lines.append('</form>')
    return "\n".join(lines)


def update(typ, conf):
    cls = TYPE2CLS[typ]
    for param in cls.c_param:
        if param not in conf:
            conf[param] = ''
    return conf


def multi_value(typ):
    cls = TYPE2CLS[typ]
    res = []
    for param, spec in cls.c_param.items():
        if spec[2] == list_serializer:
            res.append(param)
    return res


def update_config(conf, tool_params):
    # provider_info and registration_response
    dicts = {'tool': conf['tool']}
    _prof = conf['tool']['profile']
    _spec = from_profile(conf['tool']['profile'])
    _spec['return_type'] = abbr_return_type(_spec['return_type'])
    del dicts['tool']['profile']
    dicts['tool'].update(_spec)

    for item in tool_params:
        if item == 'profile':
            continue
        if item not in dicts['tool']:
            dicts['tool'][item] = ''

    multi = {'tool': ['acr_values', 'claims_locales', 'ui_locales']}
    for typ in ['provider_info', 'registration_response']:
        multi[typ] = multi_value(typ)
        try:
            dicts[typ] = conf['client'][typ]
        except KeyError:
            try:
                dicts[typ] = update(typ, conf[typ])
            except KeyError:
                pass

    state = {
        'tool': {'immutable': ['issuer', 'tag', 'register', 'discover',
                               'webfinger'],
                 'required': ['return_type', 'contact_email']}}

    notes = ''
    if _spec['webfinger']:
        state['tool']['required'].extend(['webfinger_email',
                                          'webfinger_url'])
        notes = ("If <i>webfinger</i> is True then one of "
                 "<i>webfinger_email</i> and <i>webfinger_url</i> "
                 "<b>MUST</b> have a value.")

    if 'registration_response' in dicts:
        state['registration_response'] = {
            'immutable': ['redirect_uris'],
            'required': ['client_id', 'client_secret']}

    if 'provider_info' in dicts:
        _req = ['authorization_endpoint', 'jwks_uri',
                'response_types_supported', 'subject_types_supported',
                'id_token_signing_alg_values_supported']

        state['provider_info'] = {'immutable': ['issuer']}

        if return_type(_prof) not in ['I', 'IT']:
            _req.append('token_endpoint')

        state['provider_info']['required'] = _req

    return dicts, state, multi, notes


class Action(object):
    def __init__(self, rest, tool_conf, html, entpath, ent_info_path,
                 tool_params, app, version):
        self.rest = rest
        self.tool_conf = tool_conf
        self.html = html
        self.entpath = entpath
        self.ent_info_path = ent_info_path
        self.baseurl = ''
        self.app = app
        self.tool_params = tool_params
        self.version = version

    @cherrypy.expose
    def index(self, iss, tag, ev, action):
        if action == 'restart':
            return self.restart(iss, tag, ev)
        elif action == 'delete':
            return self.delete(iss, tag, ev)
        elif action == 'configure':
            return self.update(iss, tag, ev)
        elif action == 'stop':
            return self.stop(iss, tag, ev)

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))

        if len(vpath):
            if len(vpath) == 2:
                cherrypy.request.params['iss'] = unquote_plus(vpath.pop(0))
                cherrypy.request.params['tag'] = unquote_plus(vpath.pop(0))
            cherrypy.request.params['ev'] = init_events(
                cherrypy.request.path_info)

            return self

    @cherrypy.expose
    def update(self, iss, tag, ev=None, **kwargs):
        """
        Displays interface for updating configuration
        
        :param iss: Issuer ID 
        :param tag: tag
        :param ev: Event instance
        :param kwargs: keyword arguments
        :return: 
        """
        logger.debug('update test tool configuration: {} {}'.format(iss, tag))
        uqp, qp = unquote_quote(iss, tag)

        try:
            _format, _conf = self.rest.read_conf(qp[0], qp[1])
        except TypeError:
            _msg = "No such test tool configuration"
            logger.info(_msg)
        else:
            logger.info('config: {}'.format(_conf))

            dicts, state, multi, notes = update_config(_conf, self.tool_params)

            action = "{}/run/{}/{}".format('', qp[0], qp[1])
            _msg = self.html['instance.html'].format(
                display=display(dicts, state, multi, notes, action),
                version=self.version
            )

        return as_bytes(_msg)

    def kill(self, iss, tag, ev):
        uqp, qp = unquote_quote(iss, tag)
        _key = self.app.assigned_ports.make_key(*uqp)
        
        try:
            pid = isrunning(unquote_plus(iss), unquote_plus(tag))
        except KeyError:
            pass
        else:
            if pid:
                # logger.info('kill {}'.format(pid))
                # subprocess.call(['kill', str(pid)])
                kill_process(pid)
                try:
                    del self.app.running_processes[_key]
                except KeyError:
                    pass
        
    @cherrypy.expose
    def stop(self, iss, tag, ev):
        logger.info('stop test tool: {} {}'.format(iss, tag))

        # If already running - kill
        self.kill(iss, tag, ev)
        
        uqp, qp = unquote_quote(iss, tag)

        # redirect back to entity page
        loc = '{}entity/{}'.format(self.rest.base_url, qp[0])
        raise cherrypy.HTTPRedirect(loc)

    @cherrypy.expose
    def delete(self, iss, tag, ev, pid=0):
        logger.info('delete test tool configuration: {} {}'.format(iss, tag))
        
        # If already running - kill
        self.kill(iss, tag, ev)
        
        uqp, qp = unquote_quote(iss, tag)
        _key = self.app.assigned_ports.make_key(*uqp)

        os.unlink(os.path.join(self.entpath, *qp))
        # Remove issuer if out of tags
        if not os.listdir(os.path.join(self.entpath, qp[0])):
            os.rmdir(os.path.join(self.entpath, qp[0]))

        try:
            del self.app.assigned_ports[_key]
        except KeyError:  # How could it already have gone ? Ah, well
            pass

        # redirect back to entity page
        loc = '{}entity'.format(self.rest.base_url)
        raise cherrypy.HTTPRedirect(loc)

    @cherrypy.expose
    def restart(self, iss, tag, ev):
        """
        Restart a test instance
        
        :param iss: 
        :param tag: 
        :param ev: 
        :return: 
        """
        logger.info('restart test tool: {} {}'.format(iss, tag))
        uqp, qp = unquote_quote(iss, tag)
        url = self.app.run_test_instance(*qp)

        if isinstance(url, Response):
            return conv_response(None, url)

        if url:
            # redirect back to entity page
            loc = '{}entity/{}'.format(self.rest.base_url, qp[0])
            raise cherrypy.HTTPRedirect(loc)
        else:
            args = {
                'title': "Action Failed", 'base': self.baseurl,
                'note': 'Could not restart your test instance'}

        _msg = self.html['message.html'].format(**args)
        return as_bytes(_msg)

    @cherrypy.expose
    def create(self, **kwargs):
        logger.info(
            'create test tool configuration: {} {}'.format(kwargs['iss'],
                                                           kwargs['tag']))
        
        uqp, qp = unquote_quote(kwargs['iss'], kwargs['tag'])
        if not uqp[0].startswith('https://') and not uqp[0].startswith('http://'):
            err = 'issuer value must start with "https://" or "http://"'
            logger.error(err)
            return as_bytes('Sorry failed to create: {}'.format(err))
        
        # construct profile
        try:
            profile = to_profile(kwargs)
        except KeyError as err:
            logger.error(err)
            return as_bytes('Sorry failed to create: {}'.format(err))

        _ent_conf = create_model(profile, ent_info_path=self.ent_info_path)

        if not do_discovery(profile):
            _ent_conf['client']['provider_info']['issuer'] = kwargs['iss']

        if not do_registration(profile):
            # need to create a redirect_uri, means I need to register a port
            _port = self.app.assigned_ports.register_port(kwargs['iss'],
                                                          kwargs['tag'])
            if self.app.test_tool_base.endswith('/'):
                _base = self.app.test_tool_base[:-1]
            else:
                _base = self.app.test_tool_base
            _ent_conf['client']['registration_response'][
                'redirect_uris'] = '{}:{}/authz_cb'.format(_base, _port)

        _ent_conf['tool']['issuer'] = uqp[0]
        _ent_conf['tool']['tag'] = uqp[1]
        _ent_conf['tool']['profile'] = profile

        _ent_conf.update(from_profile(profile))
        logger.info("Test tool config: {}".format(_ent_conf))

        self.rest.write(qp[0], qp[1], _ent_conf)
        # Do a redirect
        raise cherrypy.HTTPRedirect(
            '/action/update?iss={}&tag={}'.format(qp[0], qp[1]))
