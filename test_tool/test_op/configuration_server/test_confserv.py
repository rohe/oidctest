#!/usr/bin/env python3
import json
from urllib.parse import quote_plus

import requests

print('-------- get model C.T.T.T ------')
_response = requests.request('GET', 'http://localhost:9000/model/C.T.T.T')

print(_response.text)

print('-------- local modifications: issuer ------')
_info = json.loads(_response.text)
_info['tool']['issuer'] = 'https://example.com/op'
_part = quote_plus(_info['tool']['issuer'])

print('-------- Uploaded config ----------')
_response = requests.request('PUT',
                             'http://localhost:9000/{}/default'.format(_part),
                             data=json.dumps(_info))
_url = _response.text
print(_response.status_code)
print('URL:', _url)
print('-------- Downloaded config ----------')
_resp = requests.request('GET', _url)
print(_resp.text)

_info = json.loads(_resp.text)
print('-------- local modifications: enc, sig ------')
_info['tool'].update({'enc':True, 'sig': True})

print('-------- uploaded modifications -------')
_response = requests.request('POST', _url, data=json.dumps(_info))
print(_response.status_code, _response.text)

print('-------- Downloaded config ----------')
_resp = requests.request('GET', _url)
print(_resp.status_code, _resp.text)

print('-------- deleting config ----------')
_resp = requests.request('DELETE', _url)
print(_resp.status_code, _resp.text)

print('-------- Downloaded not existing config ----------')
_resp = requests.request('GET', _url)
print(_resp.status_code, _resp.text)
