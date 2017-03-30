#!/usr/bin/env python
import os
import sys

from oidctest.site_setup import fedoidc_rplib_setup
from oidctest.site_setup import oidc_cp_rplib_setup
from oidctest.site_setup import oidc_op_setup
from oidctest.site_setup import oidc_rpinst_setup

DIR = {
    'oidc_op': oidc_op_setup,
    'oidc_rpinst': oidc_rpinst_setup,
    #'oidc_rplib': oidc_rplib_setup,
    'oidc_cp_rplib': oidc_cp_rplib_setup,
    'fedoidc_rplib': fedoidc_rplib_setup
}

if len(sys.argv) != 3:
    print('Usage: oidc_setup.py <root of oidctest src> <test site dir>')
    exit()

_distroot = {'oidc': sys.argv[1]}
_root = sys.argv[2]
if os.path.isdir(_root) is False:
    os.makedirs(_root)

os.chdir(_root)
for _dir, func in DIR.items():
    if os.path.isdir(_dir) is False:
        os.mkdir(_dir)
    os.chdir(_dir)
    func(_distroot['oidc'])
    os.chdir('..')
