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
    "rp-claims_request-id_token_claims": {
        "claims": "normal",
        "response_type": ALL
    },
    "rp-claims_request-request_userinfo": {
        "claims": "normal",
        "response_type": [C, IT, CI, CT, CIT]
    },
    "rp-claims_request-userinfo_claims": {
        "claims": "normal",
        "response_type": [C, IT, CI, CT, CIT]
    },
    "rp-discovery": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-issuer_not_matching_config": {
        "claims": "normal",
        "behavior": "isso",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-jwks_uri_keys": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-openid_configuration": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-webfinger_acct": {
        "claims": "normal",
        "response_type": ALL
    },
    "rp-discovery-webfinger_url": {
        "claims": "normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-id_token-asym_sig": {
        "claims": "normal",
        'signing_alg': "RS256",
        "response_type": ALL
    },
    "rp-id_token-aud": {
        "claims": "normal",
        "behavior": ["aud"],
        "response_type": ALL
    },
    "rp-id_token-bad_asym_sig_rs256": {
        "claims": "normal",
        "behavior": ["idts"],
        'signing_alg': "RS256",
        "response_type": ALL
    },
    "rp-id_token-bad_at_hash": {
        "claims": "normal",
        "behavior": ["ath"],
        "response_type": [CIT, IT],
        'out_of_scope': [T, U]
    },
    "rp-id_token-bad_c_hash": {
        "claims": "normal",
        "behavior": ["ch"],
        "response_type": [CIT, CI],
        'out_of_scope': [T, U]
    },
    "rp-id_token-bad_es256_sig": {
        "claims": "normal",
        "behavior": ["idts"],
        'signing_alg': "ES256",
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-bad_symmetric_sig_hs256": {
        "claims": "normal",
        "behavior": ["idts"],
        'signing_alg': "HS256",
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-ec_sig": {
        "claims": "normal",
        'signing_alg': "ES256",
        "response_type": ALL},
    "rp-id_token-iat": {
        "claims": "normal",
        "behavior": ["iat"],
        "response_type": ALL
    },
    "rp-id_token-issuer": {
        "claims": "normal",
        "behavior": ["issi"],
        "response_type": ALL
    },
    "rp-id_token-kid": {
        "claims": "normal",
        # "behavior": ["nokidjwks"],
        "response_type": ALL
    },
    "rp-id_token-kid-absent": {
        "claims": "normal",
        "behavior": ["nokidjwks"],
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-kid_absent_multiple_jwks": {
        "claims": "normal",
        "behavior": ["nokidmuljwks"],
        "response_type": ALL
    },
    "rp-id_token-kid_absent_single_jwks": {
        "claims": "normal",
        "behavior": ["nokidjwks"],
        "response_type": ALL
    },
    "rp-id_token-mismatching_issuer": {
        "claims": "normal",
        "behavior": ["issi"],
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-none": {
        "claims": "normal",
        'signing_alg': "none",
        "response_type": [C, CT, CIT]
    },
    "rp-id_token-none-code": {
        "claims": "normal",
        'signing_alg': "none",
        "response_type": ALL
    },
    "rp-id_token-sig+enc": {
        "claims": "normal",
        'signing_alg': "HS256",
        'encryption_alg': 'RSA1_5',
        'encryption_enc': 'A128CBC-HS256',
        "response_type": ALL
    },
    "rp-id_token-sig_none": {
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
    "rp-id_token-sym_sig": {
        "claims": "normal",
        'signing_alg': "HS256",
        # "path": "/HS256/_/_/normal",
        "response_type": [I]
    },
    "rp-key_rotation-op_enc_key": {
        "claims": "normal",
        "behavior": ["rotenc"],
        # "path": "/_/_/rotenc/normal",
        "response_type": ALL
    },
    "rp-key_rotation-op_sign_key": {
        "claims": "normal",
        "behavior": ["rotsig"],
        # "path": "/_/_/rotsig/normal",
        "response_type": [C]
    },
    "rp-key_rotation-rp_enc_key": {
        "claims": "normal",
        "behavior": ["updkeys"],
        # "path": "/_/_/updkeys/normal",
        "response_type": [C, CT]
    },
    "rp-key_rotation-rp_sign_key": {
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
    "rp-nonce-unless_code_flow": {
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
    "rp-registration-uses_https_endpoints": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-well_formed_jwk": {
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
    "rp-scope-contains_openid_scope": {
        "claims": "normal",
        "behavior": ["openid"],
        # "path": "/_/_/openid/normal",
        "response_type": ALL
    },
    "rp-scope-userinfo_claims": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-scope-without_openid_scope": {
        "claims": "normal",
        "behavior": ["openid"],
        # "path": "/_/_/openid/normal",
        "response_type": ALL
    },
    "rp-support_3rd_party_init_login": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
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
    "rp-user_info-bad_sub_claim": {
        "claims": "normal",
        "behavior": ["uisub"],
        # "path": "/_/_/uisub/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-bearer_body": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-bearer_header": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-enc": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-not_query": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-user_info-sig+enc": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-sign": {
        "claims": "normal",
        # "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    }
}
