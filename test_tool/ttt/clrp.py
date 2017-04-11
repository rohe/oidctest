#!/usr/bin/env python3
"""
Command line tool for testing the pyoidc RP library
"""
from future.backports.urllib.parse import urlparse

import argparse
import importlib
import json
import logging

from oic.oic import Client
from oic.utils.keyio import build_keyjar
from otest.aus.client import Factory
from otest.common import setup_logger
from otest.flow import FlowState
from otest.flow import RPFlow
from otest.flow import match_usage
from otest.io import ClIO
from otest.prof_util import prof2usage
from otest.result import SIGN
from otest.result import Result

from oidctest.op import check
from oidctest.op import func
from oidctest.prof_util import SimpleProfileHandler
from oidctest.session import SessionHandler
from oidctest.tool import ClTester

try:
    from requests.packages import urllib3
except ImportError:
    pass
else:
    urllib3.disable_warnings()

__author__ = 'roland'

logger = logging.getLogger("")

PROFILES = ["C", "CI", "CT", "CIT", "I", "IT"]


def get_return_types(spec):
    if spec == '*':
        return PROFILES
    else:
        return [x for x in spec.split(',') if x in PROFILES]


def run_return_types(test_id, oper_id, kwargs, return_types):
    if len(return_types) == 1:
        single = True
    else:
        single = False

    for rtyp in return_types:  # One return_type at the time
        kwargs['profile'] = rtyp
        kwargs['opid'] = oper_id + '_' + rtyp
        kwargs['tool_conf']['tag'] = kwargs['opid']

        sh = SessionHandler(**kwargs)
        sh.init_session()

        # res = Result(sh, SimpleProfileHandler)

        io = ClIO(**kwargs)
        io.session = sh

        tester = ClTester(io, sh, **kwargs)

        if single:
            _res = tester.run(test_id, **kwargs)
            try:
                print('{} [{}] {}'.format(SIGN[_res], rtyp, test_id))
            except Exception as err:
                print('****' + test_id + '*****')
                raise
            # res.store_test_info()
            # res.write_info(test_id)
            # sh.test_flows.store_test_info(tester)
            return True
        else:
            if not tester.match_profile(test_id):
                continue
            elif tester.run(test_id, **kwargs):
                print('+ [{}] {}'.format(rtyp, test_id))
            else:
                sh.test_flows.store_test_info(tester)
                return False


ORDER = [
    "OP-Response", "OP-IDToken", "OP-UserInfo", "OP-nonce", "OP-scope",
    "OP-display", "OP-prompt", "OP-Req", "OP-OAuth", "OP-redirect_uri",
    "OP-ClientAuth", "OP-Discovery", "OP-Registration", "OP-Rotation",
    "OP-request_uri", "OP-request", "OP-claims"]

if __name__ == '__main__':
    from oic.oic.message import factory as oic_message_factory

    from oidctest.op import profiles
    from oidctest.op import oper

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='flowsdir')
    parser.add_argument('-k', dest="insecure", action='store_true')
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

    FLOWS = FlowState(cargs.flowsdir, SimpleProfileHandler,
                      cls_factories, func_factory, [])
    CONF = importlib.import_module(cargs.config)

    if cargs.log_name:
        setup_logger(logger, cargs.log_name)
    else:
        setup_logger(logger)

    # Add own keys for signing/encrypting JWTs
    jwks, keyjar, kidd = build_keyjar(CONF.KEYS)

    # export JWKS
    p = urlparse(CONF.KEY_EXPORT_URL)
    f = open("." + p.path, "w")
    f.write(json.dumps(jwks))
    f.close()
    jwks_uri = p.geturl()

    _client_info = CONF.CLIENT
    _client_info.update(
        {
            "base_url": CONF.BASE, "kidd": kidd, "keyjar": keyjar,
            "jwks_uri": jwks_uri,
        })
    if cargs.insecure:
        _client_info['verify_ssl'] = False

    kwargs = {
        "flows": FLOWS, "conf": CONF, "client_info": _client_info,
        "profiles": profiles, "operation": oper, 'order': ORDER,
        "msg_factory": oic_message_factory, "check_factory": check.factory,
        "cache": {}, 'profile_handler': SimpleProfileHandler,
        'client_factory': Factory(Client), 'tool_conf': CONF.TOOL
    }

    if cargs.test_id:
        rtypes = []
        try:
            rtypes = FLOWS[cargs.test_id]['usage']['return_type']
        except KeyError:
            print('No such test ID')
            exit()

        if cargs.profile:
            # profile is of the form A.B.C.D.E
            # The first item represents the return_type
            rtypes = []
            _use = prof2usage(cargs.profile)
            _use['return_type'] = _use['return_type'][0]
            if match_usage(FLOWS[cargs.test_id], **_use):
                rtypes.append(_use['return_type'])

        if len(rtypes) == 1:
            run_return_types(cargs.test_id, cargs.id, kwargs, rtypes)
        else:
            _res = run_return_types(cargs.test_id, cargs.id, kwargs, rtypes)
            if cargs.exit and _res is False:
                exit()
    else:
        if cargs.profile:
            rtypes = [cargs.profile]
        else:
            rtypes = PROFILES

        _sh = SessionHandler(**kwargs)
        _sh.init_session(profile=rtypes[0])

        if cargs.group:
            test_ids = [t for t in _sh["tests"] if
                        t.startswith(cargs.group)]
        else:
            test_ids = _sh["tests"]

        for tid in test_ids:
            _res = run_return_types(tid, cargs.id, kwargs, rtypes)
            if cargs.exit and _res is False:
                exit(-1)
