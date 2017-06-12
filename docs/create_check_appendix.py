#!/usr/bin/env python3

import inspect

from oidctest.op import check as op_check
from otest.aus import check as aus_check
from otest.check import Check


def split_line(line):
    words = line.split(' ')
    lin = []
    l = ''
    for w in words:
        if len(l) +1 + len(w) > 80:
            lin.append(l)
            l = w
        else:
            if l :
                l += ' '
                l += w
            else:
                l = w
    if l:
        lin.append(l)
    return '\n'.join(lin)


def doc(mod):
    res = {}
    for name, obj in inspect.getmembers(mod):
        if inspect.isclass(obj) and issubclass(obj, Check):
            if obj.__doc__:
                try:
                     _txt = obj.__doc__.strip()
                except AttributeError:
                    pass
                else:
                    _txt = ' '.join([t.strip() for t in _txt.split('\n')])
                    if len(_txt) > 80:
                        _txt = split_line(_txt)
                    try:
                        _txt += '\n{}'.format(obj.doc)
                    except AttributeError:
                        pass
                    res[obj.cid] = _txt
            else:
                res[obj.cid] = 'No description'
    return res

res = doc(op_check)
res.update(doc(aus_check))

fp = open('appendix_check.md', 'w')

kl = list(res.keys())
kl.sort()

line = []

for key in kl:
    line.append('## {}'.format(key))
    line.append('')
    line.append(res[key])
    line.append('')

fp.write('\n'.join(line))
fp.close()
