import os

from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlparse
from otest.func import SetUpError, get_base
from otest.prof_util import return_type
from past.types import basestring

import inspect
import json
import sys

from otest import ConfigurationError
from otest.check import ERROR
from otest.check import STATUSCODE_TRANSL
from otest.check import State
from otest.check import get_signed_id_tokens
from otest.events import EV_CONDITION
from otest.events import EV_RESPONSE
from otest.result import get_issuer

from oidctest.op.check import get_id_tokens

__author__ = 'roland'


def set_webfinger_resource(oper, args):
    """
    Context: WebFinger Query
    Action: Specifies the webfinger resource. If the OP supports
    webfinger queries then the resource is set to the value of 'webfinger_url'
    or 'webfinger_email' from the test instance configuration.

    :param oper: An WebFinger instance
    :param args: None
    """

    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        if oper.dynamic:
            _base = oper.conv.get_tool_attribute("webfinger_url",
                                                 "webfinger_email")
            if _base is None:
                raise SetUpError(
                    'If you want to do dynamic webfinger discovery you '
                    'must define "webfinger_url" or "webfinger_email" in '
                    'the "tool" configuration')

            oper.resource = _base


def set_discovery_issuer(oper, args):
    """
    Context: Authorization Query
    Action: Pick up issuer ID either from static configuration or dynamic
    discovery.

    :param oper: An AsyncAuthn instance
    :param args: None
    """
    if oper.dynamic:
        oper.op_args["issuer"] = get_issuer(oper.conv)


def set_response_where(oper, args):
    """
    Context: Authorization Query
    Action: Set where the response is expected to occur

    :param oper: An AsyncAuthn instance
    :param args: dictionary with keys: 'response_type', 'not_response_type'
        and "where"
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
    Context: Authorization Query
    Action: Verify that the needed support is supported by the OP
    Example:

        "check_support": {
          "WARNING": {"scopes_supported": ["phone"]}
        }

        "check_support": {
          "ERROR": {"id_token_signing_alg_values_supported": null}
        }

    :param oper: An AsyncAuthn instance
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
    try:
        _val = oper.conv.tool_config[args['param']]
    except KeyError:
        raise ConfigurationError("Missing parameter: %s" % args["param"])
    else:
        oper.req_args["principal"] = _val


def static_jwk(oper, args):
    _client = oper.conv.entity
    del oper.req_args["jwks_uri"]
    oper.req_args["jwks"] = _client.keyjar.export_jwks("")


def store_sector_redirect_uris(oper, args):
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


def id_token_hint(oper, kwargs):
    res = get_signed_id_tokens(oper.conv)

    oper.req_args["id_token_hint"] = res[0]


def login_hint(oper, args):
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
        elif "@" not in hint:
            hint = "%s@%s" % (hint, p.netloc)

    oper.req_args["login_hint"] = hint


def ui_locales(oper, args):
    oper.req_args["ui_locales"] = oper.conv.get_tool_attribute(
        "ui_locales", 'locales', default=['se'])


def claims_locales(oper, args):
    oper.req_args["claims_locales"] = oper.conv.get_tool_attribute(
        "claims_locales", 'locales', default=['se'])


def get_attribute_value(oper, tool_attr, provider_attr, default):
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
    acr = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                              "acr_values_supported", ["1", "2"])
    oper.req_args["acr_values"] = acr


def specific_acr_claims(oper, args):
    _acrs = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                                "acr_values_supported", args)
    oper.req_args["claims"] = {"id_token": {"acr": {"values": _acrs}}}


def essential_and_specific_acr_claim(oper, args):
    """
    Context: Authorization Request
    Action: Add to the request that an acr claims MUST be returned in the
     ID token. The value of acr is first picked from acr_values_supported in the
     provider info. If not acr_values_supported is given the test tool
     configuration will be used. If that is also missing it will be set to
     whatever args has as value.

    :param oper:
    :param args:
    """
    _acrs = get_attribute_value(oper, ["acr_value", "acr_values_supported"],
                                "acr_values_supported", args)

    oper.req_args["claims"] = {
        "id_token": {"acr": {"value": _acrs[0], 'essential': True}}}


def sub_claims(oper, args):
    """
    Context: Authorization Request
    Action: Specify a claim for a specific sub value. This is signalling that
     the OP should authenticate the specific subject.

    :param oper:
    :param args:
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
    Context: Authorization Request
    Action: Specify an essential claim.

    :param oper:
    :param args:
    :return:
    """
    if return_type(oper.tool_conf['profile']) == 'I':
        oper.req_args["claims"] = {"id_token": {args: {"essential": True}}}
    else:
        oper.req_args["claims"] = {"userinfo": {args: {"essential": True}}}


def multiple_return_uris(oper, args):
    """
    Context: dynamic client registration
    Action: makes the request contain two redirect_uris. Default is that
    it only contains one.

    :param oper: An Operation instance
    :param args: None
    """
    redirects = oper.conv.entity.registration_info['redirect_uris'][:]
    redirects.append("%scb" % get_base(oper.conv.entity.base_url))
    oper.req_args["redirect_uris"] = redirects


def redirect_uris_with_query_component(oper, kwargs):
    """
    Context: Dynamic Client Registration
    Action: Add a query component to a redirect_uri

    :param oper: An Operation Instance
    :param kwargs: Values to build the query part from
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "?%s" % urlencode(kwargs)
    oper.req_args["redirect_uris"] = [ru]


