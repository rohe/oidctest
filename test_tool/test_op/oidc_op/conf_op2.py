# Import everything that is supposed to be the same for all instances
from base_conf import *

# -----------------------------------------------------------------
# These you MUST change
# -----------------------------------------------------------------
# The port on which the test tool instance will listen
PORT = 9100

# The hostname of the OP to test
ISS_HOST= "localhost"
# In the HEART case everyone should use HTTPS but ...
ISSUER = "http://{}/oidc_op/".format(ISS_HOST)

# -----------------------------------------------------------------
# This should not be modified. It's here because of the dependency on PORT
BASE = "http://localhost"

REDIRECT_URIS_PATTERN = ["{}authz_cb"]

# -----------------------------------------------------------------
# Presently these should not be changed either.
# In the future we will allow the testers to modify the RP's behavior and then
# we'll need to modify things here.
INFO = {
    "client": {
        #"redirect_uris": ["%sauthz_cb" % BASE],
        "application_type": "web",
        "contact": ["foo@example.com"],
        "webfinger_url": "{}diana".format(ISSUER),
        "webfinger_email": "diana@{}".format(ISS_HOST)
    },
    'srv_discovery_url': ISSUER  # Necessary if webfinger is not supported
}
