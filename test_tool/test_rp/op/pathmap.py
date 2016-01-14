__author__ = 'roland'

NORMAL = "/_/_/_/normal"

IDMAP = {
    # Discovery
    "RP-discovery-webfinger_url": NORMAL,
    "RP-discovery-webfinger_acct": NORMAL,
    "RP-discovery": NORMAL,
    "RP-discovery-openid_configuration": NORMAL,
    "RP-discovery-jwks_uri_keys": NORMAL,
    "RP-discovery-issuer_not_matching_config": "/_/_/isso/normal",

    # Dynamic Client Registration
    "RP-registration-dynamic": NORMAL,
    'RP-registration-redirect_uris': NORMAL,
    "RP-registration-well_formed_jwk": NORMAL,
    "RP-registration-uses_https_endpoints": NORMAL,

    # Response type and response mode
    "RP-response_type-code": NORMAL,
    "RP-response_type-id_token": NORMAL,
    "RP-response_type-id_token+token": NORMAL,

    # Response type and response mode
    "RP-response_mode-form_post": NORMAL,

    # Client Authentication
    "RP-token_endpoint-client_secret_basic": NORMAL,
    "RP-token_endpoint-client_secret_post": NORMAL,
    "RP-token_endpoint-client_secret_jwt": NORMAL,
    "RP-token_endpoint-private_key_jwt": NORMAL,

    # ID Token
    "RP-id_token-asym_sig": "/RS256/_/_/normal",
    "RP-id_token-sym_sig": "/HS256/_/_/normal",
    "RP-id_token-ec_sig": "/ES256/_/_/normal",
    "RP-id_token-C_bad_asym_sig_rs256": "/RS256/_/idts/normal",
    "RP-id_token-I_bad_asym_sig_rs256": "/RS256/_/idts/normal",
    "RP-id_token-C_bad_symmetric_sig_hs256": "/HS256/_/idts/normal",
    "RP-id_token-I_bad_symmetric_sig_hs256": "/HS256/_/idts/normal",
    "RP-id_token-C_bad_es256_sig": "/ES256/_/idts/normal",
    "RP-id_token-I_bad_es256_sig": "/ES256/_/idts/normal",
    "RP-id_token-sig+enc": "/HS256/RSA1_5:A128CBC-HS256/_/normal",
    "RP-id_token-none": "/none/_/_/normal",
    "RP-id_token-issuer": "/_/_/issi/normal",
    "RP-id_token-C_sub": "/_/_/itsub/normal",
    "RP-id_token-I_sub": "/_/_/itsub/normal",
    "RP-id_token-C_aud": "/_/_/aud/normal",
    "RP-id_token-I_aud": "/_/_/aud/normal",
    "RP-id_token-C_iat": "/_/_/iat/normal",
    "RP-id_token-I_iat": "/_/_/iat/normal",
    "RP-id_token-kid-absent": "/_/_/nokid1jwks/normal",
    "RP-id_token-kid": "/_/_/nokidjwks/normal",
    "RP-id_token-bad_at_hash": "/_/_/ath/normal",
    "RP-id_token-bad_c_hash": "/_/_/ch/normal",
    "RP-id_token-C_mismatching_issuer": "/_/_/issi/normal",
    "RP-id_token-I_mismatching_issuer": "/_/_/issi/normal",
    "RP-id_token-C_kid_absent_multiple_jwks": "/_/_/nokidmuljwks/normal",
    "RP-id_token-I_kid_absent_multiple_jwks": "/_/_/nokidmuljwks/normal",
    "RP-id_token-kid_absent_single_jwks": "/_/_/nokid1jwk/normal",
    "RP-id_token-sig_none": "/none/_/_/normal",
    'RP-id_token-none-code': "/none/_/_/normal",
    # "RP-idt-epk": "",

    # UserInfo Endpoint
    "RP-user_info-bearer_header": NORMAL,
    "RP-user_info-bearer_body": NORMAL,
    "RP-user_info-not_query": NORMAL,
    "RP-user_info-bad_sub_claim": "/_/_/uisub/normal",
    "RP-user_info-sign": NORMAL,
    "RP-user_info-enc": NORMAL,
    "RP-user_info-sig+enc": NORMAL,

    # nonce Request Parameter
    "RP-nonce-unless_code_flow": NORMAL,
    "RP-nonce-invalid": "/_/_/nonce/normal",

    # scope Request Parameter
    "RP-scope-contains_openid_scope": "/_/_/openid/normal",
    "RP-scope-userinfo_claims": NORMAL,
    "RP-scope-without_openid_scope": "/_/_/openid/normal",

    # Key Rollover
    "RP-key_rotation-op_sign_key": "/_/_/rotsig/normal",
    "RP-key_rotation-rp_sign_key": "/_/_/updkeys/normal",
    "RP-key_rotation-op_enc_key": "/_/_/rotenc/normal",
    "RP-key_rotation-rp_enc_key": "/_/_/updkeys/normal",

    # request_uri Request Parameter
    "RP-request_uri-unsigned": NORMAL,
    "RP-request_uri-sig": NORMAL,
    "RP-request_uri-enc": NORMAL,
    "RP-request_uri-sig+enc": NORMAL,

    # Third Party Initiated Login
    "RP-support_3rd_party_init_login": NORMAL,

    # Claims Request Parameter
    "RP-claims_request-id_token_claims": NORMAL,
    "RP-claims_request-request_userinfo": NORMAL,
    "RP-claims_request-userinfo_claims": NORMAL,

    # "RP-3rd-login": "",

    # Claim Types
    "RP-claims-aggregated": "/_/_/_/aggregated",
    "RP-claims-distributed": "/_/_/_/distributed"

    # "RP-logout-init": "",
    # "RP-logout-received": "",
    # "RP-change-received": ""
}