import inspect
import sys

from fedoidc import ProviderConfigurationResponse
from otest.check import Check
from otest.check import Error
from otest.check import get_protocol_response


class VerifyMetadataStatements(Error):
    """
    Verify that the provider info contains at least one usable a metadata
    statement.
    """
    cid = "verify-metadata-statements"
    msg = ""

    def _func(self, conv):
        inst = get_protocol_response(conv, ProviderConfigurationResponse)[0]

        return {}


def factory(cid):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Check):
            try:
                if obj.cid == cid:
                    return obj
            except AttributeError:
                pass

    # Hierarchy of tests, going upwards ..
    from oidctest.op import check
    return check.factory(cid)
