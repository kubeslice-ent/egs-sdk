
global _authenticated_session
from egs import authentication
from egs import inventory
from egs import workspace
from egs import gpu_requests

authenticate = authentication.authenticate

create_workspace = workspace.create_workspace
delete_workspace = workspace.delete_workspace
list_workspaces = workspace.list_workspaces
get_workspace_kubeconfig = workspace.get_workspace_kubeconfig

workspace_inventory = inventory.workspace_inventory
inventory = inventory.inventory

request_gpu = gpu_requests.request_gpu
cancel_gpu_request = gpu_requests.cancel_gpu_request
update_gpu_request_priority = gpu_requests.update_gpu_request_priority
update_gpu_request_name = gpu_requests.update_gpu_request_name
release_gpu = gpu_requests.release_gpu
gpu_request_status = gpu_requests.gpu_request_status
gpu_request_status_for_workspace = gpu_requests.gpu_request_status_for_workspace