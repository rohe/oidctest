TOOL_ISS = 'https://localhost'

FO = {'swamid': 'https://swamid.sunet.se',
      'surfnet': 'https://surfnet.nl/oidc',
      'feide': 'https://www.feide.no',
      'edugain': 'https://edugain.com',
      'example.com': 'https://example.com'}

OA = {'sunet': 'https://sunet.se', 'uninett': 'https://uninett.no',
      'example.org': 'https://example.org'}

IA = {'cs.example.org': 'https://cs.example.org'}

EO = {'sunet.op': 'https://sunet.se/op',
      'example.org.op': 'https://example.org/op'}

BASE = {'sunet.op': EO['sunet.op']}

SMS_DEF = {
    OA['sunet']: {
        FO['swamid']: [
            {'request': {}, 'requester': OA['sunet'],
             'signer_add': {}, 'signer': FO['swamid']},
        ],
        FO['feide']: [
            {'request': {}, 'requester': OA['sunet'],
             'signer_add': {}, 'signer': FO['feide']},
        ],
        FO['surfnet']: [
            {'request': {}, 'requester': OA['sunet'],
             'signer_add': {}, 'signer': FO['surfnet']},
        ],
        FO['edugain']: [
            {'request': {}, 'requester': FO['swamid'],
             'signer_add': {}, 'signer': FO['edugain']},
            {'request': {}, 'requester': OA['sunet'],
             'signer_add': {}, 'signer': FO['swamid']}
        ]
    },
    OA['uninett']: {
        FO['feide']: [
            {'request': {}, 'requester': OA['uninett'],
             'signer_add': {}, 'signer': FO['feide']},
        ]
    },
    OA['example.org']: {
        FO['example.com']: [
            {'request': {}, 'requester': OA['example.org'],
             'signer_add': {'scopes_supported': ['openid', 'mail']},
             'signer': FO['example.com']},
        ],
    },
    IA['cs.example.org']: {
        FO['example.com']: [
            {'request': {}, 'requester': OA['example.org'],
             'signer_add': {'scopes_supported': ['openid', 'email']},
             'signer': FO['example.com']},
            {'request': {
                'scopes_supported': ["openid", "profile", "email", "address",
                                     "phone", "offline_access"]},
                'requester': IA['cs.example.org'],
                'signer_add': {}, 'signer': OA['example.org']}
        ],
    }
}

KEY_DEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]
