__author__ = 'roland'

NORMAL = "/_/_/_/normal"

IDMAP = {
    # Discovery
    "rp-discovery-webfinger_url": NORMAL,
    "rp-discovery-webfinger_acct": NORMAL,
    "rp-discovery": NORMAL,
    "rp-discovery-openid_configuration": NORMAL,
    "rp-discovery-jwks_uri_keys": NORMAL,
    "rp-discovery-issuer_not_matching_config": "/_/_/isso/normal",

    # Dynamic Client Registration
    "rp-registration-dynamic": NORMAL,
    'rp-registration-redirect_uris': NORMAL,
    "rp-registration-well_formed_jwk": NORMAL,
    "rp-registration-uses_https_endpoints": NORMAL,

    # Response type and response mode
    "rp-response_type-code": NORMAL,
    "rp-response_type-id_token": NORMAL,
    "rp-response_type-id_token+token": NORMAL,

    # Response type and response mode
    "rp-response_mode-form_post": NORMAL,

    # Client Authentication
    "rp-token_endpoint-client_secret_basic": NORMAL,
    "rp-token_endpoint-client_secret_post": NORMAL,
    "rp-token_endpoint-client_secret_jwt": NORMAL,
    "rp-token_endpoint-private_key_jwt": NORMAL,

    # ID Token
    "rp-id_token-asym_sig": "/RS256/_/_/normal",
    "rp-id_token-sym_sig": "/HS256/_/_/normal",
    "rp-id_token-ec_sig": "/ES256/_/_/normal",
    "rp-id_token-c_bad_asym_sig_rs256": "/RS256/_/idts/normal",
    "rp-id_token-i_bad_asym_sig_rs256": "/RS256/_/idts/normal",
    "rp-id_token-c_bad_symmetric_sig_hs256": "/HS256/_/idts/normal",
    "rp-id_token-i_bad_symmetric_sig_hs256": "/HS256/_/idts/normal",
    "rp-id_token-c_bad_es256_sig": "/ES256/_/idts/normal",
    "rp-id_token-i_bad_es256_sig": "/ES256/_/idts/normal",
    "rp-id_token-sig+enc": "/HS256/RSA1_5:A128CBC-HS256/_/normal",
    "rp-id_token-none": "/none/_/_/normal",
    "rp-id_token-issuer": "/_/_/issi/normal",
    "rp-id_token-c_sub": "/_/_/itsub/normal",
    "rp-id_token-i_sub": "/_/_/itsub/normal",
    "rp-id_token-c_aud": "/_/_/aud/normal",
    "rp-id_token-i_aud": "/_/_/aud/normal",
    "rp-id_token-c_iat": "/_/_/iat/normal",
    "rp-id_token-i_iat": "/_/_/iat/normal",
    "rp-id_token-kid-absent": "/_/_/nokid1jwks/normal",
    "rp-id_token-kid": "/_/_/nokidjwks/normal",
    "rp-id_token-bad_at_hash": "/_/_/ath/normal",
    "rp-id_token-bad_c_hash": "/_/_/ch/normal",
    "rp-id_token-c_mismatching_issuer": "/_/_/issi/normal",
    "rp-id_token-i_mismatching_issuer": "/_/_/issi/normal",
    "rp-id_token-c_kid_absent_multiple_jwks": "/_/_/nokidmuljwks/normal",
    "rp-id_token-i_kid_absent_multiple_jwks": "/_/_/nokidmuljwks/normal",
    "rp-id_token-kid_absent_single_jwks": "/_/_/nokid1jwk/normal",
    "rp-id_token-sig_none": "/none/_/_/normal",
    'rp-id_token-none-code': "/none/_/_/normal",
    # "rp-idt-epk": "",

    # UserInfo Endpoint
    "rp-user_info-bearer_header": NORMAL,
    "rp-user_info-bearer_body": NORMAL,
    "rp-user_info-not_query": NORMAL,
    "rp-user_info-bad_sub_claim": "/_/_/uisub/normal",
    "rp-user_info-sign": NORMAL,
    "rp-user_info-enc": NORMAL,
    "rp-user_info-sig+enc": NORMAL,

    # nonce Request Parameter
    "rp-nonce-unless_code_flow": NORMAL,
    "rp-nonce-invalid": "/_/_/nonce/normal",

    # scope Request Parameter
    "rp-scope-contains_openid_scope": "/_/_/openid/normal",
    "rp-scope-userinfo_claims": NORMAL,
    "rp-scope-without_openid_scope": "/_/_/openid/normal",

    # Key Rollover
    "rp-key_rotation-op_sign_key": "/_/_/rotsig/normal",
    "rp-key_rotation-rp_sign_key": "/_/_/updkeys/normal",
    "rp-key_rotation-op_enc_key": "/_/_/rotenc/normal",
    "rp-key_rotation-rp_enc_key": "/_/_/updkeys/normal",

    # request_uri Request Parameter
    "rp-request_uri-unsigned": NORMAL,
    "rp-request_uri-sig": NORMAL,
    "rp-request_uri-enc": NORMAL,
    "rp-request_uri-sig+enc": NORMAL,

    # Third Party Initiated Login
    "rp-support_3rd_party_init_login": NORMAL,

    # Claims Request Parameter
    "rp-claims_request-id_token_claims": NORMAL,
    "rp-claims_request-request_userinfo": NORMAL,
    "rp-claims_request-userinfo_claims": NORMAL,

    # "rp-3rd-login": "",

    # Claim Types
    "rp-claims-aggregated": "/_/_/_/aggregated",
    "rp-claims-distributed": "/_/_/_/distributed"

    # "rp-logout-init": "",
    # "rp-logout-received": "",
    # "rp-change-received": ""
}