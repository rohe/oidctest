#!/usr/bin/env python

import importlib
import json
import logging
import argparse
from aatest.common import setup_logger
from aatest.result import Result

from future.backports.urllib.parse import urlparse

from aatest.parse_cnf import parse_yaml_conf
from oic.utils.keyio import build_keyjar

from oidctest.op import func
from oidctest.op import check
from oidctest.op.prof_util import ProfileHandler
from oidctest.op.tool import ClTester
from oidctest.session import SessionHandler
from aatest.io import ClIO

from requests.packages import urllib3

urllib3.disable_warnings()

__author__ = 'roland'

logger = logging.getLogger("")

if __name__ == '__main__':
    from oic.oic.message import factory as oic_message_factory

    from oidctest.op import profiles
    from oidctest.op import oper

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', dest='yaml_flows')
    parser.add_argument('-l', dest="log_name")
    parser.add_argument('-p', dest="profile")
    parser.add_argument('-t', dest="testid")
    parser.add_argument('-g', dest="group")
    parser.add_argument('-x', dest='exit', action='store_true')
    parser.add_argument(dest="config")
    cargs = parser.parse_args()

    cls_factories = {'': oper.factory}
    func_factory = func.factory
    FLOWS = parse_yaml_conf(cargs.yaml_flows, cls_factories, func_factory)

    CONF = importlib.import_module(cargs.config)

    if cargs.log_name:
        setup_logger(logger, cargs.log_name)
    else:
        setup_logger(logger)

    # Add own keys for signing/encrypting JWTs
    jwks, keyjar, kidd = build_keyjar(CONF.keys)

    # export JWKS
    p = urlparse(CONF.KEY_EXPORT_URL)
    f = open("." + p.path, "w")
    f.write(json.dumps(jwks))
    f.close()
    jwks_uri = p.geturl()

    kwargs = {"base_url": CONF.BASE, "kidd": kidd, "keyjar": keyjar,
              "jwks_uri": jwks_uri, "flows": FLOWS['Flows'], "conf": CONF,
              "cinfo": CONF.INFO, "order": FLOWS['Order'],
              "desc": FLOWS['Desc'], "profiles": profiles, "operation": oper,
              "profile": cargs.profile, "msg_factory": oic_message_factory,
              "check_factory": check.factory, "cache": {},
              'profile_handler': ProfileHandler}

    if cargs.testid:
        io = ClIO(**kwargs)
        sh = SessionHandler(**kwargs)
        sh.init_session(profile=cargs.profile)
        res = Result(sh, ProfileHandler)
        io.session = sh
        tester = ClTester(io, sh, **kwargs)
        tester.run(cargs.testid, **kwargs)
        res.store_test_info()
        res.print_info(cargs.testid)
    elif cargs.group:
        _sh = SessionHandler(**kwargs)
        _sh.init_session(profile=cargs.profile)

        for tid in _sh["flow_names"]:
            if not tid.startswith(cargs.group):
                continue
            io = ClIO(**kwargs)
            sh = SessionHandler(**kwargs)
            sh.init_session(profile=cargs.profile)
            io.session = sh
            tester = ClTester(io, sh, **kwargs)
            if not tester.match_profile(tid):
                continue
            elif tester.run(tid, **kwargs):
                print('+ {}'.format(tid))
            else:
                res = Result(sh, ProfileHandler)
                res.result()
                if cargs.exit:
                    break
    else:
        _sh = SessionHandler(**kwargs)
        _sh.init_session(profile=cargs.profile)

        for tid in _sh["flow_names"]:
            io = ClIO(**kwargs)
            sh = SessionHandler(**kwargs)
            sh.init_session(profile=cargs.profile)
            io.session = sh
            tester = ClTester(io, sh, **kwargs)
            if not tester.match_profile(tid):
                continue
            elif tester.run(tid, **kwargs):
                print('+ {}'.format(tid))
            else:
                res = Result(sh, ProfileHandler)
                res.result()
                if cargs.exit:
                    break
