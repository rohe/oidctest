from oidctest.op import func
from oidctest.op import oper
from oidctest.op.client import Client
from oidctest.op.func import check_support
from oidctest.op.func import set_webfinger_resource
from oidctest.op.oper import AsyncAuthn
from oidctest.op.oper import Webfinger
from oidctest.session import SessionHandler

from otest.aus.handling_ph import WebIh
from otest.conf_setup import OP_ORDER
from otest.conversation import Conversation
from otest.events import Events
from otest.flow import FlowState
from otest.prof_util import ProfileHandler

from oic.oic.message import factory
from oic.oic.message import ProviderConfigurationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD


def setup_conv():
    entity = Client(client_authn_method=CLIENT_AUTHN_METHOD,
                    verify_ssl=False)
    entity.provider_info = ProviderConfigurationResponse(
        authorization_endpoint="https://example.com",
    )

    cls_factories = {'': oper.factory}
    func_factory = func.factory

    flow_state = FlowState('flows', profile_handler=ProfileHandler,
                           cls_factories=cls_factories,
                           func_factory=func_factory,
                           display_order=OP_ORDER)
    iss = 'https://example.org'
    tag = 'foobar'
    session_handler = SessionHandler(iss, tag,
                                     flows=flow_state,
                                     tool_conf={})  # , rest=rest, **webenv)
    session_handler.iss = iss
    session_handler.tag = tag

    info = WebIh(session=session_handler, profile_handler=ProfileHandler)

    conv = Conversation([], entity, factory, callback_uris=[])
    conv.events = Events()
    conv.tool_config = {}
    return {'conv': conv, 'io': info}


def test_set_webfinger_resource():
    _info = setup_conv()
    _info['conv'].tool_config['webfinger_url'] = 'https://example.com/diana'
    oper = Webfinger(_info['conv'], _info['io'], None, profile='C.T.T.T')
    # inut.profile_handler.webfinger(self.profile)
    set_webfinger_resource(oper, None)

    assert oper.resource == 'https://example.com/diana'


def test_check_support():
    _info = setup_conv()
    _info['conv'].entity.provider_info[
        'token_endpoint_auth_methods_supported'] = ["private_key_jwt"]
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    check_support(oper, {"WARNING": {
        "token_endpoint_auth_methods_supported": "private_key_jwt"}})

    assert oper.fail is False

    check_support(oper, {"WARNING": {
        "token_endpoint_auth_methods_supported": "client_secret_jwt"}})

    assert oper.fail is False
    assert len(oper.conv.events) == 1

    check_support(oper, {"ERROR": {
        "token_endpoint_auth_methods_supported": "client_secret_jwt"}})

    assert oper.fail is True
