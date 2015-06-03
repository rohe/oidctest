from urlparse import urlparse
from aatest.check import ERROR

__author__ = 'roland'

def resource(oper, args):
    _p = urlparse(oper.conv.conf.ISSUER)
    oper.op_args["resource"] = args["pattern"].format(oper.conv.test_id,
                                                      _p.netloc)


def expect_exception(oper, args):
    oper.expect_exception = args


def conditional_expect_exception(oper, args):
    condition = args["condition"]
    exception = args["exception"]

    for key in condition.keys():
        try:
            assert condition[key] == oper.req_args[key]
        except KeyError:
            pass
        except AssertionError:
            return  # Not applied

    oper.expect_exception = exception


def set_request_args(oper, args):
    oper.req_args.update(args)


def set_jwks_uri(oper, args):
    oper.req_args["jwks_uri"] = oper.conv.client.jwks_uri


def set_op_args(oper, args):
    oper.op_args.update(args)

def check_endpoint(oper, args):
    try:
        _ = oper.conv.client.provider_info[args]
    except KeyError:
        oper.conv.test_output.append(
            {"id": "check_endpoint",
             "status": ERROR,
             "message": "{} not in provider configuration".format(args)})
        oper.skip = True
