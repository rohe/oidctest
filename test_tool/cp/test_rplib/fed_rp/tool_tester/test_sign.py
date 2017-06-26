import json
import requests
from urllib.parse import urlencode

from jwkest import as_unicode
from jwkest.jws import factory

req = {"redirect_uris": ["https://www.example.org"]}

qp = urlencode({'signer': 'https://surfnet.nl/oidc', 'context': 'registration'})
url = 'https://localhost:8080/sign?{}'.format(qp)
r = requests.post(url, json.dumps(req), verify = False)
assert r.status_code == 200
_jw = factory(r.text)

body = json.loads(as_unicode(_jw.jwt.part[1]))
assert body['iss'] == 'https://surfnet.nl/oidc'