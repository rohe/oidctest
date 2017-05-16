#!/usr/bin/env python3
import importlib
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from fedoidc.bundle import FSJWKSBundle
from fedoidc.operator import Operator
from fedoidc.test_utils import make_signed_metadata_statement_uri
from fedoidc.test_utils import MetaDataStore

sys.path.insert(0, ".")
config = importlib.import_module(sys.argv[1])

jb = FSJWKSBundle(config.TOOL_ISS, None, 'fo_jwks',
                  key_conv={'to': quote_plus, 'from': unquote_plus})
jb.bundle.sync()

operator = {}

for entity, _keyjar in jb.items():
    operator[entity] = Operator(iss=entity, keyjar=_keyjar)


mds = MetaDataStore('mds_uri')
mds.reset()

base_url = '{}/mds_uri/'.format(config.TOOL_ISS)

for iss, sms_def in config.SMS_DEF.items():
    for context, spec in sms_def.items():
        for fo, _desc in spec.items():
            res = make_signed_metadata_statement_uri(_desc, operator, mds,
                                                     base_url)
