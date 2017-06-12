## asym-signed-userinfo

Verifies that the UserInfo was signed with a RSA key

## auth_time-check

Check that the auth_time returned in the ID Token is in the expected range.

    :param max_age: Maximum age of the id_token
    :type max_age: int
    :param skew: The allowed skew in seconds
    :type skew: int
    

## authn-response-or-error

Checks that the last response was a JSON encoded authentication or error message

## bare-keys

Dynamic OPs MUST publish their public keys as bare JWK keys

## changed-client-secret

Check whether the client secret has changed or not

## check

No description

## check-X-support

Checks that a specific provider info parameter is supported

## check-acr-support

Checks that the asked for acr are among the supported

## check-authorization-response

Verifies an Authorization response. This is additional constrains besides what
is optional or required.

## check-claims-support

Checks that the asked for scope are among the supported

## check-enc-sig-algorithms

Verify that the ENC/SIG algorithms listed are officially registered.

## check-encrypt-idtoken-alg-support

Checks that the asked for encryption algorithm are among the supported

## check-encrypt-idtoken-enc-support

Checks that the asked for encryption algorithm are among the supported

## check-encrypt-request_object-alg-support

Checks that the asked for encryption algorithm are among the supported

## check-encrypt-userinfo-enc-support

Checks that the asked for encryption algorithm are among the supported

## check-endpoint

Checks that the necessary endpoint exists at a server

## check-error-response

Checks that the HTTP response status is outside the 200 or 300 range or that an
JSON encoded error message has been received

## check-http-response

Checks that the HTTP response status is within the 200 or 300 range. Also does
some extra JSON checks

## check-id_token_signed_response_alg-support

Checks that the asked for id_token_signed_response_alg are among the supported

## check-idtoken-nonce

Verify that the nonce in the IDToken is the same that's included in the
Authorization Request.

## check-keys

Checks that the necessary keys are defined

## check-provider-info

Check that the Provider Info is sound

## check-query-part

Check that a query part send in the Authorization Request is returned in the
Authorization response.

    :param kwargs: key-value pairs that should be present in the query part
    :type kwargs: dictionary
    

## check-redirect-error-response

Checks that the HTTP response status is outside the 200 or 300 range or that an
error message has been received urlencoded in the form of a redirection.

## check-registration-response

Verifies an Registration response. This is additional constrains besides what is
optional or required.

## check-request-parameter-supported-support

Checks that the request parameter is supported

## check-request_uri-parameter-supported-support

Checks that the request parameter is supported

## check-response-mode

Checks that the asked for response mode are among the supported

## check-response-type

Checks that the asked for response type are among the supported

## check-scope-support

Checks that the asked for scope are among the supported

## check-signed-idtoken-support

Checks that the asked for signature algorithms are among the supported

## check-signed-request_object-support

Checks that the asked for signature algorithms are among the supported

## check-signed-userinfo-alg-support

Checks that the asked for encryption algorithm are among the supported

## check-signed-userinfo-support

Checks that the asked for signature algorithms are among the supported

## check-support

Checks that something asked for are supported

## check-token-endpoint-auth-method

Checks that the token endpoint supports the used client authentication method

## check-userid-support

Checks that the asked for acr are among the supported

## check_content_type_header

Verify that the content-type header is what it should be.

## claims-check

Checks if specific claims is present or not

    :param id_token: Claims that should be present in the id_token
    :type id_token: list of strings
    :param required: If the claims are required
    :type required: boolean
    

## compare-idtoken-received-with-check_id-response

Compares the JSON received as a CheckID response with my own interpretation of
the ID Token.

## different_sub

Verifies that the sub value differs between public and pairwise subject types.

## encrypted-idtoken

Verifies that a IDToken was encrypted

## encrypted-userinfo

Verifies that the UserInfo returned was encrypted

## es-signed-idtoken

Verifies that the ID Token was signed with a EC key

## got

Verify that I got the item I expected

    :param where: In which protocol response the claims should occur
    :type where: string
    :param what: Which claims 
    :type what: string
    

## got_id_token_claims

Verify that I got the claims I asked for

    :param claims: claims expected to be in the id_token
    :type claims: list of strings
    

## got_userinfo_claims

Verify that I got the claims I asked for

    :param claims: claims expected to be among the user info
    :type claims: list of strings
    

## interaction-check

A Webpage was displayed for which no known interaction is defined.

## interaction-needed

A Webpage was displayed for which no known interaction is defined.

## is-idtoken-signed

Checks if the id_token is signed

## login-required

Verifies an Authorization error response. The error should be login_required.

## logo_uri_on_page

No description