def redirect_uri_with_query_component(oper, args):
    """
    Context: Authorization request
    Action: Add a query component to the redirect_uri

    :param oper: An Operation Instance
    :param kwargs: Values to build the query part from
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uri": [ru]})


def redirect_uris_with_scheme(oper, args):
    """
    Context: Authorization Request
    Action: Create a redirect_uri with a specific scheme.

    :param oper: An Operation Instance
    :param args: The scheme to use
    """
    oper.req_args['redirect_uris'] = [
        r.replace('https', args) for r in
        oper.conv.entity.registration_info['redirect_uris'][0]]


def redirect_uris_with_fragment(oper, kwargs):
    """
    Context: Dynamic Client Registration
    Action: Add a fragment component to a redirect_uri

    :param oper: An Operation Instance
    :param kwargs: Values to build the query part from
    """
    ru = oper.conv.entity.registration_info['redirect_uris'][0]
    ru += "#" + ".".join(["%s%s" % (x, y) for x, y in list(kwargs.items())])
    oper.req_args["redirect_uris"] = [ru]


def request_in_file(oper, kwargs):
    oper.op_args["base_path"] = get_base(oper.conv.entity.base_url) + "export/"


def resource(oper, args):
    _p = urlparse(get_issuer(oper.conv))
    oper.op_args["resource"] = args["pattern"].format(
        test_id=oper.conv.test_id, host=_p.netloc,
        oper_id=oper.conv.operator_id)


def conditional_execution(oper, arg):
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


def set_jwks_uri(oper, args):
    oper.req_args["jwks_uri"] = oper.conv.entity.jwks_uri


def check_endpoint(oper, args):
    try:
        _ = oper.conv.entity.provider_info[args]
    except KeyError:
        oper.conv.events.store(
            EV_CONDITION,
            State(test_id="check_endpoint", status=ERROR,
                  message="{} not in provider configuration".format(args)))
        oper.fail = True


def cache_response(oper, arg):
    key = oper.conv.test_id
    oper.cache[key] = oper.conv.events.last_item(EV_RESPONSE)


def restore_response(oper, arg):
    key = oper.conv.test_id
    if oper.conv.events[EV_RESPONSE]:
        _lst = oper.cache[key][:]
        for x in oper.conv.events[EV_RESPONSE]:
            if x not in _lst:
                oper.conv.events.append(_lst)
    else:
        oper.conv.events.extend(oper.cache[key])

    del oper.cache[key]


def remove_post_test(oper, arg):
    try:
        oper.tests['post'].remove(arg)
    except ValueError:
        pass


def remove_grant(oper, arg):
    oper.conv.entity.grant = {}


def set_request_base(oper, args):
    oper.op_args['base_path'] = '{}{}/'.format(oper.conv.entity.base_url, args)
    oper.op_args['local_dir'] = args


def check_config(oper, args):
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
    oper.op_args['state'] = oper.conv.state


# def set_refresh_token(oper, args):
#     _state = oper.conv.state
#     oper.op_args = oper.conv.entity.


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from otest.func import factory as ofactory

    return ofactory(name)
