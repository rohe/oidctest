TOOL_ISS = 'https://localhost'

FO = ['https://swamid.sunet.se/oidc', 'https://surfnet.nl/oidc']

ORG = {
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
    'F': {'scope': ['openid', 'email']}
}

CMS = [
    (POLICY['C'], ORG['example']['OA'], FO[1]),
    (POLICY['F'], ORG['example']['EO'], ORG['example']['OA'])
]
