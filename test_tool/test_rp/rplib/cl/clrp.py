#!/usr/bin/env python
"""
Command line tool for testing the pyoidc RP library
"""
import importlib
import json
import logging
import argparse

from future.backports.urllib.parse import urlparse
from oic.oic import Client

from oic.utils.keyio import build_keyjar
from otest.aus.client import Factory
from otest.flow import RPFlow

from otest.common import setup_logger
from otest.io import ClIO
from otest.prof_util import prof2usage
from otest.result import Result, SIGN
from otest.flow import match_usage

from oidctest.op import func
from oidctest.op import check
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
                print('{} {}{}'.format(SIGN[_res], return_types, test_id))
            except Exception as err:
                print('****' + test_id + '*****')
                raise
            # res.store_test_info()
            # res.write_info(test_id)
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
    parser.add_argument('-p', dest="profile", action='append')
    parser.add_argument('-i', dest="id")
    parser.add_argument('-g', dest="group")
    parser.add_argument('-x', dest='exit', action='store_true')
    parser.add_argument(dest="config")
    cargs = parser.parse_args()

    cls_factories = {'': oper.factory}
    func_factory = func.factory

    FLOWS = RPFlow(cargs.flowsdir, cls_factories, func_factory)
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
            rtypes = FLOWS[cargs.test_id]['usage']['return_types']
        except KeyError:
            print('No such test ID')
            exit()

        if cargs.profile:
            # profile is of the form A.B.C.D.E
            # The first item represents the return_type
            rtypes = []
            for prof in cargs.profile:
                _use = prof2usage(prof)
                if not match_usage(FLOWS[cargs.test_id], **_use):
                    continue
                else:
                    rtypes.append(_use['return_type'])

        if len(rtypes) == 1:
            run_return_types(cargs.test_id, cargs.id, kwargs, rtypes)
        else:
            _res = run_return_types(cargs.test_id, cargs.id, kwargs, rtypes)
            if cargs.exit and _res is False:
                exit()
    else:
        if cargs.profile:
            rtypes = cargs.profile
        else:
            rtypes = PROFILES

        _sh = SessionHandler(**kwargs)
        _sh.init_session(profile=rtypes[0])

        if cargs.group:
            test_ids = [t for t in _sh["flow_names"] if
                        t.startswith(cargs.group)]
        else:
            test_ids = _sh["flow_names"]

        for tid in test_ids:
            _res = run_return_types(tid, cargs.id, kwargs, rtypes)
            if cargs.exit and _res is False:
                exit(-1)
