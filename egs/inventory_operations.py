import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.inventory.list_inventory_data import Inventory, ListInventoryResponse
from egs.internal.inventory.workspace_inventory_usage_data import InventoryUsage, ListWorkspaceInventoryUsageResponse


def inventory(
        authenticated_session: AuthenticatedSession = None
) -> ListInventoryResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation('/api/v1/inventory/list', 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ListInventoryResponse(**api_response.data)


def workspace_inventory(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
) -> ListWorkspaceInventoryUsageResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation('/api/v1/inventory?sliceName=' + workspace_name, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ListWorkspaceInventoryUsageResponse(**api_response.data)
