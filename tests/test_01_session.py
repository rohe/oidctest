from oidctest import oper
from oidctest import profiles
from oidctest.session import SessionHandler

import flows

__author__ = 'roland'

def _eq(l1,l2):
    return set(l1) == set(l2)

def test_session_init():
    sh = SessionHandler({}, profiles, "C.T.T.T", flows.FLOWS, oper)
    sh.session_init({})
    # Make sure all flows got in there
    assert _eq(sh.session["flow_names"], flows.FLOWS.keys())

def test_session_setup():
    sh = SessionHandler({}, profiles, "C.T.T.T", flows.FLOWS, oper)
    sh.session_init({})

    sh.session_setup(path="rp-discovery-webfinger_acct")


if __name__ == "__main__":
    test_session_init()