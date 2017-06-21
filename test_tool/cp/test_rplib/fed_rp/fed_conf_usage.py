TOOL_ISS = 'https://localhost'

FO = {'swamid': 'https://swamid.sunet.se',
      'surfnet': 'https://surfnet.nl/oidc',
      'feide': 'https://www.feide.no',
      'edugain': 'https://edugain.com',
      'example.com': 'https://example.com'}

OA = {'sunet': 'https://sunet.se', 'uninett': 'https://uninett.no',
      'example.org': 'https://example.org',
      'bogus.example.org': 'https://bogus.example.org'}

IA = {'cs.example.org': 'https://cs.example.org'}

EO = {'sunet.op': 'https://sunet.se/op',
      'example.org.op': 'https://example.org/op'}

BASE = {'sunet.op': EO['sunet.op']}

SMS_DEF = {
    OA['sunet']: {
        "discovery": {
            FO['swamid']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['swamid'], 'uri': False},
            ],
            FO['feide']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['feide'], 'uri': False},
            ],
            FO['surfnet']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['surfnet'], 'uri': False},
            ],
            FO['edugain']: [
                {'request': {}, 'requester': FO['swamid'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['edugain'], 'uri': True},
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {}, 'signer': FO['swamid'], 'uri': False}
            ]
        },
        "registration": {
            FO['swamid']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'registration'},
                 'signer': FO['swamid'], 'uri': False},
            ],
            FO['feide']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'registration'},
                 'signer': FO['feide'], 'uri': False},
            ],
            FO['surfnet']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'registration'},
                 'signer': FO['surfnet'], 'uri': False},
            ],
            FO['edugain']: [
                {'request': {}, 'requester': FO['swamid'],
                 'signer_add': {'federation_usage': 'registration'},
                 'signer': FO['edugain'], 'uri': True},
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {}, 'signer': FO['swamid'], 'uri': False}
            ]
        },
        "response": {
            FO['swamid']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['swamid'], 'uri': False},
            ],
            FO['feide']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['feide'], 'uri': False},
            ],
            FO['surfnet']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['surfnet'], 'uri': False},
            ],
            FO['edugain']: [
                {'request': {}, 'requester': FO['swamid'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['edugain'], 'uri': True},
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {}, 'signer': FO['swamid'], 'uri': False}
            ]
        }
    },
    OA['uninett']: {
        "discovery": {
            FO['feide']: [
                {'request': {}, 'requester': OA['uninett'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['feide'], 'uri': False},
            ]
        },
        "response": {
            FO['feide']: [
                {'request': {}, 'requester': OA['uninett'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['feide'], 'uri': False},
            ]
        }
    },
    OA['example.org']: {
        "discovery": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {
                     'scopes_supported': ['openid', 'mail'],
                     'federation_usage': 'discovery'},
                 'signer': FO['example.com'], 'uri': False}
            ]
        },
        "response": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['example.com'], 'uri': False},
            ]
        }
    },
    IA['cs.example.org']: {
        "discovery": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {
                     'scopes_supported': ['openid', 'email'],
                     'federation_usage': 'discovery'},
                 'signer': FO['example.com'], 'uri': False},
                {'request': {
                    'scopes_supported': ["openid", "profile", "email",
                                         "address",
                                         "phone", "offline_access"]},
                    'requester': IA['cs.example.org'],
                    'signer_add': {}, 'signer': OA['example.org'], 'uri': False}
            ]
        },
        "response": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {'federation_usage': 'response'},
                 'signer': FO['example.com'], 'uri': False},
                {'request': {}, 'requester': IA['cs.example.org'],
                 'signer_add': {}, 'signer': OA['example.org'], 'uri': False}
            ]
        }
    },
    OA['bogus.example.org']: {
        "discovery": {}
    }
}

KEY_DEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]
