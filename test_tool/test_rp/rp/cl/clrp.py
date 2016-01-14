#!/usr/bin/env python

import importlib
import json
import logging
import os
import argparse
import sys
from future.backports.urllib.parse import urlparse

from oic.utils.keyio import build_keyjar

from aatest import exception_trace
from aatest.conversation import Conversation
from aatest.yamlcnf import parse_yaml_conf

from oidctest import func
from oidctest.common import make_list
from oidctest.common import make_client
from oidctest.common import setup_logger
from oidctest.common import run_flow
from oidctest.common import Trace
from oidctest.io import ClIO
from oidctest.tool import ClTester
from oidctest.session import SessionHandler

__author__ = 'roland'


logger = logging.getLogger("")


def main(flows, profile, profiles, **kw_args):
    try:
        redirs = kw_args["cinfo"]["client"]["redirect_uris"]
    except KeyError:
        redirs = kw_args["cinfo"]["registered"]["redirect_uris"]

    test_list = make_list(flows, profile, **kw_args)

    for tid in test_list:
        _flow = flows[tid]
        _cli = make_client(**kw_args)
        conversation = Conversation(_flow, _cli, redirs, kw_args["msg_factory"],
                                    trace_cls=Trace)
        # noinspection PyTypeChecker
        try:
            run_flow(profiles, conversation, tid, kw_args["conf"],
                     profile, kw_args["check_factory"])
        except Exception as err:
            exception_trace("", err, logger)
            print(conversation.trace)


if __name__ == '__main__':
    from oidctest import profiles
    from oidctest import oper
    from oic.oic.message import factory as oic_message_factory
    from oidctest.utils import get_check

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', dest='yaml_flows')
    parser.add_argument('-l', dest="log_name")
    parser.add_argument('-p', dest="profile")
    parser.add_argument('-t', dest="testid")
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
    f = open("."+p.path, "w")
    f.write(json.dumps(jwks))
    f.close()
    jwks_uri = p.geturl()

    kwargs = {"base_url": CONF.BASE, "kidd": kidd, "keyjar": keyjar,
              "jwks_uri": jwks_uri, "flows": FLOWS['Flows'], "conf": CONF,
              "cinfo": CONF.INFO, "order": FLOWS['Order'],
              "desc": FLOWS['Desc'], "profiles": profiles, "operation": oper,
              "profile": cargs.profile, "msg_factory": oic_message_factory,
              "check_factory": get_check, "cache": {}}

    if cargs.testid:
        io = ClIO(**kwargs)
        sh = SessionHandler({}, **kwargs)
        sh.init_session({}, profile=cargs.profile)
        tester = ClTester(io, sh, **kwargs)
        tester.run(cargs.testid, **kwargs)
        io.dump_log(sh.session, cargs.testid)
    else:
        _sh = SessionHandler({}, **kwargs)
        _sh.init_session({}, profile=cargs.profile)

        for tid in _sh.session["flow_names"]:
            io = ClIO(**kwargs)
            sh = SessionHandler({}, **kwargs)
            sh.init_session({}, profile=cargs.profile)
            tester = ClTester(io, sh, **kwargs)
            if not tester.match_profile(tid):
                continue
            elif tester.run(tid, **kwargs):
                print('+ {}'.format(tid))
            else:
                io.result(sh.session)
                if cargs.exit:
                    break
