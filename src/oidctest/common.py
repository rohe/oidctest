import argparse
import importlib
import json
import logging
import os
import sys
import time

from urlparse import urlparse
import aatest

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.keyio import build_keyjar

from aatest.verify import Verify
from oidctest.setup import test_summation

from oidctest.prof_util import map_prof

__author__ = 'roland'

logger = logging.getLogger(__name__)

class Trace(aatest.Trace):
    @staticmethod
    def format(resp):
        _d = {"claims": resp.to_dict()}
        if resp.jws_header:
            _d["jws header parameters"] = resp.jws_header
        if resp.jwe_header:
            _d["jwe header parameters"] = resp.jwe_header
        return _d

    def response(self, resp):
        delta = time.time() - self.start
        try:
            cl_name = resp.__class__.__name__
        except AttributeError:
            cl_name = ""

        if cl_name == "IdToken":
            txt = json.dumps({"id_token": self.format(resp)},
                             sort_keys=True, indent=2, separators=(',', ': '))
            self.trace.append("%f %s: %s" % (delta, cl_name, txt))
        else:
            try:
                dat = resp.to_dict()
            except AttributeError:
                txt = resp
                self.trace.append("%f %s" % (delta, txt))
            else:
                if cl_name == "OpenIDSchema":
                    cl_name = "UserInfo"
                    if resp.jws_header or resp.jwe_header:
                        dat = self.format(resp)
                elif "id_token" in dat:
                    dat["id_token"] = self.format(resp["id_token"])

                txt = json.dumps(dat, sort_keys=True, indent=2,
                                 separators=(',', ': '))

                self.trace.append("%f %s: %s" % (delta, cl_name, txt))


def setup_logger(log, log_file_name="rp.log"):
    #logger = logging.getLogger("")
    hdlr = logging.FileHandler(log_file_name)
    base_formatter = logging.Formatter(
        "%(asctime)s %(name)s:%(levelname)s %(message)s")

    hdlr.setFormatter(base_formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

def main_setup(log):
    from oidctest import profiles
    from oidctest import oper

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='flows')
    parser.add_argument('-l', dest="log_name")
    parser.add_argument('-p', dest="profile")
    parser.add_argument(dest="config")
    cargs = parser.parse_args()

    if "/" in cargs.flows:
        head, tail = os.path.split(cargs.flows)
        sys.path.insert(0, head)
        FLOWS = importlib.import_module(tail)
    else:
        FLOWS = importlib.import_module(cargs.flows)

    CONF = importlib.import_module(cargs.config)

    if cargs.log_name:
        setup_logger(log, cargs.log_name)
    else:
        setup_logger(log)

    # Add own keys for signing/encrypting JWTs
    try:
        jwks, keyjar, kidd = build_keyjar(CONF.keys)
    except KeyError:
        raise
    else:
        # export JWKS
        p = urlparse(CONF.KEY_EXPORT_URL)
        with open("." + p.path, "w") as f:
            f.write(json.dumps(jwks))
        jwks_uri = p.geturl()

    return {"base_url": CONF.BASE, "kidd": kidd,
            "jwks_uri": jwks_uri, "flows": FLOWS.FLOWS, "conf": CONF,
            "cinfo": CONF.INFO, "orddesc": FLOWS.ORDDESC,
            "profiles": profiles, "operations": oper,
            "profile": cargs.profile}

def make_client(**kw_args):
    _, _keyjar, _ = build_keyjar(kw_args["conf"].keys)
    _cli = Client(client_authn_method=CLIENT_AUTHN_METHOD, keyjar=_keyjar)
    _cli.kid = kw_args["kidd"]
    _cli.jwks_uri = kw_args["jwks_uri"]

    try:
        _cli_info = kw_args["conf"].INFO["client"]
    except KeyError:
        pass
    else:
        for arg, val in _cli_info.items():
            setattr(_cli, arg, val)

    return _cli


def make_list(flows, profile, **kw_args):
    f_names = flows.keys()
    f_names.sort()
    flow_names = []
    for k in kw_args["orddesc"]:
        k += '-'
        l = [z for z in f_names if z.startswith(k)]
        flow_names.extend(l)

    res = []
    sprofile = profile.split(".")
    for tid in flow_names:
        _flow = flows[tid]

        if map_prof(sprofile, _flow["profile"].split(".")):
            res.append(tid)

    return res

def node_dict(flows, lst):
    return dict([(l,flows[l]) for l in lst])


def run_flow(profiles, conv, test_id, conf, profile, chk_factory, index=0):
    print("=="+test_id)
    conv.test_id = test_id
    conv.conf = conf

    if index >= len(conv.flow["sequence"]):
        return None

    conv.index = index

    for item in conv.flow["sequence"][index:]:
        if isinstance(item, tuple):
            cls, funcs = item
        else:
            cls = item
            funcs = {}

        _oper = cls(conv, profile, test_id, conf, funcs, chk_factory)
        conv.operation = _oper
        _oper.setup(profiles.PROFILEMAP)
        _oper()

        conv.index += 1

    try:
        if conv.flow["tests"]:
            _ver = Verify(chk_factory, conv.msg_factory, conv)
            _ver.test_sequence(conv.flow["tests"])
    except KeyError:
        pass
    except Exception as err:
        raise

    info = test_summation(conv, test_id)

    return info