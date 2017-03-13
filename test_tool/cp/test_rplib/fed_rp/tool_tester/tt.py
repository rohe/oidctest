#!/usr/bin/env python3
import argparse
import json
import requests

from fedoidc import ProviderConfigurationResponse
from fedoidc.bundle import JWKSBundle
from fedoidc.client import Client
from fedoidc.entity import FederationEntity

from oic.utils.keyio import build_keyjar
from oic.utils.keyio import KeyJar

from otest.flow import Flow

from requests.packages import urllib3
urllib3.disable_warnings()

# ----- config -------
tool_url = "https://agaton-sax.com:8080"
tester = 'dummy'
KEY_DEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
]
# --------------------

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='flowsdir', required=True)
parser.add_argument('-k', dest='insecure', action='store_true')
parser.add_argument('-t', dest='tester')
parser.add_argument(dest="config")
args = parser.parse_args()

_flows = Flow(args.flowsdir, profile_handler=None)
tests = _flows.keys()

# Get the necessary information about the JWKS bundle
info = {}
for path in ['bundle', 'bundle/signer', 'bundle/sigkey']:
    _url = "{}/{}".format(tool_url, path)
    resp = requests.request('GET', _url, verify=False)
    info[path] = resp.text

# Create a KeyJar instance that contains the key that the bundle was signed with
kj = KeyJar()
kj.import_jwks(json.loads(info['bundle/sigkey']), info['bundle/signer'])

# Create a JWKSBundle instance and load it with the keys in the bundle
# I got from the tool
jb = JWKSBundle('')
jb.upload_signed_bundle(info['bundle'], kj)

# This is for the federation entity to use when signing something
# like the keys at jwks_uri.
_kj = build_keyjar(KEY_DEFS)[1]

# A federation aware RP includes a FederationEntity instance.
# This is where it is instantiated
rp_fed_ent = FederationEntity(None, keyjar=_kj, iss='https://sunet.se/rp',
                              signer=None, fo_bundle=jb)

# And now for running the tests
for test_id in tests:
    _iss = "{}/{}/{}".format(tool_url, tester, test_id)
    _url = "{}/{}".format(_iss, ".well-known/openid-configuration")
    resp = requests.request('GET', _url, verify=False)

    rp = Client(federation_entity=rp_fed_ent)

    # Will raise an exception if there is no metadata statement I can use
    rp.handle_response(resp, _iss, rp.parse_federation_provider_info,
                       ProviderConfigurationResponse)

    # If there are more the one metadata statement I can use
    # provider_federations will be set and will contain a dictionary
    # keyed on FO identifier
    if rp.provider_federations:
        print(test_id, list(rp.provider_federations.keys()))
    else:  # Otherwise there should be exactly one metadata statement I can use
        print(test_id, rp.federation)
