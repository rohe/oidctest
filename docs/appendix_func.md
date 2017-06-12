## AccessToken

### conditional_execution


    Context: AccessToken/UserInfo
    Action: If the condition is not fulfilled the operation will not be 
    executed.
    
    Example:
        "conditional_execution":{
          "return_type": ["CIT","CI","C","CT"]
        }
        
    

## AsyncAuthn

### acr_value


    Context: AsyncAuthn
    Action: Sets the request attribute 'acr_values' to something configured,
    something gotten from the OP or to the default.
    Example:
        acr_value: null

    :param oper: 
    :param args: 
    :return: 
    

### check_support


    Context: AsyncAuthn
    Action: Verify that the needed support is supported by the OP
    Example:

        check_support: {
          WARNING: {scopes_supported: [phone]}
        }

        check_support: {
          ERROR: {id_token_signing_alg_values_supported: null}
        }

    :param args: A dictionary of dictionaries. {level: {item: value}}
    

### claims_locales


    Context: AsyncAuthn
    Action: Set the request argument 'claims_locales' to something configured or
    use the default.
    Example:
        "claims_locales": null

    :param oper: 
    :param args: 
    :return: 
    

### essential_and_specific_acr_claim


    Context: AsyncAuthn
    Action: Add to the request that an acr claims MUST be returned in the
     ID token. The value of acr is first picked from acr_values_supported in the
     provider info. If not acr_values_supported is given the test tool
     configuration will be used. If that is also missing it will be set to
     whatever args has as value.
    Example:
        "essential_and_specific_acr_claim": "1"

    :param args: A default set of acr values
    

### id_token_hint


    Context: AsyncAuthn
    Action: Will pick up an id_token received in an earlier authorization 
    request and add it to the request argument "id_token_hint"
    Example:
    
        "id_token_hint": null

    

### login_hint


    Context: AsyncAuthn
    Action: Sets the request argument 'login_hint' to a value picked from the
    configuration.
    
    Example:
        "login_hint": null

    :param oper: 
    :param args: 
    :return: 
    

### redirect_uri_with_query_component


    Context: AsyncAuthn
    Action: Add a query component to the redirect_uri
    Example:
        redirect_uri_with_query_component:
            foo: bar

    :param oper: An Operation Instance
    :param kwargs: Values to build the query part from
    

### request_in_file


    Context: AsyncAuthn
    Action: Sets the operation argument 'base_path' to where the request 
     can be found
    Example:
        request_in_file: null

    

### set_discovery_issuer


    Context: AsyncAuthn
    Action: Pick up issuer ID either from static configuration or dynamic
    discovery.

    

### set_essential_arg_claim


    Context: AsyncAuthn
    Action: Specify an essential claim. Whether it should be placed in the
    id_token or returned together with the user info depends on the profile 
    used.
    Example:
        "set_essential_arg_claim": "name"

    :param args: A claim
    

### set_response_where


    Context: AsyncAuthn
    Action: Set where the response is expected to occur dependent on which 
     response_type it is or which it isn't.

    :param response_type:
    :param not_response_type: 
    :param where: Where should the Authroization response occur
    

### specific_acr_claims


    Context: AsyncAuthn
    Action: Use the claims request parameter to specify which acr value should
    be used
    Example:
        specific_acr_claims: '1'

    :param args: A default set of acr_values 
    

### sub_claims


    Context: AsyncAuthn
    Action: Specify a claim for a specific sub value. This is signalling that
     the OP should authenticate a specific subject. The sub value is fetch from
     an id_token received in connection to a previous authorization.
    Example:
        sub_claims: null

    

### ui_locales


    Context: AsyncAuthn
    Action: Set the request argument 'ui_locales' to something configured or
    use the default.
    Example:
        "ui_locales": null

    

## RefreshAccessToken

### set_state


    Context: RefreshAccessToken
    Action: Sets the operation argument 'state' to what has been used
    previously in the session.
    Example:
        "set_state": null

    

## Registration

### multiple_return_uris


    Context: Registration
    
    Action: makes the request contain two redirect_uris. Default is that
    it only contains one.
    
    Example:
        multiple_return_uris: null

    :param oper: An Operation instance
    :param args: None
    

### redirect_uris_with_fragment


    Context: Registration
    Action: Add a fragment component to a redirect_uri
    Example:
        "redirect_uris_with_fragment": {
          "foo": "bar"
        }

    :param kwargs: Values to build the query part from
    

### redirect_uris_with_scheme


    Context: Registration
    Action: Create a redirect_uri with a specific scheme.

    :param args: The scheme to use
    

### static_jwk


    Context: Registration
    Action: Set a static JWKS, remove jwks_uri if specified.
    Example:
        
        static_jwk: null
        
    

### store_sector_redirect_uris


    Context: Registration
    Action: Will store a number of redirectURIs in a file and add a
    "sector_identifier_uri" pointing to that file to the request arguments.
    Example:
        
        store_sector_redirect_uris:
            other_uris:
              - 'https://example.com/op'
              
    :param other_uris: list of complete URLs
    :param redirect_uris: Use default redirect_uris for this entity
    :param extra: Extra relative url paths
    

## Support function

### get_attribute_value


    Context: Support function 
    Action: Picks up values from a given set of ordered attributes 
    Example:

    :param tool_attr: tool configuration attributes.
    :param provider_attr: Provider info attribute
    :param default: If no values could be found use this
    :return: value
    

## UserInfo

### conditional_execution


    Context: AccessToken/UserInfo
    Action: If the condition is not fulfilled the operation will not be 
    executed.
    
    Example:
        "conditional_execution":{
          "return_type": ["CIT","CI","C","CT"]
        }
        
    

## VerifyConfiguration

### check_config


    Context: VerifyConfiguration
    Action:
    Example:
        "check_config": {
          "login_hint": null
        }

    :param args: Dictionary with parameters and values that MUST be in the
    tool configuration
    

## WebFinger

### set_principal


    Context: WebFinger
    Action: Set principal using a specific parameter
    Example:

        set_principal:
            param: webfinger_url
            
    :param param: Value "webfinger_url" or "webfinger_email"
    

### set_webfinger_resource


    Context: WebFinger
    Action: Specifies the webfinger resource. If the OP supports
    webfinger queries then the resource is set to the value of 'webfinger_url'
    or 'webfinger_email' from the test instance configuration.

    Example:
        "set_webfinger_resource": null
        
    
