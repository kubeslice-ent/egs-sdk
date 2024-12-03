
global _authenticated_session
from egs import authentication
from egs import inventory_operations
from egs import workspace
from egs import gpu_requests

authenticate = authentication.authenticate

create_workspace = workspace.create_workspace
delete_workspace = workspace.delete_workspace
list_workspaces = workspace.list_workspaces
get_workspace_kubeconfig = workspace.get_workspace_kubeconfig

workspace_inventory = inventory_operations.workspace_inventory
inventory = inventory_operations.inventory

request_gpu = gpu_requests.request_gpu
cancel_gpu_request = gpu_requests.cancel_gpu_request
update_gpu_request_priority = gpu_requests.update_gpu_request_priority
update_gpu_request_name = gpu_requests.update_gpu_request_name
release_gpu = gpu_requests.release_gpu
gpu_request_status = gpu_requests.gpu_request_status
gpu_request_status_for_workspace = gpu_requests.gpu_request_status_for_workspace


def update_global_session(session):
    global _authenticated_session
    _authenticated_session = session

def get_global_session():
    global _authenticated_session
    return _authenticated_session