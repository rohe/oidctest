#!/usr/bin/env python
"""
Command line tool for testing the pyoidc RP library
"""
import importlib
import json
import logging
import argparse

from future.backports.urllib.parse import urlparse

from oic.utils.keyio import build_keyjar

from otest.parse_cnf import parse_yaml_conf
from otest.common import setup_logger
from otest.io import ClIO
from otest.result import Result

from oidctest.op import func
from oidctest.op import check
from oidctest.op.prof_util import SimpleProfileHandler
from oidctest.op.tool import ClTester
from oidctest.session import SessionHandler
from oidctest.rp.test_config import PROFILES

try:
    from requests.packages import urllib3
except ImportError:
    pass
else:
    urllib3.disable_warnings()

__author__ = 'roland'

logger = logging.getLogger("")


def get_return_types(spec):
    if spec == '*':
        return PROFILES
    else:
        return [x for x in spec.split(',') if x in PROFILES]


def run_return_types(test_id, oper_id, kwargs, return_types, single=True):
    for rtyp in return_types:
        kwargs['profile'] = rtyp
        kwargs['opid'] = oper_id + '_' + rtyp

        sh = SessionHandler(**kwargs)
        sh.init_session(profile=rtyp)

        res = Result(sh, SimpleProfileHandler)

        io = ClIO(**kwargs)
        io.session = sh

        tester = ClTester(io, sh, **kwargs)

        if single:
            tester.run(test_id, **kwargs)

            res.store_test_info()
            res.print_info(test_id)
            return True
        else:
            if not tester.match_profile(test_id):
                continue
            elif tester.run(test_id, **kwargs):
                print('+ {}'.format(test_id))
                return True
            else:
                res = Result(sh, SimpleProfileHandler)
                res.result()
                return False


if __name__ == '__main__':
    from oic.oic.message import factory as oic_message_factory

    from oidctest.op import profiles
    from oidctest.op import oper

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', dest='yaml_flows')
    parser.add_argument('-l', dest="log_name")
    parser.add_argument('-t', dest="test_id")
    parser.add_argument('-p', dest="profile")
    parser.add_argument('-i', dest="id")
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
              "msg_factory": oic_message_factory,
              "check_factory": check.factory, "cache": {},
              'profile_handler': SimpleProfileHandler}

    if cargs.profile:
        rtypes = [cargs.profile]
    else:
        rtypes = ['C']

    if cargs.test_id:
        try:
            rtypes = get_return_types(FLOWS['Flows'][cargs.test_id]['profile'])
        except KeyError:
            print('No such test ID')
            exit()

        if len(rtypes) == 1:
            run_return_types(cargs.test_id, cargs.id, kwargs,
                             return_types=rtypes)
        else:
            _res = run_return_types(cargs.test_id, cargs.id, kwargs, rtypes,
                                    False)
            if cargs.exit and _res is False:
                exit()
    else:
        _sh = SessionHandler(**kwargs)
        _sh.init_session(profile=rtypes[0])

        if cargs.group:
            test_ids = [t for t in _sh["flow_names"] if
                        t.startswith(cargs.group)]
        else:
            test_ids = _sh["flow_names"]

        for tid in test_ids:
            _res = run_return_types(tid, cargs.id, kwargs, rtypes, False)
            if cargs.exit and _res is False:
                exit(-1)
