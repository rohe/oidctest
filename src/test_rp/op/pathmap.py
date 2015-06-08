__author__ = 'roland'

NORMAL = "/_/_/_/normal"

IDMAP = {
    # Discovery
    "rp-discovery-webfinger_url": NORMAL,
    "rp-discovery-webfinger_acct": NORMAL,
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
    "rp-idt-asym_sig": "/RS256/_/_/normal",
    "rp-idt-sym_sig": "/HS256/_/_/normal",
    "rp-idt-ec_sig": "/ES256/_/_/normal",
    "rp-id_token-bad_asym_sig_rs256": "/RS256/_/idts/normal",
    "rp-id_token-bad_symmetric_sig_hs256": "/HS256/_/idts/normal",
    "rp-id_token-bad_es256_sig": "/ES256/_/idts/normal",
    "rp-id_token-sig+enc": "/HS256/RSA1_5:A128CBC-HS256/_/normal",
    "rp-id_token-sig_none": "/none/_/_/normal",
    "rp-id_token-issuer": "/_/_/issi/normal",
    "rp-id_token-sub": "/_/_/itsub/normal",
    "rp-id_token-aud": "/_/_/aud/normal",
    "rp-id_token-iat": "/_/_/iat/normal",
    # "rp-idt-kid-absent": "/_/_/nokid1jwks/normal",
    "rp-idt-kid": "/_/_/nokidjwks/normal",
    "rp-id_token-bad_at_hash": "/_/_/ath/normal",
    "rp-id_token-bad_c_hash": "/_/_/ch/normal",
    "rp-id_token-mismatching_issuer": "/_/_/issi/normal",
    "rp-id_token-kid_absent_multiple_jwks": "/_/_/nokidmuljwks/normal",
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
    "rp-scope-contains_openid_scope": NORMAL,
    "rp-scope-userinfo_claims": NORMAL,

    # Key Rollover
    "rp-key_rollover-op_sign_key": "/_/_/rotsig/normal",
    "rp-key_rollover-rp_sign_key": NORMAL,
    "rp-key_rollover-op_enc_key": "/_/_/rotenc/normal",
    "rp-key_rollover-rp_enc_key": NORMAL,

    # request_uri Request Parameter
    "rp-request_uri-unsigned": NORMAL,
    "rp-request_uri-sig": NORMAL,
    "rp-request_uri-enc": NORMAL,
    "rp-request_uri-sig+enc": NORMAL,

    # Claims Request Parameter
    "rp-claims_request-id_token_claims": NORMAL,
    "rp-claims_request-request_userinfo": NORMAL,

    # "rp-3rd-login": "",

    # Claim Types
    "rp-claims-aggregated": "/_/_/_/aggregated",
    "rp-claims-distributed": "/_/_/_/distributed"

    # "rp-logout-init": "",
    # "rp-logout-received": "",
    # "rp-change-received": ""
}