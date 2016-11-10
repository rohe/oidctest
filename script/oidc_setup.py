#!/usr/bin/env python

import sys
import os
import shutil
import fileinput
import filecmp
import datetime


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def copy_if_not_same(src, dst, overwrite=False):
    try:
        os.stat(dst)
    except OSError:
        shutil.copy(src, dst)
        return True

    if filecmp.cmp(src, dst):
        return False

    if modification_date(dst) > modification_date(src):
        if overwrite:
            shutil.copy(src, dst)
            return True

    return False


def oidc_op_setup(distroot):
    for _dir in ['certs', 'keys', 'server_log', 'log']:
        if os.path.isdir(_dir) is False:
            os.mkdir(_dir)

    _dir = 'htdocs'
    _op_dir = os.path.join(distroot['oidc'], 'test_tool', 'test_op', 'oidc_op',
                           'heart_mako', _dir)
    if os.path.isdir(_dir) is False:
        shutil.copytree(_op_dir, _dir)

    _dir = 'static'
    _op_dir = os.path.join(distroot['oidc'], 'test_tool', 'test_op',
                           'oidc_op', _dir)
    if os.path.isdir(_dir) is False:
        shutil.copytree(_op_dir, _dir)

    _op_dir = os.path.join(distroot['oidc'], 'test_tool', 'test_op', 'oidc_op')
    for _fname in ['flows.yaml', 'run.sh', 'sslconf.py']:
        _file = os.path.join(_op_dir, _fname)
        copy_if_not_same(_file, _fname)

    _file = os.path.join(_op_dir, 'config_examples', 'conf_TT.py')
    if copy_if_not_same(_file, 'example_conf.py'):
        for line in fileinput.input("example_conf.py", inplace=True):
            l = line.replace("../keys/", "./keys/").rstrip('\n')
            print(l)


def oidc_rpinst_setup(distroot):
    for _dir in ['certs', 'keys', 'server_log', 'log']:
        if os.path.isdir(_dir) is False:
            os.mkdir(_dir)

    _op_dir = os.path.join(distroot['oidc'], 'test_tool', 'test_rp', 'rpinst')
    for _dir in ['static', 'htdocs']:
        _src = os.path.join(_op_dir, _dir)
        if os.path.isdir(_dir) is False:
            shutil.copytree(_src, _dir)

    for _fname in ['flows.yaml', 'run.sh', 'example_conf.py', 'profiles.json',
                   'heart_interop_ports.csv']:
        _file = os.path.join(_op_dir, _fname)
        copy_if_not_same(_file, _fname)


def oidc_rplib_setup(distroot):
    for _dir in ['certs', 'keys', 'log']:
        if os.path.isdir(_dir) is False:
            os.mkdir(_dir)

    _op_dir = os.path.join(distroot['oidc'], 'test_tool', 'test_rp', 'rplib',
                           'op')

    for _dir in ['static', 'htdocs']:
        _src = os.path.join(_op_dir, _dir)
        if os.path.isdir(_dir) is False:
            shutil.copytree(_src, _dir)

    for _fname in ['run.sh', 'example_conf.py', 'test_rp_op.py', 'setup.py']:
        _file = os.path.join(_op_dir, _fname)
        copy_if_not_same(_file, _fname)


DIR = {
    'oidc_op': oidc_op_setup,
    'oidc_rpinst': oidc_rpinst_setup,
    'oidc_rplib': oidc_rplib_setup,
}

if __name__ == '__main__':
    _distroot = {'oidc': sys.argv[1]}
    _root = sys.argv[2]
    if os.path.isdir(_root) is False:
        os.makedirs(_root)

    os.chdir(_root)
    for _dir, func in DIR.items():
        if os.path.isdir(_dir) is False:
            os.mkdir(_dir)
        os.chdir(_dir)
        func(_distroot)
        os.chdir('..')
