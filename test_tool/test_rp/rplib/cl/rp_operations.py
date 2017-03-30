#!/usr/bin/env python3

from oidctest.rp.pathmap import IDMAP

l = list(IDMAP.keys())
l.sort()
for o in l:
    print(o)
