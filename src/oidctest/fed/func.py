import inspect
import sys

__author__ = 'roland'


def set_illegal_value(oper, args):
    oper.op_args['base_path'] = '{}{}/'.format(oper.conv.entity.base_url, args)
    oper.op_args['local_dir'] = args


def factory(name):
    for fname, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj):
            if fname == name:
                return obj

    from oidctest.op.func import factory as _factory
    return _factory(name)
