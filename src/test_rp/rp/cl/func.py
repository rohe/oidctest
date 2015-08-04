from oidctest.oper import include

__author__ = 'roland'

def set_webfinger_resource(oper, args):
    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        oper.resource = oper.conf.ISSUER+oper.test_id

def set_discovery_issuer(oper, args):
    if oper.dynamic:
        try:
            _issuer = include(oper.op_args["issuer"], oper.test_id)
        except KeyError:
            _issuer = include(oper.conv.info["issuer"], oper.test_id)

        oper.op_args["issuer"] = _issuer

def set_expect_error(oper, args):
    oper.expect_error = args


