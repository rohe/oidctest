var app = angular.module('main', ['ngSanitize']);

app.controller('IndexCtrl', function ($scope, $sce) {

    var OPTIONAL = "(optional)"
    var REJECTION_ALLOWED = "(rejection allowed)"
    var ALT_TO_HDR_METHOD = "(alt to hdr method)"

    var BASIC = {"text" : "Basic"}
    var BASIC_OPTIONAL = {"text" : BASIC.text, "optional_text": OPTIONAL}
    var BASIC_ALT_TO_HDR_METHOD = {"text" : BASIC.text, "optional_text": ALT_TO_HDR_METHOD}

    var IMPLICIT = {"text" : "Implicit"}
    var IMPLICIT_OPTIONAL = {"text" : IMPLICIT.text, "optional_text": OPTIONAL}
    var IMPLICIT_REJECTION_ALLOWED = {"text" : IMPLICIT.text, "optional_text": REJECTION_ALLOWED}
    var IMPLICIT_ALT_TO_HDR_METHOD = {"text" : IMPLICIT.text, "optional_text": ALT_TO_HDR_METHOD}

    var HYBRID = {"text" :"Hybrid"}
    var HYBRID_OPTIONAL = {"text" : HYBRID.text, "optional_text": OPTIONAL}
    var HYBRID_REJECTION_ALLOWED = {"text" : HYBRID.text, "optional_text": REJECTION_ALLOWED}
    var HYBRID_ALT_TO_HDR_METHOD = {"text" : HYBRID.text, "optional_text": ALT_TO_HDR_METHOD}

    var SELF_ISSUED = {"text" :"Self-issued"}
    var SELF_ISSUED_OPTIONAL = {"text" : SELF_ISSUED.text, "optional_text": OPTIONAL}

    var CONFIG = {"text" :"Config"}
    var CONFIG_OPTIONAL = {"text" : CONFIG.text, "optional_text": OPTIONAL}

    var DYNAMIC = {"text" :"Dynamic"}
    var DYNAMIC_OPTIONAL = {"text" : DYNAMIC.text, "optional_text": OPTIONAL}

    $scope.profiles = [
        {profile: 'All tests' },
        {profile: BASIC.text },
        {profile: IMPLICIT.text },
        {profile: HYBRID.text },
        {profile: SELF_ISSUED.text },
        {profile: CONFIG.text },
        {profile: DYNAMIC.text}
    ];

    $scope.selectedItem = $scope.profiles[0];

    $scope.contains_selected_profile = function(profile_list){

        if ($scope.selectedItem == $scope.profiles[0]){
            return true;
        }

        if (profile_list == null){
            return false;
        }

        for (var i=0; i<profile_list.length; i++){
            if ($scope.selectedItem.profile == profile_list[i].text){
                return true;
            }
        }

        return false;
    };

    var IMPLICIT_FLOW_ID_TOKEN_URL = "https://openid.net/specs/openid-connect-core-1_0-17.html#ImplicitIDToken";
    var CLIENT_AUTHENTICATION_URL = "https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication";
    var SIGNING_URL = "https://openid.net/specs/openid-connect-core-1_0.html#Signing";
    var ID_TOKEN_URL = "https://openid.net/specs/openid-connect-core-1_0.html#IDToken";

    var ISSUER_DISCOVERY_DOC = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#IssuerDiscovery", "OpenID Provider Issuer Discovery");
    var CLIENT_REGISTRATION_ENDPOINT = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#ClientRegistration", "client registration endpoint");
    var CODE_FLOW = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#CodeFlowAuth", "Code Flow");
    var IMPLICIT_FLOW = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ImplicitFlowAuth", "Implicit Flow");
    var BEARER_HEADER_METHOD = convert_to_link("http://tools.ietf.org/html/rfc6750#section-2.1", "Bearer header method");
    var FORM_ENCODED_BODY_METHOD = convert_to_link("http://tools.ietf.org/html/rfc6750#section-2.2", "form-encoded body method");
    var RFC7033 = convert_to_link("http://tools.ietf.org/html/rfc7033#section-7", "RFC7033");
    var URL_SYNTAX = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#URLSyntax", "URL syntax");
    var ACCT_SYNTAX = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#AcctURISyntax", "acct URI syntax");
    var CLIENT_REGISTRATION_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#RegistrationResponse", "Client Registration Response");
    var AUTHORIZATION_CODE_FLOW = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#CodeFlowAuth", "Authorization Code Flow");
    var CODE_AUTHENTICATION_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#AuthResponse", "authentication response");
    var IMPLICIT_AUTHENTICATION_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#ImplicitAuthResponse", "authentication response");
    var CLIENT_SECRET_BASIC = convert_to_link(CLIENT_AUTHENTICATION_URL, "client_secret_basic");
    var TOKEN_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#TokenResponse", "Token Response");
    var USERINFO_REQUEST = convert_to_link("https://openid.net/specs/openid-connect-standard-1_0-21.html#UserInfoRequest", "UserInfo Request");
    var USERINFO_RESPONSE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#UserInfo", "UserInfo Response");
    var OPENID_PROVIDER_ISSUER_DISCOVERY = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#IssuerDiscovery", "OpenID Provider Issuer Discovery");
    var PROVIDER_CONFIGURATION = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata", "provider configuration");
    var RESPONSE_TYPE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ImplicitAuthRequest", "response_type");
    var FORM_POST = convert_to_link("https://openid.net/specs/oauth-v2-form-post-response-mode-1_0.html#FormPostResponseMode", "form_post");
    var RESPONSE_MODE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest", "response mode");
    var CLIENT_SECRET_JWT = convert_to_link(CLIENT_AUTHENTICATION_URL, "client_secret_jwt");
    var CLIENT_SECRET_POST = convert_to_link(CLIENT_AUTHENTICATION_URL, "client_secret_post");
    var PRIVATE_KEY_JWT = convert_to_link(CLIENT_AUTHENTICATION_URL, "private_key_jwt");
    var AUTHORIZATION_CODE_VALIDATION = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#CodeValidation", "Authorization Code Validation");
    var C_HASH = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#HybridIDToken", "c_hash");
    var AT_HASH = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#HybridIDToken", "at_hash");
    var ACCESS_TOKEN_VALIDATION = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowTokenValidation", "Access Token validation");
    var ID_TOKEN_VALIDATION = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation", "ID Token validation");
    var IAT = convert_to_link(ID_TOKEN_URL, "iat");
    var AUD = convert_to_link(ID_TOKEN_URL, "aud");
    var ISS = convert_to_link(ID_TOKEN_URL, "iss");
    var CLIENT_ID = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#RegistrationResponse", "client_id");
    var SUB = convert_to_link(ID_TOKEN_URL, "sub");
    var CLAIMS_REQUEST_PARAMETER = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ClaimsParameter", "'claims' request parameter");
    var REQUEST_OBJECT_BY_REFERENCE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RequestUriParameter", "Request Object by Reference");
    var ENCRYPT_THE_REQUEST_OBJECT = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#EncryptedRequestObject", "Encrypt the Request Object");
    var SIGN_THE_REQUEST_OBJECT = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#SignedRequestObject", "Sign the Request Object");
    var AGGREGATED_CLAIMS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ClaimTypes", "Aggregated Claims");
    var DISTRIBUTED_CLAIMS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ClaimTypes", "Distributed Claims");
    var SELF_ISSUED_OPENID_PROVIDERS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#SelfIssued", "Self-Issued OpenID Provider");
    var HYBRID_FLOW_ID_TOKEN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0-17.html#HybridIDToken", "hybrid flow");
    var IMPLICIT_FLOW_ID_TOKEN = convert_to_link(IMPLICIT_FLOW_ID_TOKEN_URL, "implicit flow");
    var OPENID_SCOPE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#AuthRequest", "openid scope");
    var REQUEST_CLAIMS_USING_SCOPE_VALUES = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims", "Request claims using scope values");
    var OPENID_PROVIDER_METADATA = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata", "OpenID Provider Metadata");
    var CLIENT_METADATA = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#ClientMetadata", "Client Metadata");
    var JSON_WEB_KEY_SET_FORMAT = convert_to_link("https://tools.ietf.org/html/draft-ietf-jose-json-web-key-41#section-5", "JSON Web Key Set (JWK Set) Format");
    var THIRD_PARTY_INITIATED_LOGIN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ThirdPartyInitiatedLogin", "third-party initiated login");
    var OPENID_CONFIGURATION_INFORMATION = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig", "OpenID Provider Configuration Information");
    var SIGNING_KEY_ROLLOVER = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RotateSigKeys", "signing key rollover");
    var ENCRYPTION_KEY_ROLLOVER = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RotateEncKeys", "encryption key rollover");
    var ID_TOKEN_IMPLICIT_FLOW = convert_to_link(IMPLICIT_FLOW_ID_TOKEN_URL, "ID Token");
    var SELF_ISSUED_AUTH_RESPONSE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#SelfIssuedResponse", "authentication response");
    var SELF_ISSUED_ID_TOKEN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#SelfIssuedValidation", "self-issued ID Token");
    var TOKEN_REQUEST = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#TokenRequest", "Token Request");
    var ID_TOKEN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#IDToken", "ID Token");
    var UNSECURED_JWS = convert_to_link("https://tools.ietf.org/html/rfc7518#section-3.6", "Unsecured JWS");
    var NONCE_IMPLMENTATION = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#NonceNotes", "'nonce' value");
    var HYBRID_FLOW = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#HybridFlowAuth", "Hybrid Flow");
    var SYMMETRIC_SIGNATURES = convert_to_link(SIGNING_URL, "'client_secret' as MAC key");
    var MULITPLE_KEYS_JWKS = convert_to_link(SIGNING_URL, "multiple keys in its JWK Set document");
    var ENCRYPTED_REQUEST = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#JWTRequests", "encrypted authentication request");
    var SIGNING_KEY_ROTATION = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RotateSigKeys", "rolled over signing keys");

    $scope.guidlines = [
        ["Discovery", {
            "rp-discovery-webfinger_url": {
                "short_description": "Can discover OpenID providers using URL syntax",
                "profiles": [DYNAMIC],
                "detailed_description": "Use WebFinger (" +
                RFC7033 + ") and " + ISSUER_DISCOVERY_DOC + " to determine the location of the OpenID Provider. " +
                "The discovery should be done using " + URL_SYNTAX + " as user input identifier.",
                "expected_result": "An issuer location should be returned."
            },
            "rp-discovery-webfinger_acct": {
                "short_description": "Can discover OpenID providers using acct URI syntax",
                "profiles": [DYNAMIC],
                "detailed_description": "Use WebFinger (" +
                RFC7033 + ") and " + ISSUER_DISCOVERY_DOC + " to determine the location of the OpenID Provider. " +
                "The discovery should be done using " + ACCT_SYNTAX + " as user input identifier.",
                "expected_result": "An issuer location should be returned."
            },
            "rp-discovery": {
                "short_description": "Uses \"OpenID Connect Discovery\"",
                "profiles": [DYNAMIC],
                "detailed_description": "The Relying Party should be able to determine the OpenID Provider location by using " +
                OPENID_PROVIDER_ISSUER_DISCOVERY + ".",
                "expected_result": "An issuer location should be returned."
            },
            "rp-discovery-issuer_not_matching_config": {
                "short_description": "Rejects discovered issuer not matching provider configuration issuer",
                "profiles": [CONFIG, DYNAMIC],
                "detailed_description": "Retrieve "+ OPENID_CONFIGURATION_INFORMATION +" for OpenID Provider from the " +
                ".well-known/openid-configuration path. Verify that the issuer in the "+ PROVIDER_CONFIGURATION +" matches the one returned by WebFinger.",
                "expected_result": "Identify that the issuers are not matching and reject the provider configuration."
            },
            "rp-discovery-openid_configuration": {
                "short_description": "Uses \"Provider Configuration Information\"",
                "profiles": [CONFIG, DYNAMIC],
                "detailed_description": "Retrieve and use the " + OPENID_CONFIGURATION_INFORMATION + ".",
                "expected_result": "Read and use the JSON object returned from the OpenID Connect Provider."
            },
            "rp-discovery-mismatching_issuers": {
                "short_description": "Rejects ID Token with iss Not Matching Discovered issuer",
                "profiles": [CONFIG, DYNAMIC],
                "detailed_description": "The Relying Party should obtain an ID token and compare iss value to issuer in the " + OPENID_PROVIDER_METADATA,
                "expected_result": "Rejects ID Token when iss and issuer values differ"
            },
            "rp-discovery-jwks_uri_keys": {
                "short_description": "Uses keys discovered with jwks_uri value",
                "profiles": [CONFIG, DYNAMIC],
                "detailed_description": "The Relying Party uses keys from the jwks_uri which has been obtained from the " + OPENID_PROVIDER_METADATA + ".",
                "expected_result": "Should be able to verify signed responses and/or encrypt requests using obtained keys."
            }
        }],
        ["Dynamic Client Registration", {
            "rp-registration-dynamic": {
                "short_description": "Uses dynamic registration",
                "profiles": [DYNAMIC],
                "detailed_description": "Use the " + CLIENT_REGISTRATION_ENDPOINT + " in order to dynamically " +
                "register the Relying Party.",
                "expected_result": "Get a " + CLIENT_REGISTRATION_RESPONSE + "."
            },
            "rp-registration-redirect_uris": {
                "short_description": "Registration request has redirect_uris",
                "profiles": [DYNAMIC],
                "detailed_description": "Set the redirect_uris parameter of the "+ CLIENT_METADATA +" in a registration request.",
                "expected_result": "Get a " + CLIENT_REGISTRATION_RESPONSE + "."
            },
            "rp-registration-well_formed_jwk": {
                "short_description": "Keys are published as a well-formed JWK Set",
                "profiles": [DYNAMIC],
                "detailed_description": "The keys published by the Relying Party should follow the " + JSON_WEB_KEY_SET_FORMAT + ".",
                "expected_result": "Get a " + CLIENT_REGISTRATION_RESPONSE + "."
            },
            "rp-registration-uses_https_endpoints": {
                "short_description": "Uses HTTPS for all endpoints",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Only register URLs using the https scheme for all endpoints in the " +  CLIENT_METADATA + ".",
                "expected_result": "No endpoints not supporting HTTPS."
            }
        }],
        ["Response type and response mode", {
            "rp-response_type-code": {
                "short_description": "Can make request using response_type 'code'",
                "profiles": [BASIC],
                "detailed_description": "Make an authentication request using the " + AUTHORIZATION_CODE_FLOW + ".",
                "expected_result": "An " + CODE_AUTHENTICATION_RESPONSE + " containing an authorization code."
            },
            "rp-response_type-id_token": {
                "short_description": "Can make request using response_type 'id_token'",
                "profiles": [IMPLICIT],
                "detailed_description": "Make an authentication request using the " + IMPLICIT_FLOW +
                ", specifying the "+ RESPONSE_TYPE +" as 'id_token'."  ,
                "expected_result": "An " + IMPLICIT_AUTHENTICATION_RESPONSE + " containing an " + ID_TOKEN_IMPLICIT_FLOW + "."
            },
            "rp-response_type-id_token+token": {
                "short_description": "Can make request using response_type 'id_token token'",
                "profiles": [IMPLICIT],
                "detailed_description": "Make an authentication request using the " + IMPLICIT_FLOW +
                ", specifying the "+ RESPONSE_TYPE +" as 'id_token token'"  ,
                "expected_result": "An " + IMPLICIT_AUTHENTICATION_RESPONSE + " containing an " + ID_TOKEN_IMPLICIT_FLOW + " and an Access Token."
            },
            "rp-response_mode-form_post": {
                "short_description": "Can make request using response_type='id_token token' and response_mode='form_post'",
                "detailed_description": "Make an authentication request with the "+ RESPONSE_TYPE +
                " set to 'id_token token' and the "+ RESPONSE_MODE +" set to " + FORM_POST + ".",
                "expected_result": "HTML form post response processed, resulting in query encoded parameters."
            },
            "rp-response_type-self_issued": {
                "short_description": "Can use Self-Issued OpenID Provider",
                "profiles": [SELF_ISSUED],
                "detailed_description": "Make an authentication request to a " + SELF_ISSUED_OPENID_PROVIDERS + ".",
                "expected_result": "An " + SELF_ISSUED_AUTH_RESPONSE + " containing an " + SELF_ISSUED_ID_TOKEN + "."
            }
        }],
        ["Claims Request Parameter", {
            "rp-claims_request-id_token_claims": {
                "short_description": "Can request and use claims in ID Token using the 'claims' request parameter",
                "detailed_description": "Ask for a specific claim using the "+ CLAIMS_REQUEST_PARAMETER +
                ". Retrieve the claims from an ID Token, either by making a " + TOKEN_REQUEST + " or by using " + IMPLICIT_FLOW + ".",
                "expected_result": "An " + ID_TOKEN + " containing the requested claim."
            },
            "rp-claims_request-request_userinfo": {
                "short_description": "Can request and use claims in UserInfo Response using the 'claims' request parameter",
                "detailed_description": "Ask for a specific claim using the "+ CLAIMS_REQUEST_PARAMETER +
                ". Retrieve the claims by making a " + USERINFO_REQUEST + ".",
                "expected_result": "A " + USERINFO_RESPONSE + " containing the requested claim."
            }
        }],
        ["request_uri Request Parameter", {
            "rp-request_uri-enc": {
                "short_description": "Can use request_uri request parameter with encrypted request",
                "detailed_description": "Pass a "+ REQUEST_OBJECT_BY_REFERENCE + ", using the " +
                "request_uri parameter. " + ENCRYPT_THE_REQUEST_OBJECT +" using the 'RSA1_5' and 'A128CBC-HS256' algorithms.",
                "expected_result": "An authentication response to the encrypted request passed using the request_uri request parameter."
            },
            "rp-request_uri-sig+enc": {
                "short_description": "Can use request_uri request parameter with signed and encrypted request",
                "detailed_description": "Pass a "+ REQUEST_OBJECT_BY_REFERENCE +", using the " +
                "request_uri parameter. "+ SIGN_THE_REQUEST_OBJECT +" using the 'RS256' algorithm, then " + ENCRYPT_THE_REQUEST_OBJECT +" using the 'RSA1_5' and 'A128CBC-HS256' algorithms.",
                "expected_result": "An authentication response to the signed and encrypted request passed using the request_uri request parameter."
            },
            "rp-request_uri-unsigned": {
                "short_description": "Can use request_uri request parameter with unsigned request",
                "profiles": [DYNAMIC_OPTIONAL],
                "detailed_description": "Pass a "+ REQUEST_OBJECT_BY_REFERENCE +", using the " +
                "request_uri parameter. The Request Object should be signed using the algorithm 'none' (" +UNSECURED_JWS + ").",
                "expected_result": "An authentication response to the unsigned request passed using the request_uri request parameter."
            },
            "rp-request_uri-sig": {
                "short_description": "Can use request_uri request parameter with signed request",
                "profiles": [DYNAMIC_OPTIONAL],
                "detailed_description": "Pass a "+ REQUEST_OBJECT_BY_REFERENCE + ", using the " +
                "request_uri parameter. "+ SIGN_THE_REQUEST_OBJECT +" using the 'RS256' algorithm.",
                "expected_result": "An authentication response to the signed request passed using the request_uri request parameter."
            }
        }],
        ["Third Party Initiated Login", {
            "rp-support_3rd_party_init_login": {
                "short_description": "Supports third-party initiated login",
                "detailed_description": "Receive a "+ THIRD_PARTY_INITIATED_LOGIN +" request and send authentication request to the specified OpenID Connect Provider.",
                "expected_result": "An authentication response."
            }
        }],
        ["scope Request Parameter", {
            "rp-scope-contains_openid_scope": {
                "short_description": "'openid' scope value should be present in the Authentication Request",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Always add the "+ OPENID_SCOPE + " value when sending an Authentication Request.",
                "expected_result": "An authentication response."
            },
            "rp-scope-userinfo_claims": {
                "short_description": "Can request and use claims using scope values",
                "profiles": [BASIC_OPTIONAL, IMPLICIT_OPTIONAL, HYBRID_OPTIONAL, SELF_ISSUED_OPTIONAL],
                "detailed_description": REQUEST_CLAIMS_USING_SCOPE_VALUES + ".",
                "expected_result": "A " + USERINFO_RESPONSE + " containing the requested claims. If no access token is issued (when using "
                + IMPLICIT_FLOW + " with response_type='id_token') the " + ID_TOKEN + " contains the requested claims."
            }
        }],
        ["nonce Request Parameter", {
            "rp-nonce-unless_code_flow": {
                "short_description": "Sends 'nonce' unless using code flow",
                "profiles": [IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Always send a " + NONCE_IMPLMENTATION + " as a request parameter while using implicit or hybrid flow. " +
                "Verify the 'nonce' value returned in the " + ID_TOKEN + ".",
                "expected_result": "An " + ID_TOKEN + ", either from the Authorization Endpoint or from the Token Endpoint, containing the same 'nonce' value as passed in the authentication request when using " + HYBRID_FLOW_ID_TOKEN + " or " + IMPLICIT_FLOW_ID_TOKEN + "."
            },
            "rp-nonce-invalid": {
                "short_description": "Rejects ID Token with invalid 'nonce' when valid 'nonce' sent",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Pass a " + NONCE_IMPLMENTATION + " in the Authentication Request. Verify the 'nonce' value " +
                "returned in the " + ID_TOKEN + ".",
                "expected_result": "Identity that the 'nonce' value in the ID Token is invalid and reject the ID Token."
            }
        }],
        ["Client Authentication", {
            "rp-token_endpoint-client_secret_basic": {
                "short_description": "Can make Access Token Request with 'client_secret_basic' authentication",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "Use the '" + CLIENT_SECRET_BASIC + "' method to authenticate at the Authorization Server " +
                "when using the token endpoint.",
                "expected_result": "A " + TOKEN_RESPONSE + ", containing an ID token."
            },
            "rp-token_endpoint-client_secret_jwt": {
                "short_description": "Can make Access Token Request with 'client_secret_jwt' authentication",
                "detailed_description": "Use the '" + CLIENT_SECRET_JWT + "' method to authenticate at the Authorization Server " +
                "when using the token endpoint.",
                "expected_result": "A " + TOKEN_RESPONSE + ", containing an ID token."
            },
            "rp-token_endpoint-client_secret_post": {
                "short_description": "Can make Access Token Request with 'client_secret_post' authentication",
                "detailed_description": "Use the '" + CLIENT_SECRET_POST + "' method to authenticate at the Authorization Server " +
                "when using the token endpoint.",
                "expected_result": "A " + TOKEN_RESPONSE + ", containing an ID token."
            },
            "rp-token_endpoint-private_key_jwt": {
                "short_description": "Can make Access Token Request with 'private_key_jwt' authentication",
                "detailed_description": "Use the '" + PRIVATE_KEY_JWT + "' method to authenticate at the Authorization Server " +
                "when using the token endpoint.",
                "expected_result": "A " + TOKEN_RESPONSE + ", containing an ID token."
            }
        }],
        ["ID Token", {
            "rp-id_token-bad_asym_sig_rs256": {
                "short_description": "Rejects ID Token with invalid asymmetric 'RS256' signature",
                "profiles": [BASIC_OPTIONAL, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Request an ID token and verify its signature using the keys provided by the Issuer.",
                "expected_result": "Identify the invalid signature and reject the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-bad_symmetric_sig_hs256": {
                "short_description": "Rejects ID Token with invalid symmetric 'HS256' signature",
                "detailed_description": "Request an ID token and verify its signature using the " + SYMMETRIC_SIGNATURES + ".",
                "expected_result": "Identify the invalid signature and reject the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-sig+enc": {
                "short_description": "Can request and use signed and encrypted ID Token",
                "detailed_description": "Request an encrypted ID Token (using 'id_token_encrypted_response_alg' and 'id_token_encrypted_response_enc' in registered " + CLIENT_METADATA + "). " +
                "Decrypt the returned the ID Token and verify its signature using the keys published by the Issuer.",
                "expected_result": "Accept the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-sig_none": {
                "short_description": "Can request and use unsigned ID Token",
                "profiles": [BASIC_OPTIONAL, CONFIG_OPTIONAL, DYNAMIC_OPTIONAL],
                "detailed_description": "Register with the provider specifying \"id_token_signed_response_alg='none'\" in the " +
                CLIENT_METADATA + ". Use " + CODE_FLOW + " and retrieve an unsigned ID Token.",
                "expected_result": "Accept the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-bad_c_hash": {
                "short_description": "Rejects ID Token with incorrect 'c_hash' claim when hybrid flow is used",
                "profiles": [HYBRID],
                "detailed_description": "Retrieve Authorization Code and ID Token from the Authorization Endpoint, using " + HYBRID_FLOW + ". Verify the "+ C_HASH +" value in the returned ID token.",
                "expected_result": "Identify the incorrect 'c_hash' value and reject the ID Token after doing " + AUTHORIZATION_CODE_VALIDATION + "."
            },
            "rp-id_token-bad_at_hash": {
                "short_description": "Rejects ID Token with incorrect 'at_hash' claim when response_type='id_token token'",
                "profiles": [IMPLICIT, HYBRID],
                "detailed_description": "Make an authentication request using response_type='id_token token'. Verify the 'at_hash' value in the returned " + ID_TOKEN + ".",
                "expected_result": "Identify the incorrect 'at_hash' value and reject the ID Token after doing " + ACCESS_TOKEN_VALIDATION + "."
            },
            "rp-id_token-mismatching_issuer": {
                "short_description": "Rejects ID Token with incorrect 'iss' claim",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Request an ID token and verify its '" + ISS + "' value.",
                "expected_result": "Identify the incorrect 'iss' value and reject the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-iat": {
                "short_description": "Rejects ID Token without 'iat' claim",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "Request an ID token and verify its '" + IAT + "' value.",
                "expected_result": "Identify the missing 'iat' value and reject the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-bad_es256_sig": {
                "short_description": "Rejects ID Token with invalid asymmetric 'ES256' signature",
                "detailed_description": "Request an ID token and verify its signature using the keys provided by the Issuer.",
                "expected_result": "Identify the invalid signature and reject the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-aud": {
                "short_description": "Rejects ID Token with invalid 'aud' claim",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Request an ID token and compare its "+ AUD +" value to the Relying Party's '" + CLIENT_ID + "'.",
                "expected_result": "Identify that the 'aud' value is missing or doesn't match the 'client_id' and reject the ID Token after doing " + ID_TOKEN_VALIDATION + "."

            },
            "rp-id_token-sub": {
                "short_description": "Rejects ID Token without 'sub' claim",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Request an ID token and verify it contains a " + SUB + " value.",
                "expected_result": "Identify the missing 'sub' value and reject the ID Token."
            },
            "rp-id_token-kid_absent_single_jwks": {
                "short_description": "Accepts ID Token without 'kid' claim in JOSE header if only one JWK supplied in 'jwks_uri'",
                "profiles": [BASIC_OPTIONAL, IMPLICIT, HYBRID],
                "detailed_description": "Request an ID token and verify its signature using the keys provided by the Issuer.",
                "expected_result": "Use the single key published by the Issuer to verify the ID Tokens signature and accept the ID Token after doing " + ID_TOKEN_VALIDATION + "."
            },
            "rp-id_token-kid_absent_multiple_jwks": {
                "short_description": "Rejects ID Token without 'kid' claim in JOSE header if multiple JWKs supplied in 'jwks_uri'",
                "profiles": [BASIC_OPTIONAL, IMPLICIT_REJECTION_ALLOWED, HYBRID_REJECTION_ALLOWED],
                "detailed_description": "Request an ID token and verify its signature using the keys provided by the Issuer.",
                "expected_result": "Identify that the 'kid' value is missing from the JOSE header and that the Issuer publishes " + MULITPLE_KEYS_JWKS + " (referenced by 'jwks_uri'). Reject the ID Token since it can not be determined which key to use to verify the signature."
            }
        }],
        ["Key Rollover", {
            "rp-key_rollover-op_sign_key": {
                "short_description": "Supports rotation of provider's asymmetric signing keys",
                "profiles": [CONFIG, DYNAMIC],
                "detailed_description": "Request an ID Token and verify its signature. Make a new authentication and retrieve another ID Token and verify its signature.",
                "expected_result": "Successfully verify both ID Token signatures, fetching the " + SIGNING_KEY_ROTATION + " if the 'kid' claim in the JOSE header is unknown."
            },
            "rp-key_rollover-rp_sign_key": {
                "short_description": "Can Rollover RP Signing Key",
                "profiles": [DYNAMIC],
                "detailed_description": "The Relying Party should do a "+ SIGNING_KEY_ROLLOVER +" at its jwks_uri location after it has been used by OpenID Connect Provider",
                "expected_result": "OpenID Connect Provider successfully uses the old then new signing key"
            },
            "rp-key_rollover-op_enc_key": {
                "short_description": "Supports rotation of provider's asymmetric encryption keys",
                "detailed_description": "Fetch the issuer's keys from the 'jwks_uri' and make an " + ENCRYPTED_REQUEST +  " using the issuer's encryption keys. " +
                "Fetch the issuer's keys from the jwks_uri again, and make a new encrypted request using the rotated encryption keys.",
                "expected_result": "A successful authentication response to both authentication requests encrypted using rotated encryption keys."
            },
            "rp-key_rollover-rp_enc_key": {
                "short_description": "Can rotate encryption keys",
                "detailed_description": "Request an encrypted ID Token (using 'id_token_encrypted_response_alg' and 'id_token_encrypted_response_enc' in registered "
                + CLIENT_METADATA + ") and decrypt it. Do an "+ ENCRYPTION_KEY_ROLLOVER +" at the Relying Party's 'jwks_uri' after it has been used by the OpenID Connect Provider. " +
                "Make a new request for an encrypted ID Token and decrypt it using the rotated decryption key.",
                "expected_result": "The OpenID Connect Provider successfully uses the rotated key: the first ID Token can decrypted using the first key and the second ID Token can be decrypted using the rolled over key."
            }
        }],
        ["Claim Types", {
            "rp-claims-aggregated": {
                "short_description": "Can handle aggregated user information",
                "detailed_description": "The Relying Party can display "+ AGGREGATED_CLAIMS +" received from OpenID Connect Provider",
                "expected_result": "Receiving UserInfo response"
            },
            "rp-claims-distributed": {
                "short_description": "Handles distributed user information",
                "detailed_description": "The Relying Party can display "+ DISTRIBUTED_CLAIMS +" received from OpenID Connect Provider",
                "expected_result": "Receiving UserInfo response"
            }
        }],
        ["UserInfo Endpoint", {
            "rp-user_info-bearer_header": {
                "short_description": "Accesses UserInfo Endpoint with Header Method",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "While doing the " + USERINFO_REQUEST + " the the Relying Party should send the access token using the " +
                BEARER_HEADER_METHOD,
                "expected_result": "Receiving " + USERINFO_RESPONSE
            },
            "rp-user_info-bearer_body": {
                "short_description": "Accesses UserInfo Endpoint with form-encoded body method",
                "profiles": [BASIC_ALT_TO_HDR_METHOD, IMPLICIT_ALT_TO_HDR_METHOD, HYBRID_ALT_TO_HDR_METHOD],
                "detailed_description": "While doing the " + USERINFO_REQUEST + " the the Relying Party should send the access token using the " +
                FORM_ENCODED_BODY_METHOD,
                "expected_result": "Should receive a " + USERINFO_RESPONSE
            },
            "rp-user_info-sign":{
                "short_description": "Can Request and Use Signed UserInfo Response",
                "profiles": [CONFIG_OPTIONAL, DYNAMIC_OPTIONAL],
                "detailed_description": "The Relying Party should request and use UserInfo Response which has been signed",
                "expected_result": "Should receive and verify the signature of the " + USERINFO_RESPONSE
            },
            "rp-user_info-sig+enc":{
                "short_description": "Can Request and Use Signed and Encrypted UserInfo Response",
                "detailed_description": "The Relying Party should request and use UserInfo Response which are both signed and encrypted",
                "expected_result": "Should receive, verify the signature and decrypt the " + USERINFO_RESPONSE
            },
            "rp-user_info-enc":{
                "short_description": "Can Request and Use Encrypted UserInfo Response",
                "detailed_description": "The Relying Party should request and use UserInfo Response which has been encrypted",
                "expected_result": "Should receive and decrypt the " + USERINFO_RESPONSE
            },
            "rp-user_info-not_query":{
                "short_description": "Does Not Access UserInfo Endpoint with Query Parameter Method",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "While doing a "+ USERINFO_REQUEST +" the Relying party should not send the access token as a Query Parameter, but only as a Bearer Token",
                "expected_result": "Should receive a " + USERINFO_RESPONSE + " without using the Query Parameter method"
            },
            "rp-user_info-bad_sub_claim":{
                "short_description": "Rejects UserInfo with Invalid Sub claim",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "The Relying Party should obtain a "+ USERINFO_RESPONSE +" and compare its 'sub' value to ID Token's 'sub' claim",
                "expected_result": "Should reject UserInfo result when 'sub' value is missing or doesn't match ID Token 'sub' claim"
            }
        }]
    ];

    $scope.category_const = 0;
    $scope.test_const = 1;

    $scope.toggle_more_info_visibility = function (category_index, test_name) {
        var test = $scope.guidlines[category_index][$scope.test_const][test_name];

        if (test.visible == false) {
            test.visible = true;
        }
        else if (test.visible == true) {
            test.visible = false;
        }
    };

    function set_default_test_visibility() {
        for (var j = 0; j < $scope.guidlines.length; j++) {
            var category = $scope.guidlines[j][$scope.test_const];
            var tests = Object.keys(category);
            for (var i = 0; i < tests.length; i++) {
                category[tests[i]]['visible'] = false;
            }
        }
    }

    set_default_test_visibility();

    function convert_to_link(url, text) {
        if (text) {
            return '<a href=' + url + ' target="_blank">' + text + '</a>';
        }
        return '<a href=' + url + ' target="_blank">' + url + '</a>';
    }

    function list_all_tests(){
        var all_tests = [];
        var tests = [];
        for (var j = 0; j < $scope.guidlines.length; j++) {
            var category = $scope.guidlines[j][$scope.test_const];
            tests = Object.keys(category);
            all_tests = all_tests.concat(tests)
        }
        console.log(all_tests)
    }

    list_all_tests()

})
;
