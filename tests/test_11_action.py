from oidctest.tt.action import update_config


def test_1():
    tool_params = ['acr_values', 'claims_locales', 'issuer',
                   'login_hint', 'profile', 'ui_locales', 'webfinger_email',
                   'webfinger_url', 'insecure', 'tag']

    conf = {'sig': False, 'extra': False, 'discover': False, 'register': False,
            'tool': {'return_type': 'code', 'extra': False, 'discover': True,
                     'profile': 'C.F.F.F',
                     'issuer': 'https://idam.metrosystems.net', 'sig': False,
                     'enc': False, 'tag': 'Basic OpenID Provider',
                     'webfinger': True, 'insecure': False, 'register': True},
            'enc': False, 'return_type': 'C', 'client': {'provider_info': {
            'request_object_encryption_enc_values_supported': '',
            'id_token_signing_alg_values_supported': '', 'op_policy_uri': '',
            'end_session_endpoint': '',
            'userinfo_encryption_alg_values_supported': '',
            'grant_types_supported': '',
            'request_object_encryption_alg_values_supported': '',
            'acr_values_supported': '', 'ui_locales_supported': '',
            'display_values_supported': '', 'response_modes_supported': '',
            'userinfo_endpoint': '',
            'userinfo_encryption_enc_values_supported': '',
            'authorization_endpoint': '', 'subject_types_supported': '',
            'request_parameter_supported': '', 'claims_parameter_supported': '',
            'response_types_supported': '',
            'request_object_signing_alg_values_supported': '',
            'token_endpoint_auth_methods_supported': '', 'token_endpoint': '',
            'issuer': 'https://idam.metrosystems.net', 'jwks_uri': '',
            'id_token_encryption_alg_values_supported': '',
            'request_uri_parameter_supported': '',
            'userinfo_signing_alg_values_supported': '',
            'registration_endpoint': '', 'service_documentation': '',
            'claim_types_supported': '', 'require_request_uri_registration': '',
            'id_token_encryption_enc_values_supported': '', 'op_tos_uri': '',
            'scopes_supported': '', 'claims_supported': '',
            'check_session_iframe': '',
            'token_endpoint_auth_signing_alg_values_supported': '',
            'claims_locales_supported': ''}, 'registration_response': {
            'sector_identifier_uri': '', 'grant_types': '',
            'require_auth_time': '', 'registration_client_uri': '',
            'userinfo_encrypted_response_enc': '', 'logo_uri': '',
            'request_object_encryption_enc': '', 'tos_uri': '',
            'userinfo_signed_response_alg': '',
            'id_token_signed_response_alg': '', 'initiate_login_uri': '',
            'id_token_encrypted_response_alg': '', 'contacts': '',
            'default_max_age': '', 'subject_type': '',
            'request_object_encryption_alg': '', 'client_secret': '',
            'client_name': '', 'token_endpoint_auth_signing_alg': '',
            'client_id': '', 'policy_uri': '', 'post_logout_redirect_uris': '',
            'application_type': '', 'client_secret_expires_at': '',
            'redirect_uris': 'https://new-op.certification.openid.net:60012/authz_cb',
            'jwks': '', 'jwks_uri': '', 'response_types': '',
            'default_acr_values': '', 'registration_access_token': '',
            'request_object_signing_alg': '',
            'userinfo_encrypted_response_alg': '', 'request_uris': '',
            'client_uri': '', 'id_token_encrypted_response_enc': '',
            'token_endpoint_auth_method': '', 'client_id_issued_at': ''}},
            'none': False, 'webfinger': False}

    a,b,c,d = update_config(conf, tool_params)

    assert a
