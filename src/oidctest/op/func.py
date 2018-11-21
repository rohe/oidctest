from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlparse
from past.types import basestring

import inspect
import json
import os
import sys

from oic.oic import PREFERENCE2PROVIDER

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

from oidctest.op.check import get_id_tokens

__author__ = 'roland'


def set_webfinger_resource(oper, args):
    """
    Context: WebFinger
    Action: Specifies the webfinger resource. If the OP supports
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
    Context: AsyncAuthn
    Action: Pick up issuer ID either from static configuration or dynamic
    discovery.

    """
    if oper.dynamic:
        oper.op_args["issuer"] = get_issuer(oper.conv)


def set_response_where(oper, args):
    """
    Context: AsyncAuthn
    Action: Set where the response is expected to occur dependent on which 
     response_type it is or which it isn't.

    :param response_type:
    :param not_response_type: 
    :param where: Where should the Authroization response occur
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
    Context: AsyncAuthn
    Action: Verify that the needed support is supported by the OP
    Example:

        check_support: {
          WARNING: {scopes_supported: [phone]}
        }

        check_support: {
          ERROR: {id_token_signing_alg_values_supported: null}
        }

    :param args: A dictionary of dictionaries. {level: {item: value}}
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
                        if typ == bool or typ == basestring or typ == int:
                            if v != pinfo:
                                missing.append(v)
                        elif typ == [basestring]:
                            if v not in pinfo:
                                missing.append(v)
                else:
                    if typ == bool or typ == basestring or typ == int:
                        if val != pinfo:
                            missing = val
                    elif typ == [basestring]:
                        if val not in pinfo:
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
    Context: WebFinger
    Action: Set principal using a specific parameter
    Example:

        set_principal:
            param: webfinger_url
            
    :param param: Value "webfinger_url" or "webfinger_email"
    """
    try:
        _val = oper.conv.tool_config[args['param']]
    except KeyError:
        raise ConfigurationError("Missing parameter: %s" % args["param"])
    else:
        oper.req_args["principal"] = _val


def static_jwk(oper, args):
    """
    Context: Registration
    Action: Set a static JWKS, remove jwks_uri if specified.
    Example:
        
        static_jwk: null
        
    """
    _client = oper.conv.entity
    del oper.req_args["jwks_uri"]
    oper.req_args["jwks"] = _client.keyjar.export_jwks("")


def set_redirect_uri(oper, args):
    _base = get_base(oper.conv.entity.base_url)
    oper.req_args["redirect_uri"] = "%s%s" % (_base, args)


def set_redirect_uris(oper, args):
    _base = get_base(oper.conv.entity.base_url)
    oper.req_args["redirect_uris"] = ["%s%s" % (_base, a) for a in args]


def store_sector_redirect_uris(oper, args):
    """
    Context: Registration
    Action: Will store a number of redirectURIs in a file and add a
    "sector_identifier_uri" pointing to that file to the request arguments.
    Example:
        
        store_sector_redirect_uris:
            other_uris:
              - 'https://example.com/op'
              
    :param other_uris: list of complete URLs
    :param redirect_uris: Use default redirect_uris for this entity
    :param extra: Extra relative url paths
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
    Context: AsyncAuthn
    Action: Will pick up an id_token received in an earlier authorization 
    request and add it to the request argument "id_token_hint"
    Example:
    
        "id_token_hint": null

    """
    res = get_signed_id_tokens(oper.conv)
    if res:
        oper.req_args["id_token_hint"] = res[0]


def login_hint(oper, args):
    """
    Context: AsyncAuthn
    Action: Sets the request argument 'login_hint' to a value picked from the
    configuration.
    
    Example:
        "login_hint": null

    :param oper: 
    :param args: 
    :return: 
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
    Context: AsyncAuthn
    Action: Set the request argument 'ui_locales' to something configured or
    use the default.
    Example:
        "ui_locales": null

    """

    oper.req_args["ui_locales"] = oper.conv.get_tool_attribute(
        "ui_locales", 'locales', default=['se'])


def claims_locales(oper, args):
    """
    Context: AsyncAuthn
    Action: Set the request argument 'claims_locales' to something configured or
    use the default.
    Example:
        "claims_locales": null

    :param oper: 
    :param args: 
    :return: 
    """

    oper.req_args["claims_locales"] = oper.conv.get_tool_attribute(
        "claims_locales", 'locales', default=['se'])


def get_attribute_value(oper, tool_attr, provider_attr, default):
    """
    Context: Support function 
    Action: Picks up values from a given set of ordered attributes 
    Example:

    :param tool_attr: tool configuration attributes.
    :param provider_attr: Provider info attribute
    :param default: If no values could be found use this
    :return: value
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
    Context: AsyncAuthn
    Action: Sets the request attribute 'acr_values' to something configured,
    something gotten from the OP or to the default.
    Example:
        acr_value: null

    :param oper: 
    :param args: 
    :return: 
    """

    acr = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                              "acr_values_supported", ["1", "2"])
    oper.req_args["acr_values"] = acr


