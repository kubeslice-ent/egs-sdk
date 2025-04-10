from egs.exceptions import Unauthorized

global _authenticated_session
from egs import authentication
from egs import inventory_operations
from egs import workspace
from egs import gpu_requests
from egs import inference_endpoint
from egs import api_key
from egs import gpr_template
from egs import gpr_template_binding

authenticate = authentication.authenticate

create_api_key = api_key.create_api_key
delete_api_key = api_key.delete_api_key
list_api_keys = api_key.list_api_keys

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

list_inference_endpoint = inference_endpoint.list_inference_endpoints
create_inference_endpoint = inference_endpoint.create_inference_endpoint
create_inference_endpoint_with_custom_model_spec = inference_endpoint.create_inference_endpoint_with_custom_model_spec
describe_inference_endpoint = inference_endpoint.describe_inference_endpoint
delete_inference_endpoint = inference_endpoint.delete_inference_endpoint

create_gpr_template = gpr_template.create_gpr_template
get_gpr_template = gpr_template.get_gpr_template
list_gpr_templates = gpr_template.list_gpr_templates
update_gpr_template = gpr_template.update_gpr_template
delete_gpr_template = gpr_template.delete_gpr_template

create_gpr_template_binding = gpr_template_binding.create_gpr_template_binding
get_gpr_template_binding = gpr_template_binding.get_gpr_template_binding
list_gpr_template_bindings = gpr_template_binding.list_gpr_template_bindings
update_gpr_template_binding = gpr_template_binding.update_gpr_template_binding
delete_gpr_template_binding = gpr_template_binding.delete_gpr_template_binding

def update_global_session(session):
    global _authenticated_session
    _authenticated_session = session


def get_global_session():
    global _authenticated_session
    return _authenticated_session


def get_authenticated_session(authenticated_session):
    auth = get_global_session()
    if authenticated_session is not None:
        auth = authenticated_session
    if auth is None:
        raise Unauthorized('No authenticated session found')
    return auth


update_global_session(None)
