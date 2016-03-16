import json
from aatest import Unknown

__author__ = 'roland'


def translate(spec, func_factories):
    asp = {}
    for key, args in spec.items():
        _fnc = None
        for fact in func_factories:
            try:
                _fnc = fact(key)
            except Exception:
                pass
            else:
                break
        if not _fnc:
            raise Unknown('Check {}'.format(key))
        asp[_fnc] = args
    return asp


COPY = ['descr']


def parse_json_conf(cnf_file, cls_factories, chk_factories, func_factories):
    """

    :param cnf_file:
    :param cls_factories:
    :param chk_factory:
    :return:
    """
    stream = open(cnf_file, 'r')
    js = json.load(stream)
    stream.close()
    res = {}
    for tid, spec in js.items():
        ops = {}
        for oper, asse in spec.items():
            if oper == 'setup':
                if asse:
                    ops['setup'] = translate(asse, func_factories)
                else:
                    ops['setup'] = {}
            elif oper in COPY:
                ops[oper] = asse
            else:
                _cls = ''
                for fact in cls_factories:
                    try:
                        _cls = fact(oper)
                    except Exception:
                        pass
                    else:
                        break
                if not _cls:
                    raise Unknown('Operation {}'.format(oper))

                ops[_cls.__name__] = {'assert': {}}
                if 'assert' in asse and asse['assert'] is not None:
                    ops[_cls.__name__]['assert'] = translate(
                        asse['assert'], chk_factories)
        res[tid] = ops
    return res
