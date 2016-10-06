#!/usr/bin/env python3
from oidctest.rp import test_config

l = list(test_config.CONF.keys())
l.sort()

for o in l:
    print(o)