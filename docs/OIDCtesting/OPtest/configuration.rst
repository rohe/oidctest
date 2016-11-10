.. _config:

How to do the configuration of an oidctest instance
===================================================

There are a number of different OP types based on their functionality.
They may or may not support Web Finger, dynamic provider information discovery
and dynamic client registration.

Depending on which type an OP belongs to the configuration file will
look differently.
A configuration file consists of three parts.

Part one
--------

The first part contains the PORT, BASE and KEYS specification:

* PORT is which port the test instance will listen on.
* BASE is the basic URL from which the RP specific URLs will be constructed.
* KEYS are a specification of the keys that the RP will have.

An example would be::

    PORT = 60050
    BASE = "http://localhost"
    KEYS = [
        {"key": "../keys/enc.key", "type": "RSA", "use": ["enc"]},
        {"key": "../keys/sig.key", "type": "RSA", "use": ["sig"]},
        {"crv": "P-256", "type": "EC", "use": ["sig"]},
        {"crv": "P-256", "type": "EC", "use": ["enc"]}
    ]

Here the port that the instance will listen on is 60050.
The basic part of the RPs URLs if http://localhost. What that means
when it comes to the resulting URLs depends on whether you're running the
test instance directly visable from the Internet or behind a reverse proxy.
If you're not running a reverse proxy the RPs redirect_uri would be
(given that all defaults are used) http://localhost:60050/authz_cb .
The key specification means that the RP will have access to four own keys.
2 RSA keys (one for signing and one for encryption) and 2 EC keys (again
one for signing and one for encryption). If there are no RSA keys in the
provided file specifications then new keys will be minted and written to the
files. The EC keys will be newly minted every time the test tool is restarted.

Part two
--------

The second part specifies the TOOL configuration.
This is configuration that is needed to run the tests.
The set of attributes depends on which tests one expects to run.

.. Note::TODO list of attributes vs testID

There are two MUST attributes and those are *issuer* and *profile*::

    TOOL = {
        "profile": "C.T.T.T.ns.",
        "issuer": "https://localhost:8040/"
    }


issuer
~~~~~~
The issuer ID of the OpenID Connect Provider

profile
~~~~~~~
The default profile which is always used as the starting point when
a test instance is restarted and no profile is given as a command argument.
More about profile in :ref:`run_profile` .

Part three
----------

The third part then is the RP configuration information.
There is a number of possible attibutes. You should not need to modify
*behaviour* and *preferences*.
What you do have to modify is 'registration_info', 'registration_response'
and 'provider_information'.
Which of these you have to touch depends on if your doing
dynamic provider information discovery and/or dynamic client registration.

behaviour
~~~~~~~~~
*Place holder*

preferences
~~~~~~~~~~~
The RPs preferences.

registration_info
~~~~~~~~~~~~~~~~~
'registration_info' is the information the client will register with the OP
when doing dynamic client registration. The set of attributes that can be
used can be found `here`__:

__ http://openid.net/specs/openid-connect-registration-1_0.html#ClientMetadata

registration_response
~~~~~~~~~~~~~~~~~~~~~
'registration_response' contains the information that was statically
registered with the OP. How this registration happened is completely
out-of-scope for this document

provider_information
~~~~~~~~~~~~~~~~~~~~
'provider_information' is information about the OP that you in some
out-of-band way got hold off. Now, since you're running the OP you should now
how. I don't.

This means that if you're running dynamic provider information discovery and
dynamic client registration you only need *registration_info*.

If you on the other hand is doing dynamic provider information discovery but
static client registration. Then you need to specify *registration_response*.

And finally if you do static provider information discovery and static client
registration then you need to specify *provider_information* and
*registration_response*.


Configuration Example
---------------------

Example configuration for testing an OP that supports both dynamic
provider information discovery and dynamic client registration::

    PORT = 60050
    BASE = "http://locahost"
    KEYS = [
        {"key": "../keys/enc.key", "type": "RSA", "use": ["enc"]},
        {"key": "../keys/sig.key", "type": "RSA", "use": ["sig"]},
        {"crv": "P-256", "type": "EC", "use": ["sig"]},
        {"crv": "P-256", "type": "EC", "use": ["enc"]}
    ]

    TOOL = {
        "profile": "C.T.T.T.ns.",
        "issuer": "https://localhost:8040/"
        "acr_values": "1 2",
        "claims_locales": "en",
        "instance_id": "60050",
        "login_hint": "foobar",
        "ui_locales": "en",
        "webfinger_email": "foobar@localhost:8040",
        "webfinger_url": "https://localhost:8040/foobar",
    }

    CLIENT = {
        "behaviour": {
            "scope": ["openid", "profile", "email", "address", "phone"]
        },
        "preferences": {
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
        "registration_info": {
            "application_name": "OIC test tool",
            "application_type": "web",
            "redirect_uris": ["{}/authz_cb"],
            "contacts": ["roland@example.com"],
            "post_logout_redirect_uris": ["{}/logout"]
        }
    }

More examples can be found in the test_tool/test_op/config_examples
directory in the source distribution of oidctest.