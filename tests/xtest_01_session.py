import importlib

from otest.conf_setup import construct_app_args
from otest.flow import FlowState

from oidctest.op import oper
from oidctest.op import profiles

from oidctest.session import SessionHandler

__author__ = 'roland'

_path, app_args = construct_app_args(args, config, oper, func, profiles,
                                     ent_conf)


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_session_init():
    sh = SessionHandler(profiles, "C.T.T.T", flow_state, oper,
                        tool_conf={'profile': 'C.T.T.T'})
    sh.session_init()
    # Make sure all flows got in there
    assert _eq(sh["flow_names"], flows.FLOWS.keys())


def test_session_setup():
    sh = SessionHandler(profiles, "C.T.T.T", flows.FLOWS, oper,
                        tool_conf={'profile': 'C.T.T.T'})
    sh.session_init()

    sh.session_setup(path="rp-discovery-webfinger_acct")


if __name__ == "__main__":
    test_session_init()
