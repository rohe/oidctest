__author__ = 'roland'


def set_webfinger_resource(oper, args):
    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        oper.resource = oper.conf.ISSUER

def set_discovery_issuer(oper, args):
    if oper.dynamic:
        try:
            _ = oper.op_args["issuer"]
        except KeyError:
            oper.op_args["issuer"] = oper.conv.info["issuer"]
