from egs.util.string_util import serialize
from egs.internal.client.egs_core_apis_client import EgsCoreApisClient

class AuthenticatedSession(object):
    def __init__(
            self,
            client: EgsCoreApisClient,
            sdk_default = False,
    ):
        self.client = client
        if sdk_default:
            _authenticated_session = self

    def __str__(self):
        return serialize(self)

