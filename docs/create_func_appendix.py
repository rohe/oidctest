#!/usr/bin/env python3
import inspect

from oidctest.op import func as op_func


def doc(mod):
    res = {}
    others = []
    for fname, obj in inspect.getmembers(mod):
        if fname == 'factory':
            continue
        if inspect.isfunction(obj):
            if obj.__doc__:
                cl = []
                for p in obj.__doc__.split('\n'):
                    if 'Context' in p:
                        c = p.split(':')[1].strip()
                        cl = c.split('/')

                for c in cl:
                    try:
                        res[c][fname] = obj.__doc__
                    except KeyError:
                        res[c] = {fname: obj.__doc__}
            else:
                others.append(fname)

    return res


res = doc(op_func)

fp = open('appendix_func.md', 'w')

kl = list(res.keys())
kl.sort()

line = []

pk = ''
for key in kl:
    if pk != key:
        line.append('## {}'.format(key))
        line.append('')
        pk = key
    fn = list(res[key].keys())
    fn.sort()
    for n in fn:
        line.append('### {}'.format(n))
        line.append('')
        line.append(res[key][n])
        line.append('')

fp.write('\n'.join(line))
fp.close()
