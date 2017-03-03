TOOL_ISS = 'https://localhost'

FO = {'swamid': 'https://swamid.sunet.se',
      'surfnet': 'https://surfnet.nl/oidc',
      'feide': 'https://www.feide.no'}

OA = {
    'uninett': 'https://www.uninett.no',
    'umu': 'https://adm.umu.se/',
    'sunet':'https://sunet.se/',
    'example': 'https://adm.example.com/'
}

LO = {
    'umu.its': 'https://its.umu.se',
    'example.ops': 'https://ops.example.com'
}

EO = {
    'foodle': 'https://foodle.uninett.no',
    'cambro': 'https://cambro.umu.se',
    'connect': 'https://connect.sunet.se',
    'box': 'https://box.example.com'
    }

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
    'D': {'redirect_uris': 'https://rp.example.com/auth_cb'},
    'E': {'tos_uri': 'https://inter.example.com/tos.html'},
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

SMS_DEF = [
    [
        {'request': {'contacts': 'info@example.com'},
         'requester': OA['example'],
         'signer_add': {}, 'signer': FO['swamid']},
        {'request': {'scope': ['openid', 'email']},
         'requester': EO['box'],
         'signer_add': {}, 'signer': OA['example']}
    ],
    # [
    #     [{'request': POLICY['C'], 'requester': ORG['example']['OA'],
    #       'signer_add': {}, 'signer': FO[1]},
    #      {'request': POLICY['C'], 'requester': ORG['example']['OA'],
    #       'signer_add': {}, 'signer': FO[0]}
    #      ],
    #     {'request': POLICY['F'], 'requester': ORG['example']['EO'][0],
    #      'signer_add': {}, 'signer': ORG['example']['OA']}
    # ],
    # [
    #     [{'request': {}, 'requester': ORG['uninett']['OA'],
    #       'signer_add': POLICY['G'], 'signer': FO[2]},
    #      {'request': {}, 'requester': ORG['uninett']['OA'],
    #       'signer_add': POLICY['H'], 'signer': FO[0]}],
    #     {'request': {"redirect_uris": ['https://foodle.uninett.no/callback'],
    #                  "application_type": 'web',
    #                  "response_types": ['code'],
    #                  "signed_jwks_uri": 'https://foodle.uninett.no/jwks.jws'},
    #      'requester': ORG['uninett']['EO'][0], 'signer_add': {},
    #      'signer': ORG['uninett']['OA']
    #      }
    # ]
]
