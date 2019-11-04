import inspect
import json
import os
import sys

import six
from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlparse
from jwkest import as_bytes
from jwkest import as_unicode
from jwkest import b64e
from jwkest.jws import factory as jws_factory
from oic import rndstr
from oic.oic import IdToken
from oic.oic import PREFERENCE2PROVIDER
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.time_util import time_sans_frac
from oidctest.op.check import get_id_tokens
from otest import ConfigurationError
from otest.check import ERROR
from otest.check import STATUSCODE_TRANSL
from otest.check import State
from otest.check import get_signed_id_tokens
from otest.events import EV_CONDITION
from otest.func import SetUpError
from otest.func import get_base
from otest.prof_util import return_type
from otest.result import get_issuer
from past.types import basestring

__author__ = 'roland'


def set_webfinger_resource(oper, args):
    """
    Context:
        WebFinger
    Action:
        Specifies the webfinger resource. If the OP supports
        webfinger queries then the resource is set to the value of 'webfinger_url'
        or 'webfinger_email' from the test instance configuration.
    Example:
        "set_webfinger_resource": null
        
    """

    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        if oper.dynamic:
            try:
                _base = oper.conv.get_tool_attribute("webfinger_url",
                                                     "webfinger_email")
            except KeyError:
                raise SetUpError(
                    'If you want to do dynamic webfinger discovery you '
                    'must define "webfinger_url" or "webfinger_email" in '
                    'the "tool" configuration')

            oper.resource = _base


