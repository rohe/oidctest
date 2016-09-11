__author__ = 'roland'

NORMAL = "/_/_/_/normal"
C = 'code'
CI = 'code id_token'
CT = 'code token'
CIT = 'code id_token token'
I = 'id_token'
IT = 'id_token token'
ALL = [C, CI, CT, CIT, I, IT]

R = 'registration_endpoint'
A = 'authorization_endpoint'
T = 'token_endpoint'
U = 'userinfo_endpoint'

CONF = {
    "rp-claims-aggregated": {
        "claims": "aggregated",
        "response_type": [C, CI, CT, CIT],
    },
    "rp-claims-distributed": {
        "claims": "distributed",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-claims_request-id_token": {
        "claims": "normal",
        "response_type": ALL
    },
    "rp-claims_request-userinfo": {
        "claims": "normal",
        "response_type": [C, IT, CI, CT, CIT]
    },
    "rp-discovery-issuer-not-matching-config": {
        "claims": "normal",
        "behavior": "isso",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-jwks_uri-keys": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-discovery-openid-configuration": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-webfinger-acct": {
        "claims": "normal",
        "response_type": ALL
    },
    "rp-discovery-webfinger-url": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-id_token-sig-rs256": {
        "claims": "normal",
        'signing_alg': "RS256",
        "response_type": ALL
    },
    "rp-id_token-sig-hs256": {
        "claims": "normal",
        'signing_alg': "HS256",
        "response_type": ALL
    },
    "rp-id_token-sig-es256": {
        "claims": "normal",
        'signing_alg': "ES256",
        "response_type": ALL
    },
    "rp-id_token-aud": {
        "claims": "normal",
        "behavior": ["aud"],
        "response_type": ALL
    },
    "rp-id_token-bad-sig-rs256": {
        "claims": "normal",
        "behavior": ["idts"],
        'signing_alg': "RS256",
        "response_type": ALL
    },
    "rp-id_token-bad-sig-hs256": {
        "claims": "normal",
        "behavior": ["idts"],
        'signing_alg': "HS256",
        "response_type": ALL
    },
    "rp-id_token-bad-sig-es256": {
        "claims": "normal",
        "behavior": ["idts"],
        'signing_alg': "ES256",
        "response_type": ALL
    },
    "rp-id_token-bad-at_hash": {
        "claims": "normal",
        "behavior": ["ath"],
        "response_type": [CIT, IT],
        'out_of_scope': [T, U]
    },
    "rp-id_token-bad-c_hash": {
        "claims": "normal",
        "behavior": ["ch"],
        "response_type": [CIT, CI],
        'out_of_scope': [T, U]
    },
    "rp-id_token-iat": {
        "claims": "normal",
        "behavior": ["iat"],
        "response_type": ALL
    },
    "rp-id_token-kid-absent-multiple-jwks": {
        "claims": "normal",
        "behavior": ["nokidmuljwks"],
        "response_type": ALL
    },
    "rp-id_token-kid-absent-single-jwks": {
        "claims": "normal",
        "behavior": ["nokid1jwks"],
        "response_type": ALL
    },
    "rp-id_token-issuer-mismatch": {
        "claims": "normal",
        "behavior": ["issi"],
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-sig+enc": {
        "claims": "normal",
        'signing_alg': "HS256",
        'encryption_alg': 'RSA1_5',
        'encryption_enc': 'A128CBC-HS256',
        "response_type": ALL
    },
    "rp-id_token-sig-none": {
        "claims": "normal",
        'signing_alg': "none",
        "response_type": [C]
    },
    "rp-id_token-sub": {
        "claims": "normal",
        "behavior": ["itsub"],
        # "path": "/_/_/itsub/normal",
        "response_type": [C, CT]
    },
    "rp-key-rotation-op-enc-key": {
        "claims": "normal",
        "behavior": ["rotenc"],
        # "path": "/_/_/rotenc/normal",
        "response_type": ALL
    },
    "rp-key-rotation-op-sign-key": {
        "claims": "normal",
        "behavior": ["rotsig"],
        # "path": "/_/_/rotsig/normal",
        "response_type": [C]
    },
    "rp-key-rotation-rp-enc-key": {
        "claims": "normal",
        "behavior": ["updkeys"],
        # "path": "/_/_/updkeys/normal",
        "response_type": [C, CT]
    },
    "rp-key-rotation-rp-sign-key": {
        "claims": "normal",
        "behavior": ["updkeys"],
        # "path": "/_/_/updkeys/normal",
        "response_type": ALL
    },
    "rp-nonce-invalid": {
        "claims": "normal",
        "behavior": ["nonce"],
        # "path": "/_/_/nonce/normal",
        "response_type": [I, IT, CI, CIT]
    },
    "rp-nonce-unless-code-flow": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [I, IT, CI, CIT]
    },
    "rp-registration-dynamic": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-redirect_uris": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-uses-https-endpoints": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-well-formed-jwk": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-enc": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-sig": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-sig+enc": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-unsigned": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-response_mode-form_post": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [I, IT, CI, CT, CIT]
    },
    "rp-response_type-code": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C]
    },
    "rp-response_type-id_token": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [I]
    },
    "rp-response_type-id_token+token": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [IT]
    },
    "rp-response_type-code+token": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [CT]
    },
    "rp-response_type-code+id_token": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [CI]
    },
    "rp-response_type-code+id_token+token": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [CIT]
    },
    "rp-scope-openid": {
        "claims": "normal",
        "behavior": ["openid"],
        # "path": "/_/_/openid/normal",
        "response_type": ALL
    },
    "rp-scope-userinfo-claims": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    # "rp-self-issued": {
    #     "claims": "normal",
    #     # "path": "/_/_/openid/normal",
    #     "response_type": ALL
    # },
    # "rp-support_3rd_party_init_login": {
    #     "claims": "normal",
    #     # "path": "/_/_/_/normal",
    #     "response_type": ALL
    # },
    "rp-token_endpoint-client_secret_basic": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-token_endpoint-client_secret_jwt": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-token_endpoint-client_secret_post": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-token_endpoint-private_key_jwt": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-userinfo-bad-sub-claim": {
        "claims": "normal",
        "behavior": ["uisub"],
        # "path": "/_/_/uisub/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-userinfo-bearer-body": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-userinfo-bearer-header": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-userinfo-enc": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-userinfo-not-query": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-userinfo-sig+enc": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-userinfo-sig": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    }
}
