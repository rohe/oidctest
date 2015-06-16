import json
from urllib import urlencode
from urlparse import urlparse
from aatest import ConfigurationError
from oidctest.tool import get_redirect_uris

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
