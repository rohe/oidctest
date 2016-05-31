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
        "path": "/_/_/_/aggregated",
        "response_type": [C, CI, CT, CIT],
    },
    "rp-claims-distributed": {
        "path": "/_/_/_/distributed",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-claims_request-id_token_claims": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-claims_request-request_userinfo": {
        'path': "/_/_/_/normal",
        "response_type": [C, IT, CI, CT, CIT]
    },
    "rp-claims_request-userinfo_claims": {
        "path": "/_/_/_/normal",
        "response_type": [C, IT, CI, CT, CIT]
    },
    "rp-discovery": {
        'path': "/_/_/_/normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-issuer_not_matching_config": {
        "path": "/_/_/isso/normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-jwks_uri_keys": {
        "path": "/_/_/_/normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-openid_configuration": {
        "path": "/_/_/_/normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-discovery-webfinger_acct": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-discovery-webfinger_url": {
        "path": "/_/_/_/normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-id_token-asym_sig": {
        'path': "/RS256/_/_/normal",
        "response_type": ALL
    },
    "rp-id_token-aud": {
        "path": "/_/_/aud/normal",
        "response_type": ALL
    },
    "rp-id_token-bad_asym_sig_rs256": {
        "path": "/RS256/_/idts/normal",
        "response_type": ALL
    },
    "rp-id_token-bad_at_hash": {
        "path": "/_/_/ath/normal",
        "response_type": [CIT, IT],
        'out_of_scope': [T, U]
    },
    "rp-id_token-bad_c_hash": {
        "path": "/_/_/ch/normal",
        "response_type": [CIT, CI],
        'out_of_scope': [T, U]
    },
    "rp-id_token-bad_es256_sig": {
        "path": "/ES256/_/idts/normal",
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-bad_symmetric_sig_hs256": {
        "path": "/HS256/_/idts/normal",
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-ec_sig": {
        'path': "/ES256/_/_/normal",
        "response_type": ALL},
    "rp-id_token-iat": {
        "path": "/_/_/iat/normal",
        "response_type": ALL
    },
    "rp-id_token-issuer": {
        'path': "/_/_/issi/normal",
        "response_type": ALL
    },
    "rp-id_token-kid": {
        'path': "/_/_/nokidjwks/normal",
        "response_type": ALL
    },
    "rp-id_token-kid-absent": {
        'path': "/_/_/nokid1jwks/normal",
        "response_type": ALL,
        'out_of_scope': [U]
    },
    "rp-id_token-kid_absent_multiple_jwks": {
        "path": "/_/_/nokidmuljwks/normal",
        "response_type": ALL
    },
    "rp-id_token-kid_absent_single_jwks": {
        "path": "/_/_/nokid1jwk/normal",
        "response_type": ALL
    },
    "rp-id_token-mismatching_issuer": {
        "path": "/_/_/issi/normal",
        "response_type": ALL,
        'out_of_scope': [R, A, T, U]
    },
    "rp-id_token-none": {
        "path": "/none/_/_/normal",
        "response_type": [C, CT, CIT]
    },
    "rp-id_token-none-code": {
        "path": "/none/_/_/normal",
        "response_type": ALL
    },
    "rp-id_token-sig+enc": {
        "path": "/HS256/RSA1_5:A128CBC-HS256/_/normal",
        "response_type": ALL
    },
    "rp-id_token-sig_none": {
        "path": "/none/_/_/normal",
        "response_type": [C]
    },
    "rp-id_token-sub": {
        "path": "/_/_/itsub/normal",
        "response_type": [C, CT]
    },
    "rp-id_token-sym_sig": {
        "path": "/HS256/_/_/normal",
        "response_type": [I]
    },
    "rp-key_rotation-op_enc_key": {
        "path": "/_/_/rotenc/normal",
        "response_type": ALL
    },
    "rp-key_rotation-op_sign_key": {
        "path": "/_/_/rotsig/normal",
        "response_type": [C]
    },
    "rp-key_rotation-rp_enc_key": {
        "path": "/_/_/updkeys/normal",
        "response_type": [C, CT]
    },
    "rp-key_rotation-rp_sign_key": {
        "path": "/_/_/updkeys/normal",
        "response_type": ALL
    },
    "rp-nonce-invalid": {
        "path": "/_/_/nonce/normal",
        "response_type": [I, IT, CI, CIT]
    },
    "rp-nonce-unless_code_flow": {
        "path": "/_/_/_/normal",
        "response_type": [I, IT, CI, CIT]
    },
    "rp-registration-dynamic": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-redirect_uris": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-uses_https_endpoints": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-registration-well_formed_jwk": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-enc": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-sig": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-sig+enc": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-request_uri-unsigned": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-response_mode-form_post": {
        "path": "/_/_/_/normal",
        "response_type": [I, IT, CI, CT, CIT]
    },
    "rp-response_type-code": {
        "path": "/_/_/_/normal",
        "response_type": [C]
    },
    "rp-response_type-id_token": {
        "path": "/_/_/_/normal",
        "response_type": [I]
    },
    "rp-response_type-id_token+token": {
        "path": "/_/_/_/normal",
        "response_type": [IT]
    },
    "rp-scope-contains_openid_scope": {
        "path": "/_/_/openid/normal",
        "response_type": ALL
    },
    "rp-scope-userinfo_claims": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-scope-without_openid_scope": {
        "path": "/_/_/openid/normal",
        "response_type": ALL
    },
    "rp-support_3rd_party_init_login": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-token_endpoint-client_secret_basic": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-token_endpoint-client_secret_jwt": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-token_endpoint-client_secret_post": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-token_endpoint-private_key_jwt": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CIT]
    },
    "rp-user_info-bad_sub_claim": {
        "path": "/_/_/uisub/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-bearer_body": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-bearer_header": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-enc": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-not_query": {
        "path": "/_/_/_/normal",
        "response_type": ALL
    },
    "rp-user_info-sig+enc": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    },
    "rp-user_info-sign": {
        "path": "/_/_/_/normal",
        "response_type": [C, CI, CT, CIT]
    }
}
