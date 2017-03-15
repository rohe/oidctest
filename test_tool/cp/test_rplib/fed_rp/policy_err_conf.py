TOOL_ISS = 'https://localhost'

FO = {'example.com': 'https://example.com'}
OA = {'example.org': 'https://example.org'}
IA = {'cs.example.org': 'https://cs.example.org'}
EO = {'example.org.op': 'https://example.org/op'}

SMS_DEF = {
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
