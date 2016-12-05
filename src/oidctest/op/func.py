import inspect
import json
import os
import sys

from future.backports.urllib.parse import urlparse
from future.backports.urllib.parse import urlencode

from otest import ConfigurationError
from otest.check import ERROR
from otest.check import get_signed_id_tokens
from otest.check import State
from otest.check import STATUSCODE_TRANSL
from otest.events import EV_CONDITION
from otest.events import EV_RESPONSE
from otest.result import get_issuer

from oidctest.op.check import get_id_tokens
from oidctest.prof_util import map_prof

from past.types import basestring

__author__ = 'roland'


def set_webfinger_resource(oper, args):
    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        if oper.dynamic:
            _base = oper.conv.get_tool_attribute("webfinger_url",
                                                 "webfinger_email")
            if _base is None:
                raise AttributeError(
                    'If you want to do dynamic webfinger discovery you must '
                    'define "webfinger_url" or "webfinger_email" in the '
                    '"tool" configuration')

            if oper.conv.operator_id is None:
                oper.resource = _base
            else:
                oper.resource = os.path.join(_base, oper.conv.operator_id,
                                             oper.conv.test_id)


def set_discovery_issuer(oper, args):
    if oper.dynamic:
        oper.op_args["issuer"] = get_issuer(oper.conv)


def redirect_uri_with_query_component(oper, args):
    ru = oper.conv.get_redirect_uris()[0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uri": ru})


def set_response_where(oper, args):
    if oper.req_args["response_type"] != ["code"]:
        oper.response_where = "fragment"


def check_support(oper, args):
    # args = { level : kwargs }
    for level, kwargs in list(args.items()):
        for key, val in list(kwargs.items()):
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
        _val = oper.tool_conf[args['param']]
    except KeyError:
        raise ConfigurationError("Missing parameter: %s" % args["param"])
    else:
        oper.req_args["principal"] = _val


def set_uri(oper, args):
    ru = oper.conv.get_redirect_uris()[0]
    p = urlparse(ru)
    oper.req_args[args[0]] = "%s://%s/%s" % (p.scheme, p.netloc, args[1])


def static_jwk(oper, args):
    _client = oper.conv.entity
    oper.req_args["jwks_uri"] = None
    oper.req_args["jwks"] = {"keys": _client.keyjar.dump_issuer_keys("")}


def get_base(base):
    """
    Make sure a '/' terminated URL is returned
    """
    part = urlparse(base)

    if part.path:
        if not part.path.endswith("/"):
            _path = part.path[:] + "/"
        else:
            _path = part.path[:]
    else:
        _path = "/"

    return "%s://%s%s" % (part.scheme, part.netloc, _path,)


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

    f = open("%ssiu.json" % "export/", 'w')
    f.write(json.dumps(ruris))
    f.close()

    sector_identifier_url = "%s%s%s" % (_base, "export/", "siu.json")
    oper.req_args["sector_identifier_uri"] = sector_identifier_url


def set_expect_error(oper, args):
    oper.expect_error = args


def id_token_hint(oper, kwargs):
    res = get_signed_id_tokens(oper.conv)

    try:
        res.extend(oper.conv.cache["id_token"])
    except (KeyError, ValueError):
        pass

    oper.req_args["id_token_hint"] = res[0]


def login_hint(oper, args):
    _iss = oper.conv.entity.provider_info["issuer"]
    p = urlparse(_iss)
    try:
        hint = oper.conv.get_tool_attribute("login_hint")
    except KeyError:
        hint = "buffy@%s" % p.netloc
    else:
        if "@" not in hint:
            hint = "%s@%s" % (hint, p.netloc)

    oper.req_args["login_hint"] = hint


def ui_locales(oper, args):
    oper.req_args["ui_locales"] = oper.conv.get_tool_attribute(
        "ui_locales", 'locales', default=['se'])


def claims_locales(oper, args):
    oper.req_args["claims_locales"] = oper.conv.get_tool_attribute(
        "claims_locales", 'locales', default=['se'])


def acr_value(oper, args):
    oper.req_args["acr_values"] = oper.conv.get_tool_attribute(
        "acr_value", "acr_values_supported", default=["1", "2"])


def specific_acr_claims(oper, args):
    _acrs = oper.req_args["acr_values"] = oper.conv.get_tool_attribute(
        "acr_value", "acr_values_supported", default=["2"])

    oper.req_args["claims"] = {"id_token": {"acr": {"values": _acrs}}}


def sub_claims(oper, args):
    res = get_id_tokens(oper.conv)
    try:
        res.extend(oper.conv.cache["id_token"])
    except (KeyError, ValueError):
        pass
    idt = res[-1]
    _sub = idt["sub"]
    oper.req_args["claims"] = {"id_token": {"sub": {"value": _sub}}}


def multiple_return_uris(oper, args):
    redirects = oper.conv.entity.redirect_uris
    redirects.append("%scb" % get_base(oper.conv.entity.base_url))
    oper.req_args["redirect_uris"] = redirects


def redirect_uris_with_query_component(oper, kwargs):
    ru = oper.conv.get_redirect_uris()[0]
    ru += "?%s" % urlencode(kwargs)
    oper.req_args["redirect_uris"] = ru


def redirect_uris_with_fragment(oper, kwargs):
    ru = oper.conv.get_redirect_uris()[0]
    ru += "#" + ".".join(["%s%s" % (x, y) for x, y in list(kwargs.items())])
    oper.req_args["redirect_uris"] = ru


def request_in_file(oper, kwargs):
    oper.op_args["base_path"] = get_base(oper.conv.entity.base_url) + "export/"


def resource(oper, args):
    _p = urlparse(get_issuer(oper.conv))
    oper.op_args["resource"] = args["pattern"].format(
        test_id=oper.conv.test_id, host=_p.netloc,
        oper_id=oper.conv.operator_id)


def expect_exception(oper, args):
    oper.expect_exception = args


def conditional_expect(oper, args):
    condition = args["condition"]

    res = True
    for key in list(condition.keys()):
        try:
            assert oper.req_args[key] in condition[key]
        except KeyError:
            pass
        except AssertionError:
            res = False

    for param in ['error', 'exception']:
        do_set = False
        try:
            if res == args["oper"]:
                do_set = True
        except KeyError:
            if res is True:
                do_set = True

        if do_set:
            try:
                setattr(oper, 'expect_{}'.format(param), args[param])
            except KeyError:
                pass


def conditional_execution(oper, arg):
    for key, val in arg.items():
        if key == 'profile':
            if not map_prof(oper.profile, val):
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


def skip_operation(oper, arg):
    if oper.profile[0] in arg["flow_type"]:
        oper.skip = True


def remove_post_test(oper, arg):
    try:
        oper.tests['post'].remove(arg)
    except ValueError:
        pass


def remove_grant(oper, arg):
    oper.conv.entity.grant = {}


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from otest.func import factory as aafactory

    return aafactory(name)
