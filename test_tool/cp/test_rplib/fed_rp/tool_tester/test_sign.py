import json
import requests
from urllib.parse import urlencode

from jwkest import as_unicode
from jwkest.jws import factory, JWS
from oic.utils.keyio import KeyJar

req = {"redirect_uris": ["https://www.example.org"]}

FO = {'swamid': 'https://swamid.sunet.se',
      'surfnet': 'https://surfnet.nl/oidc',
      'feide': 'https://www.feide.no',
      'edugain': 'https://edugain.com',
      'example.com': 'https://example.com'}


def bundle2keyjar():
    url = 'https://localhost:8080/bundle'
    r = requests.get(url, verify=False)
    assert r.status_code == 200
    _bundle = r.text

    url = 'https://localhost:8080/bundle/sigkey'
    r = requests.get(url, verify=False)
    assert r.status_code == 200
    _sigkey_jwks = json.loads(as_unicode(r.text))

    kj = KeyJar()
    kj.import_jwks(_sigkey_jwks, '')

    _ver_bundle = JWS().verify_compact(_bundle, kj.get_verify_key())

    jwks_dir = _ver_bundle['bundle']
    for iss, jwks in jwks_dir.items():
        kj.import_jwks(jwks, iss)

    return kj

if __name__ == '__main__':
    keyjar = bundle2keyjar()

    for fo in ['swamid', 'surfnet', 'feide', 'edugain', 'example.com' ]:
        qp = urlencode({'signer': FO[fo], 'context': 'registration'})
        url = 'https://localhost:8080/sign?{}'.format(qp)
        r = requests.post(url, json.dumps(req), verify = False)
        assert r.status_code == 200
        _jw = factory(r.text)

        # Just checking the issuer ID *not* verifying the Signature
        body = json.loads(as_unicode(_jw.jwt.part[1]))
        assert body['iss'] == FO[fo]

        try:
            msg = _jw.verify_compact(r.text,
                                     keyjar.get_verify_key(owner=FO[fo]))
        except AssertionError:
            print('{} - NOT OK'.format(FO[fo]))
        else:
            print('{} - OK'.format(FO[fo]))

