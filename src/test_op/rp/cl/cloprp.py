#!/usr/bin/env python

import importlib
import json
import logging
import os
import argparse
import sys

from urlparse import urlparse

from oic.utils.authn.client import BearerHeader
from oic.utils.keyio import build_keyjar

from aatest import NotSupported, exception_trace
from aatest import ConfigurationError
from aatest.conversation import Conversation
from oidctest.common import make_list
from oidctest.common import make_client
from oidctest.common import setup_logger
from oidctest.common import run_flow
from oidctest.common import Trace

__author__ = 'roland'


logger = logging.getLogger("")


def get_claims(client):
    resp = {}
    for src in client.userinfo["_claim_names"].values():
        spec = client.userinfo["_claim_sources"][src]
        ht_args = BearerHeader(client).construct(**spec)

        try:
            part = client.http_request(spec["endpoint"], "GET", **ht_args)
        except Exception:
            raise
        resp.update(json.loads(part.content))

    return resp


def endpoint_support(client, endpoint):
    if endpoint in client.provider_info:
        return True
    else:
        return False


def run_func(spec, conv, req_args):
    if isinstance(spec, tuple):
        func, args = spec
    else:
        func = spec
        args = {}

    try:
        req_args = func(req_args, conv, args)
    except KeyError as err:
        conv.trace.error("function: %s failed" % func)
        conv.trace.error(str(err))
        raise NotSupported
    except ConfigurationError:
        raise
    else:
        return req_args


def run_one(test_id, flows, profile, profiles, **kw_args):
    try:
        redirs = kw_args["cinfo"]["client"]["redirect_uris"]
    except KeyError:
        redirs = kw_args["cinfo"]["registered"]["redirect_uris"]

    _flow = flows[test_id]
    _cli = make_client(**kw_args)
    conversation = Conversation(_flow, _cli, redirs, kw_args["msg_factory"],
                                interaction=kw_args["conf"].INTERACTION,
                                trace_cls=Trace)
    # noinspection PyTypeChecker
    try:
        run_flow(profiles, conversation, test_id, kw_args["conf"],
                 profile, kw_args["check_factory"])
    except Exception as err:
        exception_trace("", err, logger)
        print conversation.trace


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
                                    interaction=kw_args["conf"].INTERACTION,
                                    trace_cls=Trace)

        # noinspection PyTypeChecker
        try:
            run_flow(profiles, conversation, tid, kw_args["conf"],
                     profile, kw_args["check_factory"])
        except Exception as err:
            exception_trace("", err, logger)
            print conversation.trace


if __name__ == '__main__':
    from oidctest import profiles
    from oidctest import oper
    from oic.oic.message import factory as oic_message_factory
    from oidctest.check import factory as check_factory

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='flows')
    parser.add_argument('-l', dest="log_name")
    parser.add_argument('-p', dest="profile")
    parser.add_argument('-t', dest="testid")
    parser.add_argument(dest="config")
    cargs = parser.parse_args()

    if "/" in cargs.flows:
        head, tail = os.path.split(cargs.flows)
        sys.path.insert(0, head)
        if tail.endswith(".py"):
            tail = tail[:-3]
        FLOWS = importlib.import_module(tail)
    else:
        FLOWS = importlib.import_module(cargs.flows)

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
              "jwks_uri": jwks_uri, "flows": FLOWS.FLOWS, "conf": CONF,
              "cinfo": CONF.INFO, "orddesc": FLOWS.ORDDESC,
              "profiles": profiles, "operations": oper,
              "profile": cargs.profile, "msg_factory": oic_message_factory,
              "check_factory": check_factory}

    if cargs.testid:
        run_one(cargs.testid, **kwargs)
    else:
        main(**kwargs)