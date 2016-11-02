PORT = 60050
BASE = "http://localhost"
KEYS = [
    {"key": "../keys/enc.key", "type": "RSA", "use": ["enc"]},
    {"key": "../keys/sig.key", "type": "RSA", "use": ["sig"]},
    {"crv": "P-256", "type": "EC", "use": ["sig"]},
    {"crv": "P-256", "type": "EC", "use": ["enc"]}
]

TOOL = {
    "instance_id": "basic_test_1",
    "login_hint": "foobar@example.com",
    "profile": "C.F.F.F.s.",
    "ui_locales": "de en",
    "issuer": "https://localhost:8040/"
}

CLIENT = {
    "behaviour": {
        "scope": ["openid", "profile", "email", "address", "phone"]
    },
    "client_prefs": {
        "default_max_age": 3600,
        "grant_types": [
            "authorization_code", "implicit", "refresh_token",
            "urn:ietf:params:oauth:grant-type:jwt-bearer:"],
        "id_token_signed_response_alg": [
            "RS256", "RS384", "RS512", "HS512", "HS384", "HS256"
        ],
        "request_object_signing_alg": [
            "RS256", "RS384", "RS512", "HS512", "HS384", "HS256"
        ],
        "require_auth_time": True,
        "response_types": [
            "code", "token", "id_token", "token id_token",
            "code id_token", "code token", "code token id_token"
        ],
        "subject_type": "public",
        "token_endpoint_auth_method": [
            "client_secret_basic", "client_secret_post",
            "client_secret_jwt", "private_key_jwt"
        ],
        "userinfo_signed_response_alg": [
            "RS256", "RS384", "RS512", "HS512", "HS384", "HS256"
        ],
    },
    "provider_info": {
        "acr_values_supported": ["PASSWORD"],
        "claims_supported": ["website", "updated_at", "address",
                             "email", "locale", "nickname",
                             "email_verified", "phone_number",
                             "gender", "picture", "family_name",
                             "zoneinfo", "name", "sub",
                             "birthdate", "middle_name",
                             "profile", "given_name",
                             "phone_number_verified",
                             "preferred_username"],
        "subject_types_supported": ["public", "pairwise"],
        "require_request_uri_registration": True,
        "token_endpoint": "https://localhost:8040/token",
        "claim_types_supported": ["normal", "aggregated",
                                  "distributed"],
        "userinfo_encryption_enc_values_supported": [
            "A128CBC-HS256", "A192CBC-HS384", "A256CBC-HS512",
            "A128GCM", "A192GCM", "A256GCM"],
        "registration_endpoint":
            "https://localhost:8040/registration",
        "token_endpoint_auth_methods_supported": [
            "client_secret_post", "client_secret_basic",
            "client_secret_jwt", "private_key_jwt"],
        "issuer": "https://localhost:8040/",
        "request_object_encryption_alg_values_supported": [
            "RSA1_5", "RSA-OAEP", "A128KW", "A192KW", "A256KW",
            "ECDH-ES", "ECDH-ES+A128KW", "ECDH-ES+A192KW",
            "ECDH-ES+A256KW"],
        "scopes_supported": ["address", "email", "offline_access",
                             "openid", "phone", "profile",
                             "openid"],
        "id_token_signing_alg_values_supported": [
            "RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "HS256",
            "HS384", "HS512", "PS256", "PS384", "PS512", "none"],
        "token_endpoint_auth_signing_alg_values_supported": [
            "RS256", "RS384", "RS512", "ES256", "ES384", "ES512",
            "HS256", "HS384", "HS512", "PS256", "PS384", "PS512"],
        "jwks_uri": "https://localhost:8040/static/jwks.json",
        "authorization_endpoint": "https://localhost:8040/authorization",
        "request_parameter_supported": True,
        "id_token_encryption_enc_values_supported": [
            "A128CBC-HS256", "A192CBC-HS384", "A256CBC-HS512",
            "A128GCM", "A192GCM", "A256GCM"],
        "userinfo_encryption_alg_values_supported": [
            "RSA1_5", "RSA-OAEP", "A128KW", "A192KW", "A256KW",
            "ECDH-ES", "ECDH-ES+A128KW", "ECDH-ES+A192KW",
            "ECDH-ES+A256KW"],
        "claims_parameter_supported": True,
        "userinfo_signing_alg_values_supported": [
            "RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "HS256",
            "HS384", "HS512", "PS256", "PS384", "PS512", "none"],
        "version": "3.0",
        "response_modes_supported": ["query", "fragment",
                                     "form_post"],
        "request_object_encryption_enc_values_supported": [
            "A128CBC-HS256", "A192CBC-HS384", "A256CBC-HS512",
            "A128GCM", "A192GCM", "A256GCM"],
        "end_session_endpoint": "https://localhost:8040/end_session",
        "userinfo_endpoint": "https://localhost:8040/userinfo",
        "id_token_encryption_alg_values_supported": [
            "RSA1_5", "RSA-OAEP", "A128KW", "A192KW", "A256KW", "ECDH-ES",
            "ECDH-ES+A128KW", "ECDH-ES+A192KW", "ECDH-ES+A256KW"],
        "grant_types_supported": ["authorization_code",
                                  "implicit",
                                  "urn:ietf:params:oauth:grant-type:jwt-bearer"],
        "request_uri_parameter_supported": True,
        "request_object_signing_alg_values_supported": [
            "RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "HS256",
            "HS384", "HS512", "PS256", "PS384", "PS512", "none"],
        "response_types_supported": [
            "code", "token", "id_token", "code token", "code id_token",
            "id_token token", "code token id_token", "none"]
    },
    "registration_response": {
        "client_secret":
            "cfd6d91cd2d91bf25584dcbfcd98b9ab7e5dda8f9e2b727c4ef84d1f",
        "redirect_uris": ["http://localhost:60050/authz_cb"],
        "client_id": "PFIHprfcLhon",
        "client_salt": "amE5T4VL"
    }
}
