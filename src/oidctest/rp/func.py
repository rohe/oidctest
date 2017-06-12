from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlparse

import inspect
import os
import sys

from otest.result import get_issuer


def set_webfinger_resource(oper, args):
    """
    Context: WebFinger Query
    Action: Specifies the webfinger resource. If the OP supports
    webfinger queries then the resource is set to the value of 'webfinger_url'
    or 'webfinger_email' from the test instance configuration.

    :param oper: An WebFinger instance
    :param args: None or a dictionary with the key 'pattern'
    """

    try:
        oper.resource = oper.op_args["resource"]
    except KeyError:
        if oper.dynamic:
            if args:
                _p = urlparse(get_issuer(oper.conv))
                oper.op_args["resource"] = args["pattern"].format(
                    test_id=oper.conv.test_id, host=_p.netloc,
                    oper_id=oper.conv.operator_id)
            else:
                _base = oper.sh.tool_conf['issuer']
                if oper.conv.operator_id is None:
                    oper.resource = _base
                else:
                    oper.resource = os.path.join(_base, oper.conv.operator_id,
                                                 oper.conv.test_id)


def set_configuration(oper, arg):
    oper.conv.entity.capabilities.update(arg)


def set_start_page(oper, args):
    _conf = oper.sh['test_conf']
    _url = _conf['start_page']
    _iss = oper.conv.entity.baseurl
    _params = _conf['params'].replace('<issuer>', _iss)
    _args = dict([p.split('=') for p in _params.split('&')])
    oper.start_page = _url + '?' + urlencode(_args)


def set_op(oper, args):
    _op = oper.conv.entity
    for key, val in args.items():
        _attr = getattr(_op, key)
        if isinstance(_attr, dict):
            _attr.update(val)
        else:
            _attr = val


def set_request_base(oper, args):
    oper.op_args['base_path'] = '{}{}/'.format(oper.conv.entity.base_url, args)
    oper.op_args['local_dir'] = args


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


def resource(oper, args):
    """
    Context:
    Action:
    Example:

    :param oper: 
    :param args: 
    :return: 
    """

    _p = urlparse(get_issuer(oper.conv))
    oper.op_args["resource"] = args["pattern"].format(
        test_id=oper.conv.test_id, host=_p.netloc,
        oper_id=oper.conv.operator_id)


def set_jwks_uri(oper, args):
    """
    Context: AsyncAuthn
    Action:
    Example:

    :param oper: 
    :param args: 
    :return: 
    """

    oper.req_args["jwks_uri"] = oper.conv.entity.jwks_uri


def remove_grant(oper, arg):
    """
    Context:
    Action:
    Example:

    :param oper: 
    :param args: 
    :return: 
    """

    oper.conv.entity.grant = {}


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


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from oidctest.testfunc import factory as ot_factory

    return ot_factory(name)