def set_discovery_issuer(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Pick up issuer ID either from static configuration or dynamic discovery.
    Example:
        "set_discovery_issuer": null
    """
    if oper.dynamic:
        oper.op_args["issuer"] = get_issuer(oper.conv)


def set_response_where(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Set where the response is expected to occur dependent on which
        response_type it is or which it isn't.
    Args:
        None or one of response_type or not_response_type and where
    Example:
        "set_response_where": null

    """
    if args is None:
        args = {"not_response_type": ["code"], "where": "fragment"}

    if 'response_type' in args:
        for rt in args['response_type']:
            if oper.req_args["response_type"] == [rt]:
                oper.response_where = args["where"]
                break
    elif 'not_response_type' in args:
        for rt in args['not_response_type']:
            if oper.req_args["response_type"] != [rt]:
                oper.response_where = args["where"]
                break
    else:
        oper.response_where = args["where"]


def check_support(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Verify that the needed support is supported by the OP
    Args:
        A dictionary of dictionaries. {level: {item: value}}
    Example:
        "check_support": {
          WARNING: {"scopes_supported": ["phone"]}
        }

        "check_support": {
          ERROR: {"id_token_signing_alg_values_supported": null}
        }

    """
    # args = { level : kwargs }
    for level, kwargs in list(args.items()):
        for key, val in list(kwargs.items()):
            # type of value: boolean, int, string, list, ...
            typ = oper.conv.entity.provider_info.__class__.c_param[key][0]
            try:
                pinfo = oper.conv.entity.provider_info[key]
            except KeyError:
                pass
            else:
                missing = []
                if isinstance(val, list):
                    for v in val:
                        if isinstance(typ, list) and issubclass(typ[0], (six.string_types, basestring)):
                            if v not in pinfo:
                                missing.append(v)
                        elif issubclass(typ, (bool, int, six.string_types, basestring)):
                            if v != pinfo:
                                missing.append(v)
                else:
                    if isinstance(typ, list) and issubclass(typ[0], (six.string_types, basestring)):
                        if val not in pinfo:
                            missing = val
                    elif issubclass(typ, (bool, int, six.string_types, basestring)):
                        if val != pinfo:
                            missing = val

                if missing:
                    oper.conv.events.store(
                        EV_CONDITION,
                        State(status=STATUSCODE_TRANSL[level],
                              test_id="Check support",
                              message="No support for: {}={}".format(key,
                                                                     missing)))
                    if level == 'ERROR':
                        oper.fail = True


def set_principal(oper, args):
    """
    Context:
        WebFinger
    Action:
        Set principal using a specific parameter
    Args:
        Value "webfinger_url" or "webfinger_email"
    Example:
        "set_principal": {
            "param": "webfinger_url"
        }
    """
    try:
        _val = oper.conv.tool_config[args['param']]
    except KeyError:
        raise ConfigurationError("Missing parameter: %s" % args["param"])
    else:
        oper.req_args["principal"] = _val


def static_jwk(oper, args):
    """
    Context:
        Registration
    Action:
        Set a static JWKS, remove jwks_uri if specified.
    Example:
        "static_jwk": null
        
    """
    _client = oper.conv.entity
    del oper.req_args["jwks_uri"]
    oper.req_args["jwks"] = _client.keyjar.export_jwks("")


def set_redirect_uri(oper, args):
    """
    Context:
        Authorization
    Action:
        Set the path of the redirect_uri.
    Example:
        "set_redirect_uri": "authz_post"
    """


    _base = get_base(oper.conv.entity.base_url)
    oper.req_args["redirect_uri"] = "%s%s" % (_base, args)


def set_redirect_uris(oper, args):
    """
    Context:
        Authorization
    Action:
        Constructs a set of redirect_uris based on the base_url and a number of paths.
    Example:
        "set_redirect_uris": ["authz_post"]
    """
    _base = get_base(oper.conv.entity.base_url)
    oper.req_args["redirect_uris"] = ["%s%s" % (_base, path) for path in args]


def store_sector_redirect_uris(oper, args):
    """
    Context:
        Registration
    Action:
        Will store a number of redirectURIs in a file and add a
        "sector_identifier_uri" pointing to that file to the request arguments.
    Args:
        other_uris: list of complete URLs
        redirect_uris: Use default redirect_uris for this entity
        extra: Extra relative url paths
    Example:
        "store_sector_redirect_uris": {
          "other_uris": [
            "https://example.com/op"
          ]
        }
    """
    _base = get_base(oper.conv.entity.base_url)

    try:
        ruris = args["other_uris"]
    except KeyError:
        try:
            ruris = oper.req_args["redirect_uris"]
        except KeyError:
            ruris = oper.conv.entity.redirect_uris

        try:
            ruris.append("%s%s" % (_base, args["extra"]))
        except KeyError:
            pass

    try:
        f = open("export/siu.json", 'w')
    except FileNotFoundError:
        os.makedirs('export')
        f = open("export/siu.json", 'w')
    f.write(json.dumps(ruris))
    f.close()

    sector_identifier_url = "%s%s%s" % (_base, "export/", "siu.json")
    oper.req_args["sector_identifier_uri"] = sector_identifier_url


def id_token_hint(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Will pick up an id_token received in an earlier authorization
        request and add it as value to the request claim "id_token_hint".
    Example:
        "id_token_hint": null
    """
    res = get_signed_id_tokens(oper.conv)
    if res:
        oper.req_args["id_token_hint"] = res[0]


def login_hint(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Sets the request argument 'login_hint' to a value picked from the configuration.
    Example:
        "login_hint": null
    """
    _iss = oper.conv.entity.provider_info["issuer"]
    p = urlparse(_iss)
    _default = "buffy@%s" % p.netloc
    try:
        hint = oper.conv.get_tool_attribute("login_hint")
    except KeyError:
        hint = _default
    else:
        if hint is None:
            hint = _default
        # elif "@" not in hint:
        #     hint = "%s@%s" % (hint, p.netloc)

    oper.req_args["login_hint"] = hint


def ui_locales(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Set the request argument 'ui_locales' to something configured or use the default.
    Example:
        "ui_locales": null
    """

    oper.req_args["ui_locales"] = oper.conv.get_tool_attribute(
        "ui_locales", 'locales', default=['se'])


def claims_locales(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Set the request argument 'claims_locales' to something configured or use the default.
    Example:
        "claims_locales": null
    """

    oper.req_args["claims_locales"] = oper.conv.get_tool_attribute(
        "claims_locales", 'locales', default=['se'])


def get_attribute_value(oper, tool_attr, provider_attr, default):
    """
    Context:
        Support function
    Action:
        Picks up values from a given set of ordered attributes
    Args:
        tool_attr: tool configuration attributes.
        provider_attr: Provider info attribute
       default: If no values could be found use this
    """

    try:
        val = oper.conv.get_tool_attribute(*tool_attr)
    except KeyError:
        if provider_attr:
            try:
                val = oper.conv.entity.provider_info[provider_attr]
            except (KeyError, AttributeError):
                val = default
        else:
            val = default

    return val


def acr_value(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Sets the request attribute 'acr_values' to something configured,
        something gotten from the OP or to a default.
    Example:
        "acr_value": null
    """

    acr = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                              "acr_values_supported", ["1", "2"])
    oper.req_args["acr_values"] = acr


def specific_acr_claims(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Use the claims request parameter to specify which acr value should be used.
    Args:
        A default set of acr_values
    Example:
        "specific_acr_claims": ['1']
    """

    _acrs = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                                "acr_values_supported", args)
    oper.req_args["claims"] = {"id_token": {"acr": {"values": _acrs}}}


def essential_and_specific_acr_claim(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Add to the request that an acr claims MUST be returned in the
        ID token. The value of acr is first picked from acr_values_supported in the
        provider info. If not acr_values_supported is given the test tool
        configuration will be used. If that is also missing it will be set to
        whatever args has as value
    Args:
        A default set of acr values
    Example:
        "essential_and_specific_acr_claim": "1"
    """
    _acrs = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                                "acr_values_supported", args)

    oper.req_args["claims"] = {
        "id_token": {"acr": {"value": _acrs[0], 'essential': True}}
    }


def sub_claims(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Specify a claim for a specific sub value. This is signalling that
        the OP should authenticate a specific subject. The sub value is fetch from
        an id_token received in connection to a previous authorization.
    Example:
        "sub_claims": null
    """
    res = get_id_tokens(oper.conv)
    try:
        res.extend(oper.conv.cache["id_token"])
    except (KeyError, ValueError):
        pass
    idt = res[-1]
    _sub = idt["sub"]
    oper.req_args["claims"] = {"id_token": {"sub": {"value": _sub}}}


def set_essential_arg_claim(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Specify an essential claim. Whether it should be placed in the
        id_token or returned together with the user info depends on the profile used.
    Args:
        A claim name
    Example:
        "set_essential_arg_claim": "name"
    """
    if return_type(oper.tool_conf['profile']) == 'I':
        oper.req_args["claims"] = {"id_token": {args: {"essential": True}}}
    else:
        oper.req_args["claims"] = {"userinfo": {args: {"essential": True}}}


def multiple_return_uris(oper, args):
    """
    Context:
        Registration
    Action:
        Makes the request contain two redirect_uris. Default is that it only contains one.
    Example:
        "multiple_return_uris": null
    """
    redirects = oper.conv.entity.registration_info['redirect_uris'][:]
    redirects.append("%scb" % get_base(oper.conv.entity.base_url))
    oper.req_args["redirect_uris"] = redirects


def redirect_uri_with_query_component(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Add a query component to the redirect_uri
    Args:
        Dictionary with claims and values to build the query part from
    Example:
        "redirect_uri_with_query_component": {
          "foo": "bar"
        }
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uri": [ru]})


def redirect_uris_with_query_component(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Add a query component to the redirect_uris
    Args:
        Dictionary with attributes and values to build the query part from
    Example:
        "redirect_uris_with_query_component": {
          "foo": "bar"
        }
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uris": [ru]})


def redirect_uris_with_scheme(oper, args):
    """
    Context:
        Registration
    Action:
        Create a redirect_uri with a specific scheme.
    Args:
        The scheme to use
    Example:
        "redirect_uris_with_scheme": "http"
    """
    oper.req_args['redirect_uris'] = [
        r.replace('https', args) for r in
        oper.conv.entity.registration_info['redirect_uris'][0]]


def redirect_uris_with_fragment(oper, kwargs):
    """
    Context:
        Registration
    Action:
        Add a fragment component to a redirect_uri
    Args:
        Dictionary with attributes and values to build the query part from
    Example:
        "redirect_uris_with_fragment": {
          "foo": "bar"
        }
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "#" + ".".join(["%s%s" % (x, y) for x, y in list(kwargs.items())])
    oper.req_args["redirect_uris"] = [ru]


def post_logout_redirect_uri_with_query_component(oper, args):
    """
    Context:
        AsyncAuthn
    Action:
        Add a query component to the post_logout_redirect_uri
    Args:
        Dictionary with keys and values to build the query part from
    Example:
        "post_logout_redirect_uri_with_query_component": {"foo":  "bar"}
    """
    ru = oper.conv.entity.registration_info['post_logout_redirect_uris'][0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"post_logout_redirect_uri": [ru]})


def request_in_file(oper, kwargs):
    """
    Context:
        AsyncAuthn
    Action:
        Sets the operation argument 'base_path' to where the request
        can be found. This is about the usage of the request_uri parameter.
    Example:
        "request_in_file": null
    """

    oper.op_args["base_path"] = get_base(oper.conv.entity.base_url) + "export/"


def conditional_execution(oper, arg):
    """
    Context:
        AccessToken/UserInfo
    Action:
        If the condition is not fulfilled the operation will not be executed.
    Args:
        Dictionary with claim as key and allowed values as values
    Example:
        "conditional_execution":{
          "return_type": ["CIT","CI","C","CT"]
        }
    """

    for key, val in arg.items():
        if key == 'profile':
            try:
                if oper.profile[0] not in val.split(','):
                    oper.skip = True
                    return
            except AttributeError:
                if oper.profile[0] not in val:
                    oper.skip = True
                    return

        elif key == 'return_type':
            if oper.profile[0] not in val:
                oper.skip = True
                return


def check_config(oper, args):
    """
    Context:
        VerifyConfiguration
    Action:
        Verifies that certain parameters appear in the configuration.
    Args:
        Dictionary with parameters and values that MUST be in the tool configuration
    Example:
        "check_config": {
          "login_hint": null
        }
    """

    _cnf = oper.conv.tool_config
    for key, val in args.items():
        if key in _cnf:
            if val and val != _cnf[key]:
                _msg = "{}={} not OK, should have been {}".format(key, val,
                                                                  _cnf[key])
                oper.conv.events.store(EV_CONDITION,
                                       State("Check support", status=ERROR,
                                             message=_msg))
                oper.unsupported = _msg
        else:
            _msg = "No {} in the configuration".format(key)
            oper.conv.events.store(EV_CONDITION,
                                   State("Check support", status=ERROR,
                                         message=_msg))

            oper.unsupported = _msg


def set_state(oper, arg):
    """
    Context:
        RefreshAccessToken
    Action:
        Sets the operation argument 'state' to what has been used previously in the session.
    Example:
        "set_state": null
    """

    oper.op_args['state'] = oper.conv.state


def set_req_args_state(oper, arg):
    """
    Context:
        RefreshAccessToken
    Action:
        Sets the request argument 'state' to what has been used previously in the session.
    Example:
        "set_state": null
    """

    oper.req_args['state'] = oper.conv.state


def set_post_logout_redirect_uri(oper, arg):
    """
    Context:
        EndSession
    Action:
        Sets the 'post_logout_redirect_uri' argument in the request
    Example:
        "set_post_logout_redirect_uri": null
    """
    ent = oper.conv.entity
    oper.req_args["post_logout_redirect_uri"] = ent.registration_info[
        'post_logout_redirect_uris'][0]


def register_signing_arg(oper, arg):
    """
    Context:
        ClientRegistration
    Action:
        Registers a signing algorithm that the provider supports
    Example:
        "register_signing_arg": "id_token"
    """
    map = {
        'id_token': 'id_token_signed_response_alg',
        'userinfo': 'userinfo_signed_response_alg',
        'request_object': 'request_object_signing_alg',
        'token_endpoint': 'token_endpoint_auth_signing_alg'
    }

    _pinfo = oper.conv.entity.provider_info
    _pref = oper.conv.entity.pref

    # What the provider can do
    _algs = _pinfo[PREFERENCE2PROVIDER[map[arg]]]

    oper.op_args[map[arg]] = _algs[0]


def register(oper, arg):
    """
    Context:
        ClientRegistration
    Action:
        Registers a set of claims
    Args:
        List of claims to register.
    Example:
        "register": [ "userinfo_signed_response_alg" ]

    """
    for a in arg:
        oper.req_args[a] = oper.conv.entity.provider_info[
            PREFERENCE2PROVIDER[a]][0]


def set_end_session_state(oper, arg):
    """
    Context:
        EndSession
    Action:
        Sets the 'state' argument in a end_session request. Note that this
        'state' variable has nothing to do with the authorization request 'state'
    Example:
        "set_end_session_state": null
    """
    _state = rndstr(32)
    oper.conv.end_session_state = _state
    oper.req_args["state"] = _state


def set_client_authn_method(oper, arg):
    """
    Context:
        AccessToken
    Action:
        Sets the operation argument 'authn_method' to what the client wants to use, what the
        provider supports or the default according to the standard.
    Example:
        "set_client_authn_method" : null
    """
    _entity = oper.conv.entity
    try:
        _method = _entity.behaviour["token_endpoint_auth_method"]
    except KeyError:
        try:
            _method = _entity.provider_info[
                "token_endpoint_auth_methods_supported"][0]
            # generate a key error if client authn method is not supported by
            # pyoidc
            m = CLIENT_AUTHN_METHOD[_method]
        except KeyError:  # Go with default
            _method = 'client_secret_basic'

    oper.op_args['authn_method'] = _method


def create_idtoken_hint_other_issuer(oper, arg):
    """
    Context:
        EndSession
    Action:
        Sets the 'id_token_hint' argument in a end_session request.
        The value of the argument is a correct signed JWT but not the one
        that should have been used.
    Example:
        "create_idtoken_hint_other_issuer": null
    """
    iss = oper.conv.entity.client_id
    op = oper.conv.entity.provider_info['issuer']
    iat = time_sans_frac()
    exp = iat+3600
    idt = IdToken(iss=iss, aud=[op], iat=iat, exp=exp, **arg)
    keys = oper.conv.entity.keyjar.get_signing_key('rsa')
    _jwt = idt.to_jwt(keys, 'RS256')
    oper.req_args["id_token_hint"] = _jwt


def modified_idtoken_hint(oper, arg):
    """
    Context:
        EndSession
    Action:
        Sets the 'id_token_hint' argument in a end_session request.
        The value of the argument is a incorrect signed JWT.
    Example:
        "create_idtoken_hint_other_issuer": null
    """
    res = get_signed_id_tokens(oper.conv)
    if res:
        _jws = jws_factory(res[-1])

        header = as_unicode(b64e(as_bytes(json.dumps({'alg': 'none'}))))
        oper.req_args["id_token_hint"] = '.'.join(
            [header, as_unicode(_jws.jwt.b64part[1]), ''])


def set_backchannel_logout_uri(oper, args):
    """
    Context:
        Registration
    Action:
        Creates a backchannel_logout_uri and adds it to the client registration request arguments
    Example:
        "set_backchannel_logout_uri": null
    """
    _base = get_base(oper.conv.entity.base_url)
    entity_id = rndstr(24)
    oper.conv.entity.entity_id = entity_id
    oper.req_args['backchannel_logout_uri'] = "{}{}?entity_id={}".format(
        _base, "backchannel_logout", entity_id)


def set_frontchannel_logout_uri(oper, args):
    """
    Context:
        Registration
    Action:
        Creates a frontchannel_logout_uri and adds it to the client registration request arguments
    Example:
        "set_frontchannel_logout_uri": null
    """
    _base = get_base(oper.conv.entity.base_url)
    entity_id = rndstr(24)
    oper.conv.entity.entity_id = entity_id
    oper.req_args['frontchannel_logout_uri'] = "{}{}?entity_id={}".format(
        _base, "frontchannel_logout", entity_id)


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from otest.func import factory as ofactory

    return ofactory(name)