## missing-redirect

At this point in the flow a redirect back to the client was expected.

## multiple-sign-on

Verifies that multiple authentications was used in the flow

    :param status: Status code returned on error
    :type status: integer
    

## new-encryption-keys

Verifies that two set of encryption keys are not the same

## new-signing-keys

Verifies that two set of signing keys are not the same

## policy_uri_on_page

No description

## providerinfo-has-claims_supported

Check that the claims_supported discovery metadata value is in the provider_info

## providerinfo-has-jwks_uri

Check that the jwks_uri discovery metadata value is in the provider_info

## response-parse

Parsing the response

## same-authn

Verifies that the same authentication was used twice in the flow.

## signed-encrypted-idtoken

Verifies that a IDToken was signed and then encrypted

    :param enc_alg: Key Encryption algorithm
    :type enc_alg: string
    :param enc_enc: Content Encryption algorithm
    :type enc_enc: string
    :param sig_alg: Signature algorithm
    :type sig_alg: string
    

## single-sign-on

Verifies that Single-Sign-On actually works

## sub-claim-configured

No description

## support-discovery

Verifies that an endpoint for Provider Info discovery is configured

## sym-signed-idtoken

Verifies that the IDToken was signed with a symmetric key

## unpack-aggregated-claims

No description

## unsigned-idtoken

Verifies that an IDToken is in fact unsigned, that is signed with the 'none'
algorithm.

## used-acr-value

The acr value in the ID Token

## valid_code

Check that the authorization response contained a valid access code.

## verify-access-token-response

Checks the Access Token response

## verify-aud

No description

## verify-authn-response

Checks that the last response was a JSON encoded authentication message

## verify-bad-request-response

Verifies that the OP returned a 400 Bad Request response containing a Error
message.

## verify-base64url

Verifies that the base64 encoded parts of a JWK is in fact base64url encoded and
not just base64 encoded

## verify-claims

Verifies that the claims returned as UserInfo or in the ID Token is consistent
with what was asked for

    :param userinfo: Whether the method should look for the claims in the user info
    :type userinfo: boolean
    :param id_token: Whether the method should look for the claims in the id_token
    :type id_token: boolean
    
    Example:
        "verify-claims": {
          "id_token": null
        }
    

## verify-different-sub

Verifies that the sub claim returned in the id_token matched the asked for.

## verify-err-response

Verifies that the response received by the client via redirect was an Error
response.

## verify-error

Verifies that an error message was returned and also if it's the correct type.

## verify-error-response

Checks that the last response was a JSON encoded error message

## verify-https-usage

Verify that specific endpoints uses https

    :param endpoints: Which OP endpoints that should be checked
    :type endpoints: list of strings
    

## verify-id-token

Verifies that the IDToken contains what it should

## verify-id_token-userinfo-same-sub

Verify that the sub claim in the ID Token is the same as is provider in the
userinfo

## verify-implicit-reponse

No description

## verify-iss

verify that the iss value given in the discovery response is the same as the
issuer in an IDToken.

## verify-mti-enc-sig-algorithms

Verify that the MTI algorithms appear.

## verify-nonce

Verifies that the nonce received in the IDToken is the same as was given in the
Authorization Request

## verify-op-endpoints-use-https

Verify that all OP endpoints uses https

## verify-op-has-registration-endpoint

Verify that the OP has a registration endpoint

## verify-prompt-none-response

The OP may respond in more than one way and still be within what the spec says.
Effect of prompt=none The Authorization Server MUST NOT display any
authentication or consent user interface pages.

## verify-random-request-response

No description

## verify-redirect_uri-query_component

Checks that a query component in the redirect_uri value that was specified in
the Authorization request are present in the URL used by the OP for the
response.

    :param kwargs: query components (key, value) that was expected
    :type kwargs: dictionary
    

## verify-response

Checks that the last response was one of a possible set of OpenID Connect
Responses

    :param response_cls: Which responses the test tool has received
    :type response_cls: list of strings

    Example:
        "verify-response": {
          "response_cls": [
            "AuthorizationResponse",
            "AccessTokenResponse"
          ]
        }
    

## verify-scopes

Verifies that the claims corresponding to the requested scopes are returned

## verify-signed-idtoken-has-kid

Verifies that the header of a signed IDToken includes a kid claim.

## verify-state

Verifies that the State variable is the same returned as was sent

## verify-sub-value

Verifies that the sub claim returned in the id_token matched the one asked for.

## verify-unknown-client-id-response

No description

## verify-userinfo

Checks that all required information are in the UserInfo. Note that it's not an
error on the OPs behalf if not all information is there.
