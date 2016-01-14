IDP_BASE = "https://localhost:8088"

INTERACTION = [
    {
        "matches": {
            "url": "%s/sso/redirect" % IDP_BASE,
            "title": 'IDP test login'
        },
        "page-type": "login",
        "control": {
            "type": "form",
            "set": {"login": "roland", "password": "dianakra"}
        }
    }, {
        "matches": {
            "url": "%s/sso/post" % IDP_BASE,
            "title": 'IDP test login'
        },
        "page-type": "login",
        "control": {
            "type": "form",
            "set": {"login": "roland", "password": "dianakra"}
        }
    },
    {
        "matches": {
            "url": "%s/sso/redirect" % IDP_BASE,
            "title": "SAML 2.0 POST"
        },
        "page-type": "other",
        "control": {
            "index": 0,
            "type": "form",
        }
    },
    {
        "matches": {
            "url": "%s/sso/post" % IDP_BASE,
            "title": "SAML 2.0 POST"
        },
        "page-type": "other",
        "control": {
            "index": 0,
            "type": "form",
            "set": {}
        }
    },
    {
        "matches": {
            "url": "%s/slo/soap" % IDP_BASE,
            #"title": "SAML 2.0 POST"
        },
        "page-type": "other",
        "control": {
            "type": "response",
            "pick": {"form": {"action": "%s/sls" % IDP_BASE}}
        }
    },
]
