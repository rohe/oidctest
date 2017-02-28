import importlib
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from fedoidc import MetadataStatement
from fedoidc.bundle import FSJWKSBundle
from fedoidc.bundle import keyjar_to_jwks_private
from fedoidc.operator import Operator

sys.path.insert(0, ".")
config = importlib.import_module('sms_conf')


def make_ms(desc, ms, root, leaf, operator):
    req = MetadataStatement(**desc['request'])
    _requester = operator[desc['requester']]
    req['signing_keys'] = _requester.signing_keys_as_jwks()
    if ms:
        if isinstance(ms, list):
            req['metadata_statements'] = ms[:]
        else:
            req['metadata_statements'] = [ms[:]]
    req.update(desc['signer_add'])

    if leaf:
        jwt_args = {'aud': [_requester.iss]}
    else:
        jwt_args = {}

    _signer = operator[desc['signer']]
    ms = _signer.pack_metadata_statement(req, jwt_args=jwt_args)
    if root is True:
        _fo = _signer.iss
    else:
        _fo = ''

    return ms, _fo


def make_signed_metadata_statements(smsdef, operator):
    res = []

    for ms_chain in smsdef:
        _ms = []
        depth = len(ms_chain)
        i = 1
        _fo = []
        _root_fo = []
        root = True
        leaf = False
        for desc in ms_chain:
            if i == depth:
                leaf = True
            if isinstance(desc, dict):
                _ms, _fo = make_ms(desc, _ms, root, leaf, operator)
            else:
                _mss = []
                _fos = []
                for d in desc:
                    _m, _f = make_ms(d, _ms, root, leaf, operator)
                    _mss.append(_m)
                    if _f:
                        _fos.append(_f)
                _ms = _mss
                if _fos:
                    _fo = _fos
            if root:
                _root_fo = _fo
            root = False
            i += 1

        res.append({'fo':_root_fo, 'ms':_ms})
    return res


if __name__ == "__main__":
    jb = FSJWKSBundle(config.TOOL_ISS, None, 'fo_jwks',
                          key_conv={'to': quote_plus, 'from': unquote_plus})

    # Need to save the private parts
    jb.bundle.value_conv['to'] = keyjar_to_jwks_private
    jb.bundle.sync()

    operator = {}

    for entity, _keyjar in jb.items():
        operator[entity] = Operator(iss=entity, keyjar=_keyjar)

    for sms in make_signed_metadata_statements(config.SMSDEF, operator):
        print(sms['fo'], sms['ms'])
