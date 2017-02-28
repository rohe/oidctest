TOOL_ISS = 'https://localhost'

FO = ['https://swamid.sunet.se', 'https://surfnet.nl/oidc',
      'https://www.feide.no']

ORG = {
    'uninett': {
        'OA': 'https://www.uninett.no',
        'EO': ['https://foodle.uninett.no']
    },
    'umu': {
        'OA': 'https://adm.umu.se/',
        'LO': ['https://its.umu.se'],
        'EO': ['https://its.umu.se/sysadm']
    },
    'sunet': {
        'OA': 'https://sunet.se/',
        'EO': ['https://sunet.se/sysadm']
    },
    'example': {
        'OA': 'https://adm.example.com/',
        'LO': ['https://org.example.com/', 'https://ou.org.example.com/'],
        'EO': ['https://ou.org.example.com/sysadm']
    }}

POLICY = {
    'A': {
        "response_types": ["code", "id_token", "token"],
        "token_endpoint_auth_method": "private_key_jwt",
        "scopes": ['openid', 'email', 'phone']
    },
    'B': {
        "response_types": ["code", "token"],
        "token_endpoint_auth_method": "private_key_jwt",
        "scopes": ['openid', 'email']
    },
    'C': {'contacts': 'info@example.com'},
    'D': {'redirect_uris': 'https://rp.example.com/auth_cb'},
    'E': {'tos_uri': 'https://inter.example.com/tos.html'},
    'F': {'scope': ['openid', 'email']},
    'G': {
        'id_token_signing_alg_values_supported': ['RS256', 'RS512'],
        'claims': ['sub', 'name', 'email', 'picture']
    },
    'H': {
        "response_types": ["code", "token"],
        "token_endpoint_auth_method": "private_key_jwt",
        "scopes": ['openid', 'email']
    }
}

SMSDEF = [
    [
        {'request': POLICY['C'], 'requester': ORG['example']['OA'],
         'signer_add': {}, 'signer': FO[1]},
        {'request': POLICY['F'], 'requester': ORG['example']['EO'][0],
         'signer_add': {}, 'signer': ORG['example']['OA']}
    ],
    [
        [{'request': POLICY['C'], 'requester': ORG['example']['OA'],
          'signer_add': {}, 'signer': FO[1]},
         {'request': POLICY['C'], 'requester': ORG['example']['OA'],
          'signer_add': {}, 'signer': FO[0]}
         ],
        {'request': POLICY['F'], 'requester': ORG['example']['EO'][0],
         'signer_add': {}, 'signer': ORG['example']['OA']}
    ],
    [
        [{'request': {}, 'requester': ORG['uninett']['OA'],
          'signer_add': POLICY['G'], 'signer': FO[2]},
         {'request': {}, 'requester': ORG['uninett']['OA'],
          'signer_add': POLICY['H'], 'signer': FO[0]}],
        {'request': {"redirect_uris": ['https://foodle.uninett.no/callback'],
                     "application_type": 'web',
                     "response_types": ['code'],
                     "signed_jwks_uri": 'https://foodle.uninett.no/jwks.jws'},
         'requester': ORG['uninett']['EO'][0], 'signer_add': {},
         'signer': ORG['uninett']['OA']
         }
    ]
]
