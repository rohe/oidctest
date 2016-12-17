import inspect
import sys

from future.backports.urllib.parse import urlencode


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


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from oidctest.testfunc import factory as ot_factory

    return ot_factory(name)
