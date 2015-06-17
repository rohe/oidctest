import json
from urllib import urlencode
from urlparse import urlparse
from aatest import ConfigurationError
from oidctest.tool import get_redirect_uris
from oidctest.check import get_id_tokens

__author__ = 'roland'


def set_webfinger_resource(oper, args):
    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        oper.resource = oper.conf.ISSUER


def set_discovery_issuer(oper, args):
    if oper.dynamic:
        oper.op_args["issuer"] = oper.conv.info["issuer"]


def redirect_uri_with_query_component(oper, args):
    ru = get_redirect_uris(oper.conf.INFO)[0]
    ru += "?%s" % urlencode(args)
    oper.req_args.update({"redirect_uri": ru})


def set_response_where(oper, args):
    if oper.req_args["response_type"] != ["code"]:
        oper.response_where = "fragment"


def check_support(oper, args):
    # args = { level : kwargs }
    for level, kwargs in args.items():
        for key, val in kwargs.items():
            try:
                assert val in oper.conv.client.provider_info[key]
            except AssertionError:
                oper.conv.test_output(
                    {"status": level, "id": "Check support",
                     "message": "No support for: {}={}".format(key, val)})


def set_principal(oper, args):
    try:
        oper.req_args["principal"] = oper.conv.client_config[args["param"]]
    except KeyError:
        raise ConfigurationError("Missing parameter: %s" % args["param"])


def set_uri(oper, param, tail):
    ru = get_redirect_uris(oper.conv)[0]
    p = urlparse(ru)
    oper.req_args[param] = "%s://%s/%s" % (p.scheme, p.netloc, tail)


def static_jwk(oper, args):
    _client = oper.conv.client
    oper.req_args["jwks_uri"] = None
    oper.req_args["jwks"] = {"keys": _client.keyjar.dump_issuer_keys("")}


def get_base(cconf=None):
    """
    Make sure a '/' terminated URL is returned
    """
    try:
        part = urlparse(cconf["_base_url"])
    except KeyError:
        part = urlparse(cconf["base_url"])
    # part = urlparse(cconf["redirect_uris"][0])

    if part.path:
        if not part.path.endswith("/"):
            _path = part.path[:] + "/"
        else:
            _path = part.path[:]
    else:
        _path = "/"

    return "%s://%s%s" % (part.scheme, part.netloc, _path,)


def store_sector_redirect_uris(oper, args):
    _base = get_base(oper.conv.client_config)

    try:
        ruris = args["other_uris"]
    except KeyError:
        try:
            ruris = oper.req_args["redirect_uris"]
        except KeyError:
            ruris = oper.conv.client.redirect_uris

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
    res = get_id_tokens(oper.conv)

    try:
        res.extend(oper.conv.cache["id_token"])
    except (KeyError, ValueError):
        pass

    idt, jwt = res[0]
    oper.req_args["id_token_hint"] = jwt


def login_hint(oper, args):
    _iss = oper.conv.client.provider_info["issuer"]
    p = urlparse(_iss)
    try:
        hint = oper.conv.client_config["login_hint"]
    except KeyError:
        hint = "buffy@%s" % p.netloc
    else:
        if "@" not in hint:
            hint = "%s@%s" % (hint, p.netloc)

    oper.req_args["login_hint"] = hint


def ui_locales(oper, args):
    try:
        uil = oper.conv.client_config["ui_locales"]
    except KeyError:
        try:
            uil = oper.conv.client_config["locales"]
        except KeyError:
            uil = ["se"]

    oper.req_args["ui_locales"] = uil


def claims_locales(oper, args):
    try:
        loc = oper.conv.client_config["claims_locales"]
    except KeyError:
        try:
            loc = oper.conv.client_config["locales"]
        except KeyError:
            loc = ["se"]

    oper.req_args["claims_locales"] = loc


def acr_value(oper, args):
    try:
        acr = oper.conv.client_config["acr_value"]
    except KeyError:
        try:
            acr = oper.conv.client.provider_info["acr_values_supported"]
        except (KeyError, AttributeError):
            acr = ["1", "2"]

    oper.req_args["acr_values"] = acr


def specific_acr_claims(oper, args):
    try:
        _acrs = oper.conv.client_config["acr_values"]
    except KeyError:
        _acrs = ["2"]

    oper.req_args["claims"] = {"id_token": {"acr": {"values": _acrs}}}


def sub_claims(oper, args):
    res = get_id_tokens(oper.conv)
    try:
        res.extend(oper.conv.cache["id_token"])
    except (KeyError, ValueError):
        pass
    idt, _ = res[-1]
    _sub = idt["sub"]
    oper.req_args["claims"] = {"id_token": {"sub": {"value": _sub}}}


def multiple_return_uris(oper, args):
    redirects = get_redirect_uris(oper.conv)
    redirects.append("%scb" % get_base(oper.conv.client_config))
    oper.req_args["redirect_uris"] = redirects


def redirect_uris_with_query_component(oper, kwargs):
    ru = get_redirect_uris(oper.conv)[0]
    ru += "?%s" % urlencode(kwargs)
    oper.req_args["redirect_uris"] = ru


def redirect_uris_with_fragment(oper, kwargs):
    ru = get_redirect_uris(oper.conv)[0]
    ru += "#" + ".".join(["%s%s" % (x, y) for x,y in kwargs.items()])
    oper.req_args["redirect_uris"] = ru


def request_in_file(oper, kwargs):
    oper.opargs["base_path"] = get_base(oper.conv.client_config) + "export/"