def specific_acr_claims(oper, args):
    """
    Context: AsyncAuthn
    Action: Use the claims request parameter to specify which acr value should
    be used
    Example:
        specific_acr_claims: '1'

    :param args: A default set of acr_values 
    """

    _acrs = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                                "acr_values_supported", args)
    oper.req_args["claims"] = {"id_token": {"acr": {"values": _acrs}}}


def essential_and_specific_acr_claim(oper, args):
    """
    Context: AsyncAuthn
    Action: Add to the request that an acr claims MUST be returned in the
     ID token. The value of acr is first picked from acr_values_supported in the
     provider info. If not acr_values_supported is given the test tool
     configuration will be used. If that is also missing it will be set to
     whatever args has as value.
    Example:
        "essential_and_specific_acr_claim": "1"

    :param args: A default set of acr values
    """
    _acrs = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                                "acr_values_supported", args)

    oper.req_args["claims"] = {
        "id_token": {"acr": {"value": _acrs[0], 'essential': True}}}


def sub_claims(oper, args):
    """
    Context: AsyncAuthn
    Action: Specify a claim for a specific sub value. This is signalling that
     the OP should authenticate a specific subject. The sub value is fetch from
     an id_token received in connection to a previous authorization.
    Example:
        sub_claims: null

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
    Context: AsyncAuthn
    Action: Specify an essential claim. Whether it should be placed in the
    id_token or returned together with the user info depends on the profile 
    used.
    Example:
        "set_essential_arg_claim": "name"

    :param args: A claim
    """
    if return_type(oper.tool_conf['profile']) == 'I':
        oper.req_args["claims"] = {"id_token": {args: {"essential": True}}}
    else:
        oper.req_args["claims"] = {"userinfo": {args: {"essential": True}}}


def multiple_return_uris(oper, args):
    """
    Context: Registration
    
    Action: makes the request contain two redirect_uris. Default is that
    it only contains one.
    
    Example:
        multiple_return_uris: null

    :param oper: An Operation instance
    :param args: None
    """
    redirects = oper.conv.entity.registration_info['redirect_uris'][:]
    redirects.append("%scb" % get_base(oper.conv.entity.base_url))
    oper.req_args["redirect_uris"] = redirects


def redirect_uri_with_query_component(oper, args):
    """
    Context: AsyncAuthn
    Action: Add a query component to the redirect_uri
    Example:
        redirect_uri_with_query_component:
            foo: bar

    :param oper: An Operation Instance
    :param kwargs: Values to build the query part from
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uri": [ru]})


def redirect_uris_with_query_component(oper, args):
    """
    Context: AsyncAuthn
    Action: Add a query component to the redirect_uris
    Example:
        redirect_uris_with_query_component:
            foo: bar

    :param oper: An Operation Instance
    :param kwargs: Values to build the query part from
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uris": [ru]})


def redirect_uris_with_scheme(oper, args):
    """
    Context: Registration
    Action: Create a redirect_uri with a specific scheme.

    :param args: The scheme to use
    """
    oper.req_args['redirect_uris'] = [
        r.replace('https', args) for r in
        oper.conv.entity.registration_info['redirect_uris'][0]]


def redirect_uris_with_fragment(oper, kwargs):
    """
    Context: Registration
    Action: Add a fragment component to a redirect_uri
    Example:
        "redirect_uris_with_fragment": {
          "foo": "bar"
        }

    :param kwargs: Values to build the query part from
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "#" + ".".join(["%s%s" % (x, y) for x, y in list(kwargs.items())])
    oper.req_args["redirect_uris"] = [ru]


def request_in_file(oper, kwargs):
    """
    Context: AsyncAuthn
    Action: Sets the operation argument 'base_path' to where the request 
     can be found
    Example:
        request_in_file: null

    """

    oper.op_args["base_path"] = get_base(oper.conv.entity.base_url) + "export/"


def conditional_execution(oper, arg):
    """
    Context: AccessToken/UserInfo
    Action: If the condition is not fulfilled the operation will not be 
    executed.
    
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
    Context: VerifyConfiguration
    Action:
    Example:
        "check_config": {
          "login_hint": null
        }

    :param args: Dictionary with parameters and values that MUST be in the
    tool configuration
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
    Context: RefreshAccessToken
    Action: Sets the operation argument 'state' to what has been used
    previously in the session.
    Example:
        "set_state": null

    """

    oper.op_args['state'] = oper.conv.state


def register(oper, arg):
    for a in arg:
        oper.req_args[a] = oper.conv.entity.provider_info[
            PREFERENCE2PROVIDER[a]][0]


def set_client_authn_method(oper, arg):
    _entity = oper.conv.entity
    try:
        _method = _entity.behaviour["token_endpoint_auth_method"]
    except KeyError:
        try:
            _method = _entity.provider_info[
                "token_endpoint_auth_methods_supported"][0]
        except KeyError:  # Go with default
            _method = 'client_secret_basic'

    oper.op_args['authn_method'] = _method


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from otest.func import factory as ofactory

    return ofactory(name)
