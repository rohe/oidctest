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

    var ISSUER_DISCOVERY_DOC = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#IssuerDiscovery", "OpenID Provider Issuer Discovery");
    var CLIENT_REGISTRATION_ENDPOINT = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#ClientRegistration", "client registration endpoint");
    var CODE_FLOW = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#CodeFlowAuth", "Code flow");
    var IMPLICIT_FLOW = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#ImplicitFlowSteps", "Implicit Flow");
    var BEARER_HEADER_METHOD = convert_to_link("http://tools.ietf.org/html/rfc6750#section-2.1", "Bearer header method");
    var FORM_ENCODED_BODY_METHOD = convert_to_link("http://tools.ietf.org/html/rfc6750#section-2.2", "form-encoded body method");
    var RFC7033 = convert_to_link("http://tools.ietf.org/html/rfc7033#section-7", "RFC7033");
    var URL_SYNTAX = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#URLSyntax", "URL syntax");
    var ACCT_SYNTAX = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#AcctURISyntax", "acct URI syntax");
    var CLIENT_REGISTRATION_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#RegistrationResponse", "Client Registration Response");
    var AUTHORIZATION_CODE_FLOW = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#CodeFlowAuth", "authorization code flow");
    var AUTHENTICATION_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0-17.html#ImplicitAuthResponse", "authentication response");
    var CLIENT_SECRET_BASIC = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication", "client_secret_basic");
    var TOKEN_RESPONSE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#TokenResponse", "token response");
    var USERINFO_REQUEST = convert_to_link("https://openid.net/specs/openid-connect-standard-1_0-21.html#UserInfoRequest", "UserInfo request");
    var USERINFO_RESPONSE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#UserInfo", "UserInfo response");
    var OPENID_PROVIDER_ISSUER_DISCOVERY = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#IssuerDiscovery", "OpenID Provider Issuer Discovery");
    var PROVIDER_CONFIGURATION = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata", "provider configuration");
    var RESPONSE_TYPE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ImplicitAuthRequest", "response_type");
    var FORM_POST = convert_to_link("https://openid.net/specs/oauth-v2-form-post-response-mode-1_0.html#FormPostResponseMode", "form_post");
    var RESPONSE_MODE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest", "response mode");
    var CLIENT_SECRET_JWT = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication", "client_secret_jwt");
    var CLIENT_SECRET_POST = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication", "client_secret_post");
    var PRIVATE_KEY_JWT = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication", "private_key_jwt");
    var ALG_VALUE_EQUAL_TO_NONE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#IDToken", "'alg' value equal to 'none'");
    var AUTHORIZATION_CODE = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#CodeValidation", "authorization code");
    var C_HASH = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#HybridIDToken", "c_hash");
    var AT_HASH = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#HybridIDToken", "at_hash");
    var ACCESS_TOKEN_VALIDATION = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowTokenValidation", "access_token validation");
    var ID_TOKEN_VALIDATION = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation", "ID Token validation");
    var IAT = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#IDToken", "iat");
    var AUD = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#IDToken", "aud");
    var CLIENT_ID = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#RegistrationResponse", "Client ID");
    var SUB = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#IDToken", "sub");
    var CLAIMS_REQUEST_PARAMETER = convert_to_link("https://openid.net/specs/openid-connect-core-1_0.html#ClaimsParameter", "'claims' request parameter");
    var REQUEST_OBJECT_BY_REFERENCE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RequestUriParameter", "Request Object by reference");
    var ENCRYPT_THE_REQUEST_OBJECT = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#EncryptedRequestObject", "Encrypt the Request Object");
    var SIGN_THE_REQUEST_OBJECT = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#SignedRequestObject", "Sign the Request Object");
    var AGGREGATED_CLAIMS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ClaimTypes", "Aggregated Claims");
    var DISTRIBUTED_CLAIMS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ClaimTypes", "Distributed Claims");
    var SELF_ISSUED_OPENID_PROVIDERS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#SelfIssued", "Self-Issued OpenID Providers");
    var HYBRID_FLOW_ID_TOKEN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0-17.html#HybridIDToken", "hybrid flow");
    var IMPLICIT_FLOW_ID_TOKEN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0-17.html#ImplicitIDToken", "implicit flow");
    var ID_TOKEN_VALIDATION_FOR_CODE_FLOW = convert_to_link("http://openid.net/specs/openid-connect-core-1_0-17.html#IDTokenValidation", "ID Token validation for code flow");
    var VALIDATE_THE_NONCE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0-17.html#ImplicitIDTValidation", "validate the nonce");
    var OPENID_SCOPE = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#AuthRequest", "openid scope");
    var REQUEST_CLAIMS_USING_SCOPE_VALUES = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims", "request claims using Scope Values");
    var OPENID_PROVIDER_METADATA = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata", "OpenID Provider Metadata");
    var CLIENT_METADATA = convert_to_link("https://openid.net/specs/openid-connect-registration-1_0.html#ClientMetadata", "Client Metadata");
    var JSON_WEB_KEY_SET_FORMAT = convert_to_link("https://tools.ietf.org/html/draft-ietf-jose-json-web-key-41#section-5", "JSON Web Key Set (JWK Set) Format");
    var THIRD_PARTY_INITIATED_LOGIN = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#ThirdPartyInitiatedLogin", "third-party initiated login");
    var OPENID_CONFIGURATION_INFORMATION = convert_to_link("https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig", "OpenID Provider Configuration Information");
    var SIGNING_KEY_ROLLOVER = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RotateSigKeys", "signing key rollover");
    var ENCRYPTION_KEY_ROLLOVER = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#RotateEncKeys", "encryption key rollover");
    var SINGLE_KEY = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#Signing", "single key");
    var MULTIPLE_KEYS = convert_to_link("http://openid.net/specs/openid-connect-core-1_0.html#Signing", "multiple keys");

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
                "short_description": "Keys are published as a well-formed JWKS",
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
                "short_description": "Can make requests with 'code' response type",
                "profiles": [BASIC],
                "detailed_description": "Tests if an Relying Party can make a authentication request using the " + AUTHORIZATION_CODE_FLOW,
                "expected_result": "A " + AUTHENTICATION_RESPONSE + " containing an authorization code"
            },
            "rp-response_type-id_token": {
                "short_description": "Can make request with 'id_token' response type",
                "profiles": [IMPLICIT],
                "detailed_description": "Tests if an Relying Party can make a authentication request using the " + IMPLICIT_FLOW +
                ". The "+ RESPONSE_TYPE +" should be set to 'id_token'"  ,
                "expected_result": "A authorization response containing an id_token"
            },
            "rp-response_type-id_token+token": {
                "short_description": "Can make request with 'id_token token' response type",
                "profiles": [IMPLICIT],
                "detailed_description": "Tests if an Relying Party can make a authentication request using the " + IMPLICIT_FLOW +
                ". The "+ RESPONSE_TYPE +" should be set to 'id_token token'"  ,
                "expected_result": "A authorization response containing an id_token and an access token"
            },
            "rp-response_mode-form_post": {
                "short_description": "Can make request using response_type='id_token token' and response_mode='form_post'",
                "detailed_description": "Tests if an Relying Party can make a authentication request. The "+ RESPONSE_TYPE +
                " should be set to 'id_token token' and the "+ RESPONSE_MODE +" should be " + FORM_POST,
                "expected_result": "HTML form post response processed resulting in query encoded parameters"
            },
            "rp-response_type-self_issued": {
                "short_description": "Can use Self-Issued OP",
                "profiles": [SELF_ISSUED],
                "detailed_description": "Tests if an Relying Party can make a authentication request to a " + SELF_ISSUED_OPENID_PROVIDERS,
                "expected_result": "A authorization response containing an id_token"
            }
        }],
        ["Claims Request Parameter", {
            "rp-claims_reqest-id_token_claims": {
                "short_description": "Can Request and use claims in ID Token using the 'claims' request parameter",
                "detailed_description": "The Relying Party can ask for a specific claim using the "+ CLAIMS_REQUEST_PARAMETER +". The claim should be returned in a ID Token",
                "expected_result": "The claim should appear in the returned ID Token"
            },
            "rp-id_token-request_userinfo": {
                "short_description": "Can Request UserInfo Claims by using the 'claims' request parameter",
                "detailed_description": "The Relying Party can ask for a specific claim using the "+ CLAIMS_REQUEST_PARAMETER +". The claim should be returned in a UserInfo response",
                "expected_result": "The claim should appear in the UserInfo response"
            }
        }],
        ["request_uri Request Parameter", {
            "rp-request_uri-enc": {
                "short_description": "Can use request_uri request parameter with encrypted request",
                "detailed_description": "The Relying Party can pass a "+ REQUEST_OBJECT_BY_REFERENCE +" using the " +
                "request_uri parameter. "+ ENCRYPT_THE_REQUEST_OBJECT +" using RSA1_5 and A128CBC-HS256 algorithms",
                "expected_result": "Completing the Authorization Request using request_uri Request Parameter"
            },
            "rp-request_uri-sig+enc": {
                "short_description": "Can Use request_uri Request Parameter with Signed and Encrypted Request",
                "detailed_description": "The Relying Party can pass a "+ REQUEST_OBJECT_BY_REFERENCE +" using the " +
                "request_uri parameter. "+ ENCRYPT_THE_REQUEST_OBJECT +" using RSA1_5 and A128CBC-HS256 algorithms and sign it using RS256 algorithm",
                "expected_result": "Completing the Authorization Request using request_uri Request Parameter"
            },
            "rp-request_uri-unsigned": {
                "short_description": "Can Use request_uri Request Parameter with Unsigned Request",
                "profiles": [DYNAMIC_OPTIONAL],
                "detailed_description": "The Relying Party can pass a "+ REQUEST_OBJECT_BY_REFERENCE +" using the " +
                "request_uri parameter. The Request Object should set 'alg' equal to 'none'",
                "expected_result": "Completing the Authorization Request using request_uri Request Parameter"
            },
            "rp-request_uri-sig": {
                "short_description": "Can Use request_uri Request Parameter with Signed Request",
                "profiles": [DYNAMIC_OPTIONAL],
                "detailed_description": "The Relying Party can pass a "+ REQUEST_OBJECT_BY_REFERENCE +" using the " +
                "request_uri parameter. "+ SIGN_THE_REQUEST_OBJECT +" using the RS256 algorithm",
                "expected_result": "Completing the Authorization Request using request_uri Request Parameter"
            }
        }],
        ["Third Party Initiated Login", {
            "rp-support_3rd_party_init_login": {
                "short_description": "Support Third-Party Initiated Login",
                "detailed_description": "Receive "+ THIRD_PARTY_INITIATED_LOGIN +" request and login to the specified OpenID Connect Provider",
                "expected_result": "Successfully logs in to the OpenID Connect Provider"
            }
        }],
        ["scope Request Parameter", {
            "rp-scope-contains_openid_scope": {
                "short_description": "openid scope value should be present in the Authorization Request",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "The Relying Party should always add the "+ OPENID_SCOPE + " value while sending an Authorization Request.",
                "expected_result": "Receiving successful Authorization response"
            },
            "rp-scope-userinfo_claims": {
                "short_description": "Requesting UserInfo Claims with scope values",
                "profiles": [BASIC_OPTIONAL, IMPLICIT_OPTIONAL, HYBRID_OPTIONAL, SELF_ISSUED_OPTIONAL],
                "detailed_description": "The Relying Party should be able to " + REQUEST_CLAIMS_USING_SCOPE_VALUES,
                "expected_result": "Receiving UserInfo response"
            }
        }],
        ["nonce Request Parameter", {
            "rp-nonce-unless_code_flow": {
                "short_description": "Sends nonce request parameter unless using code flow",
                "profiles": [IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "The Relying Party should always send a nonce as a request parameter while using " +
                "implicit or hybrid flow. Since the server is suppose to return the nonce in the ID Token return from " +
                "Authorization Endpoint, see ID Token required claims in " + HYBRID_FLOW_ID_TOKEN + " or " + IMPLICIT_FLOW_ID_TOKEN +
                ". When using Code flow the the nonce is not required, see "+ ID_TOKEN_VALIDATION_FOR_CODE_FLOW,
                "expected_result": "The nonce should be returned in the ID Token when using implicit or hybrid flow"
            },
            "rp-nonce-invalid": {
                "short_description": "Reject ID Token with invalid nonce when nonce valid sent",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "If a nonce value was sent in the Authentication Request the Relying Party " +
                "must "+ VALIDATE_THE_NONCE +" returned in the ID Token.",
                "expected_result": "Should reject the ID Token if the nonce is not valid"
            }
        }],
        ["Client Authentication", {
            "rp-token_endpoint-client_secret_basic": {
                "short_description": "Can make Access Token request with 'client_secret_basic' authentication",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "Tests if a client can authenticate to the authentication server " +
                "when using the token endpoint. In order to authenticate " +
                "the client should be using '" + CLIENT_SECRET_BASIC + "'",
                "expected_result": "A " + TOKEN_RESPONSE + " should be returned containing an ID token"
            },
            "rp-token_endpoint-client_secret_jwt": {
                "short_description": "Can make Access Token request with 'client_secret_jwt' authentication",
                "detailed_description": "Tests if a client can authenticate to the authentication server " +
                "when using the token endpoint. In order to authenticate the client should be using '" + CLIENT_SECRET_JWT + "'",
                "expected_result": "A " + TOKEN_RESPONSE + " should be returned containing an ID token"
            },
            "rp-token_endpoint-client_secret_post": {
                "short_description": "Can Make Access Token Request with 'client_secret_post' Authentication",
                "detailed_description": "Tests if a client can authenticate to the authentication server " +
                "when using the token endpoint. In order to authenticate the client should be using '" + CLIENT_SECRET_POST + "'",
                "expected_result": "A " + TOKEN_RESPONSE + " should be returned containing an ID token"
            },
            "rp-token_endpoint-private_key_jwt": {
                "short_description": "Can Make Access Token Request with 'private_key_jwt' Authentication",
                "detailed_description": "Tests if a client can authenticate to the authentication server " +
                "when using the token endpoint. In order to authenticate the client should be using '" + PRIVATE_KEY_JWT + "'",
                "expected_result": "A " + TOKEN_RESPONSE + " should be returned containing an ID token"
            }
        }],
        ["ID Token", {
            "rp-id_token-bad_asym_sig_rs256": {
                "short_description": "Reject invalid asymmetric ID Token signature, signed with RS256",
                "profiles": [BASIC_OPTIONAL, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "Tests if the Relying Party can identify and reject an ID Token with an " +
                "invalid signature. The ID Token has been signed using the asymmetric algorithm RS256. " +
                "For more information see list item 6 in " + ID_TOKEN_VALIDATION,
                "expected_result": "Identify invalid ID token"
            },
            "rp-id_token-bad_symmetric_sig_hs256": {
                "short_description": "Reject invalid symmetric ID Token signature with HS256",
                "detailed_description": "Tests if the Relying Party can identify and reject an ID Token with an " +
                "invalid signature. The ID Token has been signed using the symmetric algorithm HS256. " +
                "For more information see list item 6 in " + ID_TOKEN_VALIDATION,
                "expected_result": "Identify invalid ID token"
            },
            "rp-id_token-sig+enc": {
                "short_description": "Can request and use signed and encrypted ID Token response",
                "detailed_description": "Tests if the Relying Party can request and use an signed and encrypted ID Token",
                "expected_result": "Retrieve, verify the signature and decrypt the ID token"
            },
            "rp-id_token-sig_none": {
                "short_description": "Can request and use unsigned ID Token response",
                "profiles": [BASIC_OPTIONAL, CONFIG_OPTIONAL, DYNAMIC_OPTIONAL],
                "detailed_description": "Tests if the Relying Party can request and use unsigned ID Tokens. Use "+ CODE_FLOW +
                " and set the " + ALG_VALUE_EQUAL_TO_NONE,
                "expected_result": "Retrieve an unsigned ID Token"
            },
            "rp-id_token-bad_c_hash": {
                "short_description": "Rejects incorrect c_hash from an ID token when code flow is used",
                "profiles": [HYBRID],
                "detailed_description": "Tests if the Relying Party extract an "+ C_HASH +" from an ID token presented as json. It should be used " +
                "to validate the correctness of the " + AUTHORIZATION_CODE,
                "expected_result": "The RP should be able to detect that the c_hash i invalid"
            },
            "rp-id_token-bad_at_hash": {
                "short_description": "Rejects incorrect at_hash when response type equals 'id_token token'",
                "profiles": [IMPLICIT, HYBRID],
                "detailed_description": "Tests if the Relying Party can extract an "+ AT_HASH +" from an ID token " +
                "and it should be used in the " + ACCESS_TOKEN_VALIDATION + ". The response type should be set to 'id_token token'",
                "expected_result": "The RP should be able to detect that the at_hash is invalid"
            },
            //TODO Difference between this test and rp-discovery-mismatching_issuers
            "rp-id_token-mismatching_issuer": {
                "short_description": "Rejects discovered issuer not matching ID Token iss",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "The Relying Party should request an ID token and reject it if the issuer " +
                "identifier for the OpenID Provider isn't matching the issuer in the returned ID Token",
                "expected_result": "Should do a "+ ID_TOKEN_VALIDATION +" and detect that the issuers are not matching"
            },
            "rp-id_token-iat": {
                "short_description": "Reject ID Token without iat claim",
                "profiles": [BASIC, IMPLICIT, HYBRID],
                "detailed_description": "The Relying Party should request an ID token if it does not contain a "+ IAT +" claim it should be rejected",
                "expected_result": "Should do a "+ ID_TOKEN_VALIDATION +" and detect that the iat claim is missing"
            },
            "rp-id_token-bad_es256_sig": {
                "short_description": "Reject Invalid Asymmetric ID Token Signature",
                "detailed_description": "The Relying Party should reject invalid asymmetric ID Token signature which has been signed using the algorithm ES256",
                "expected_result": "Should do a "+ ID_TOKEN_VALIDATION +" and detect that the ID Token signature is invalid"
            },
            "rp-id_token-aud": {
                "short_description": "Reject ID Token with invalid aud claim",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "The Relying Party should request an ID token and compare its "+ AUD +" value to Relying Party's " + CLIENT_ID,
                "expected_result": "Should do a "+ ID_TOKEN_VALIDATION +" and detect when 'aud' claim is missing or doesn't match Client ID"
            },
            "rp-id_token-sub": {
                "short_description": "Reject ID Token without sub claim",
                "profiles": [BASIC, IMPLICIT, HYBRID, SELF_ISSUED],
                "detailed_description": "The Relying Party should request an ID token and reject it if the "+ SUB +" claim is missing",
                "expected_result": "Should detect when the sub claim is missing"
            },
            "rp-id_token-kid_absent_single_jwks": {
                "short_description": "Accept ID Token without kid claim if only one JWK supplied in jwks_uri",
                "profiles": [BASIC_OPTIONAL, IMPLICIT, HYBRID],
                "detailed_description": "If the JWK supplied in jwks_uri only contains a "+ SINGLE_KEY +" the ID Token does not need to contain a kid claim",
                "expected_result": "The Relying Party should be accept the JWK"
            },
            "rp-id_token-kid_absent_multiple_jwks": {
                "short_description": "Reject ID Token without kid claim if multiple JWKs supplied in jwks_uri",
                "profiles": [BASIC_OPTIONAL, IMPLICIT_REJECTION_ALLOWED, HYBRID_REJECTION_ALLOWED],
                "detailed_description": "If there are "+ MULTIPLE_KEYS +" in the referenced JWK Set document, a kid value MUST be provided in the JOSE Header",
                "expected_result": "Accept ID Token containing kid"
            }
        }],
        ["Key Rollover", {
            "rp-key_rollover-op_sign_key": {
                "short_description": "Support OP Signing Key Rollover",
                "profiles": [CONFIG, DYNAMIC],
                "detailed_description": "The OpenID Connect Providera should do a "+ SIGNING_KEY_ROLLOVER +" at its jwks_uri location after it has been used by Relying Party",
                "expected_result": "Relying Party successfully uses the old then new signing key"
            },
            "rp-key_rollover-rp_sign_key": {
                "short_description": "Can Rollover RP Signing Key",
                "profiles": [DYNAMIC],
                "detailed_description": "The Relying Party should do a "+ SIGNING_KEY_ROLLOVER +" at its jwks_uri location after it has been used by OpenID Connect Provider",
                "expected_result": "OpenID Connect Provider successfully uses the old then new signing key"
            },
            "rp-key_rollover-op_enc_key": {
                "short_description": "Support OP Encryption Key Rollover",
                "detailed_description": "The Relying Party should do a "+ ENCRYPTION_KEY_ROLLOVER +" at its jwks_uri location after it has been used by OpenID Connect Provider",
                "expected_result": "Relying Party successfully uses the old then new encryption key"
            },
            "rp-key_rollover-rp_enc_key": {
                "short_description": "Can rollover RP encryption key",
                "detailed_description": "The Relying Party should do a "+ ENCRYPTION_KEY_ROLLOVER +" at its jwks_uri location after it has been used by OpenID Connect Provider",
                "expected_result": "OpenID Connect Provider successfully uses the old then new encryption key"
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
