#!/usr/bin/env python3
import json

import argparse
import sys
import importlib

import requests
from fedoidc.bundle import JWKSBundle
from fedoidc.client import Client
from fedoidc.entity import FederationEntity
from oic.utils.keyio import build_keyjar
from oic.utils.keyio import KeyJar
from otest.flow import Flow

from requests.packages import urllib3
urllib3.disable_warnings()

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

_kj = build_keyjar(conf.KEY_DEFS)[1]

rp_fed_ent = FederationEntity(None, keyjar=_kj, iss='https://sunet.se/op',
                              signer=None, fo_bundle=jb)

for test_id in tests:
    _iss = "{}/{}/{}".format(conf.tool_url, conf.tester, test_id)
    _url = "{}/{}".format(_iss, ".well-known/openid-configuration")
    resp = requests.request('GET', _url, verify=False)

    rp = Client(federation_entity=rp_fed_ent)

    # Will raise an exception if there is no metadata statement I can use
    rp.parse_federation_provider_info(json.loads(resp.text), _iss)

    # If there are more the one metadata statement I can use
    # provider_federations will be set
    if rp.provider_federations:
        print(test_id, list(rp.provider_federations.keys()))
    else:  # Exactly one metadata statement I can use
        print(test_id, rp.federation)

