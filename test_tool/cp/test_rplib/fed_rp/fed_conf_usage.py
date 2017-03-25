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
                 'signer_add': {'usage': 'discovery'},
                 'signer': FO['swamid']},
            ],
            FO['feide']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'usage': 'discovery'},
                 'signer': FO['feide']},
            ],
            FO['surfnet']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'usage': 'discovery'},
                 'signer': FO['surfnet']},
            ],
            FO['edugain']: [
                {'request': {}, 'requester': FO['swamid'],
                 'signer_add': {'usage': 'discovery'},
                 'signer': FO['edugain']},
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {}, 'signer': FO['swamid']}
            ]
        },
        "response": {
            FO['swamid']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['swamid']},
            ],
            FO['feide']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['feide']},
            ],
            FO['surfnet']: [
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['surfnet']},
            ],
            FO['edugain']: [
                {'request': {}, 'requester': FO['swamid'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['edugain']},
                {'request': {}, 'requester': OA['sunet'],
                 'signer_add': {}, 'signer': FO['swamid']}
            ]
        }
    },
    OA['uninett']: {
        "discovery": {
            FO['feide']: [
                {'request': {}, 'requester': OA['uninett'],
                 'signer_add': {'usage': 'discovery'},
                 'signer': FO['feide']},
            ]
        },
        "response": {
            FO['feide']: [
                {'request': {}, 'requester': OA['uninett'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['feide']},
            ]
        }
    },
    OA['example.org']: {
        "discovery": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {
                     'scopes_supported': ['openid', 'mail'],
                     'usage': 'discovery'},
                 'signer': FO['example.com']}
            ]
        },
        "response": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['example.com']},
            ]
        }
    },
    IA['cs.example.org']: {
        "discovery": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {
                     'scopes_supported': ['openid', 'email'],
                     'usage': 'discovery'},
                 'signer': FO['example.com']},
                {'request': {
                    'scopes_supported': ["openid", "profile", "email",
                                         "address",
                                         "phone", "offline_access"]},
                    'requester': IA['cs.example.org'],
                    'signer_add': {}, 'signer': OA['example.org']}
            ]
        },
        "response": {
            FO['example.com']: [
                {'request': {}, 'requester': OA['example.org'],
                 'signer_add': {'usage': 'response'},
                 'signer': FO['example.com']},
                {'request': {}, 'requester': IA['cs.example.org'],
                 'signer_add': {}, 'signer': OA['example.org']}
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
