__author__ = 'roland'

NORMAL = "/_/_/_/normal"

IDMAP = {
    # Discovery
    "rp-discovery-webfinger-url": NORMAL,
    "rp-discovery-webfinger-acct": NORMAL,
    "rp-discovery-openid-configuration": NORMAL,
    "rp-discovery-jwks_uri-keys": NORMAL,
    "rp-discovery-issuer-not-matching-config": "/_/_/isso/normal",

    # Dynamic Client Registration
    "rp-registration-dynamic": NORMAL,
    #"rp-registration-well-formed-jwk": NORMAL,
    #"rp-registration-uses-https-endpoints": NORMAL,

    # Response type and response mode
    "rp-response_type-code": NORMAL,
    "rp-response_type-id_token": NORMAL,
    "rp-response_type-id_token+token": NORMAL,
    "rp-response_type-code+id_token": NORMAL,
    "rp-response_type-code+token": NORMAL,
    "rp-response_type-code+id_token+token": NORMAL,

    # Response type and response mode
    "rp-response_mode-form_post": NORMAL,

    # Client Authentication
    "rp-token_endpoint-client_secret_basic": NORMAL,
    "rp-token_endpoint-client_secret_post": NORMAL,
    "rp-token_endpoint-client_secret_jwt": NORMAL,
    "rp-token_endpoint-private_key_jwt": NORMAL,

    # ID Token
    "rp-id_token-sig-rs256": "/RS256/_/_/normal",
    "rp-id_token-sig-hs256": "/HS256/_/_/normal",
    "rp-id_token-sig-es256": "/ES256/_/_/normal",
    "rp-id_token-bad-sig-rs256": "/RS256/_/idts/normal",
    "rp-id_token-bad-sig-hs256": "/HS256/_/idts/normal",
    "rp-id_token-bad-sig-es256": "/ES256/_/idts/normal",
    "rp-id_token-sig+enc": "/HS256/RSA1_5:A128CBC-HS256/_/normal",
    "rp-id_token-issuer-mismatch": "/_/_/issi/normal",
    "rp-id_token-sub": "/_/_/itsub/normal",
    "rp-id_token-aud": "/_/_/aud/normal",
    "rp-id_token-iat": "/_/_/iat/normal",
    #"rp-id_token-kid-absent": "/_/_/nokid1jwks/normal",
    #"rp-id_token-kid": "/_/_/nokidjwks/normal",
    "rp-id_token-bad-at_hash": "/_/_/ath/normal",
    "rp-id_token-bad-c_hash": "/_/_/ch/normal",
    "rp-id_token-kid-absent-multiple-jwks": "/_/_/nokidmuljwks/normal",
    "rp-id_token-kid-absent-single-jwks": "/_/_/nokid1jwk/normal",
    "rp-id_token-sig-none": "/none/_/_/normal",
    # "rp-idt-epk": "",

    # UserInfo Endpoint
    "rp-userinfo-bearer-header": NORMAL,
    "rp-userinfo-bearer-body": NORMAL,
    "rp-userinfo-not-query": NORMAL,
    "rp-userinfo-bad-sub-claim": "/_/_/uisub/normal",
    "rp-userinfo-sig": NORMAL,
    "rp-userinfo-enc": NORMAL,
    "rp-userinfo-sig+enc": NORMAL,

    # nonce Request Parameter
    "rp-nonce-unless-code-flow": NORMAL,
    "rp-nonce-invalid": "/_/_/nonce/normal",

    # scope Request Parameter
    "rp-scope-openid": "/_/_/openid/normal",
    "rp-scope-userinfo-claims": NORMAL,
    #"rp-scope-without-openid": "/_/_/openid/normal",

    # Key Rollover
    "rp-key-rotation-op-sign-key": "/_/_/rotsig/normal",
    "rp-key-rotation-rp-sign-key": "/_/_/updkeys/normal",
    "rp-key-rotation-op-enc-key": "/_/_/rotenc/normal",
    "rp-key-rotation-rp-enc-key": "/_/_/updkeys/normal",

    # request_uri Request Parameter
    "rp-request_uri-unsigned": NORMAL,
    "rp-request_uri-sig": NORMAL,
    "rp-request_uri-enc": NORMAL,
    "rp-request_uri-sig+enc": NORMAL,

    # Third Party Initiated Login
    "rp-support-3rd-party-init-login": NORMAL,

    # Claims Request Parameter
    "rp-claims_request-id_token": NORMAL,
    "rp-claims_request-userinfo": NORMAL,
    #"rp-claims_request-userinfo_claims": NORMAL,

    # "rp-3rd-login": "",

    # Claim Types
    "rp-claims-aggregated": "/_/_/_/aggregated",
    "rp-claims-distributed": "/_/_/_/distributed",

    # "rp-logout-init": "",
    # "rp-logout-received": "",
    # "rp-change-received": ""
    'rp-self-issued': "/_/_/selfissued/normal"
}
