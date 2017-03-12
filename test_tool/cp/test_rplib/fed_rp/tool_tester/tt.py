#!/usr/bin/env python3
import json

import argparse
import sys
import importlib

import requests
from fedoidc.bundle import JWKSBundle
from fedoidc.operator import Operator
from oic.utils.keyio import KeyJar
from otest.flow import Flow

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='flowsdir', required=True)
parser.add_argument('-k', dest='insecure', action='store_true')
parser.add_argument('-t', dest='tester')
parser.add_argument(dest="config")
args = parser.parse_args()

_flows = Flow(args.flowsdir, profile_handler=None)
tests = _flows.keys()

sys.path.insert(0, ".")
conf = importlib.import_module(args.config)

info = {}

for path in ['bundle', 'bundle/signer', 'bundle/sigkey']:
    _url = "{}/{}".format(conf.tool_url, path)
    resp = requests.request('GET', _url, verify=False)
    info[path] = resp.text

kj = KeyJar()
kj.import_jwks(json.loads(info['bundle/sigkey']), info['bundle/signer'])

jb = JWKSBundle('')
jb.upload_signed_bundle(info['bundle'], kj)

fed_operator = Operator(jwks_bundle=jb)

for test_id in tests:
    _url = "{}/{}/{}/{}".format(conf.tool_url, conf.tester, test_id,
                                ".well-known/openid-configuration")
    resp = requests.request('GET', _url, verify=False)
