#!/usr/bin/env python3
import importlib
import psutil

from oidctest.tt.app import Application
from oidctest.tt.rest import REST
from otest.proc import find_test_instances

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='test_tool_conf')
parser.add_argument('-i', dest='iss')
parser.add_argument('-t', dest='tag')
parser.add_argument(dest="config")
args = parser.parse_args()

_conf = importlib.import_module(args.config)
_ttc = importlib.import_module(args.test_tool_conf)

rest = REST(_conf.BASE_URL)  # Base URL just place holder

_app = Application(_conf.TEST_SCRIPT, _conf.FLOWDIR, rest, _conf.PORT_MIN,
                   _conf.PORT_MAX, _ttc.BASE, args.test_tool_conf, '')

for pid, proc_info in find_test_instances('op_test_tool.py').items():
    if args.iss:
        if proc_info['iss'] != args.iss:
            continue

        if args.tag:
            if proc_info['tag'] != args.tag:
                continue

    print('Restarting: {iss} {tag}'.format(**proc_info))
    ps = psutil.Process(pid)
    ps.kill()

    _app.run_test_instance(proc_info['iss'], proc_info['tag'])
