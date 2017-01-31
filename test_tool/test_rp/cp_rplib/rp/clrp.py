#!/usr/bin/env python3
import json
import random
from oic.federation import MetadataStatement
from oic.federation.bundle import JWKSBundle
from oic.federation.bundle import verify_signed_bundle
from oic.federation.operator import Operator
from oic.utils.jwt import JWT
from oic.utils.keyio import build_keyjar
from oic.utils.keyio import KeyJar
import requests

__author__ = 'roland'

tt = 'http://localhost:8080'

# first get the bundle signers public key

r = requests.request('GET', tt+'/bundle/signer')
signer = r.text
r = requests.request('GET', tt+'/bundle/sigkey')
sig_key = r.text

bundle_sigkey = KeyJar()
bundle_sigkey.import_jwks(json.loads(sig_key), signer)

# fetch bundle

r = requests.request('GET', tt+'/bundle')
_bundle = JWKSBundle('me')
_bundle.loads(verify_signed_bundle(r.text, bundle_sigkey)['bundle'])

# Own key

jwks, keyj, kids = build_keyjar([{"type": "RSA", "key": '', "use": ["sig"]}])

statement = MetadataStatement(
    contacts=['dev_admin@example.com'],
    policy_uri='https://example.com/policy.html',
    tos_uri='https://example.com/tos.html',
    logo_uri='https://example.com/logo.jpg',
    signing_keys=jwks
)

data = json.dumps(statement.to_dict())

# pick federation Operator

r = requests.request('GET', tt+'/who')
available = json.loads(r.text)

bundle_keys = list(_bundle.keys())
# assert set(available) == bundle_keys
# bundle.keys() subset of available, one extra in available 'the signer'

# pick one at random

i = random.randint(0, len(bundle_keys)-1)

fo_iss = bundle_keys[i]

r = requests.request('POST', tt+'/sign?fo='+fo_iss, data=data)

_jwt = JWT(_bundle[fo_iss])
verf = _jwt.unpack(r.text)

assert verf
