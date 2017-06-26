import json
import requests

from jwkest import as_unicode
from jwkest.jws import JWS
from oic.utils.keyio import KeyJar

url = 'https://localhost:8080/bundle'
r = requests.get(url, verify = False)
assert r.status_code == 200
_bundle = r.text

url = 'https://localhost:8080/bundle/sigkey'
r = requests.get(url, verify = False)
assert r.status_code == 200
_sigkey_jwks = json.loads(as_unicode(r.text))

kj = KeyJar()
kj.import_jwks(_sigkey_jwks, '')

_ver_bundle = JWS().verify_compact(_bundle, kj.get_verify_key())

print(_ver_bundle)