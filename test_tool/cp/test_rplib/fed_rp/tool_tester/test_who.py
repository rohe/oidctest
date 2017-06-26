import json

import requests

r = requests.get('https://localhost:8080/who', verify=False)
assert r.status_code == 200
fo_list = json.loads(r.text)
print(fo_list)
assert set(fo_list) == {'https://swamid.sunet.se', 'https://surfnet.nl/oidc',
                        'https://www.feide.no', 'https://example.com',
                        'https://edugain.com'}
