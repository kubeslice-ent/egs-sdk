from egs.internal.authentication.authentication_data import (
    AuthenticationRequest,
    AuthenticationResponse,
)
from egs.internal.gpr.create_gpr_data import CreateGprRequest, CreateGprResponse
from egs.internal.gpr.delete_gpr_data import DeleteGprRequest, DeleteGprResponse
from egs.internal.gpr.gpr_release_data import GprReleaseRequest, GprReleaseResponse
from egs.internal.gpr.list_workspace_gpr_data import (
    GetGprByIdRequest,
    GprData,
    GprStatus,
    ListWorkspaceGprRequest,
    ListWorkspaceGprResponse,
)
from egs.internal.gpr.update_gpr_name_data import (
    UpdateGprNameRequest,
    UpdateGprNameResponse,
)
from egs.internal.gpr.update_gpr_priority_data import (
    UpdateGprPriorityRequest,
    UpdateGprPriorityResponse,
)
from egs.internal.gpr_template.create_gpr_template import CreateGprTemplateRequest
from egs.internal.gpr_template.delete_gpr_template import (
    DeleteGprTemplateRequest,
    DeleteGprTemplateResponse,
)
from egs.internal.gpr_template.list_gpr_templates import ListGprTemplatesRequest
from egs.internal.gpr_template.update_gpr_template import (
    UpdateGprTemplateRequest,
    UpdateGprTemplateResponse,
)
from egs.internal.gpr_template_binding.create_gpr_template_binding import (
    GprTemplateBindingCluster,
)
from egs.internal.gpr_template_binding.delete_gpr_template_binding import (
    DeleteGprTemplateBindingRequest,
    DeleteGprTemplateBindingResponse,
)
from egs.internal.gpr_template_binding.list_gpr_template_binding import (
    ListGprTemplateBindingsRequest,
)
from egs.internal.gpr_template_binding.update_gpr_template_binding import (
    GprTemplateBindingCluster as UpdateCluster,
    UpdateGprTemplateBindingRequest,
)
from egs.internal.inference_endpoint.delete_inference_endpoint_data import (
    DeleteInferenceEndpointRequest,
    DeleteInferenceEndpointResponse,
)
from egs.internal.inference_endpoint.describe_inference_endpoint_data import (
    DescribeInferenceEndpointRequest,
)
from egs.internal.inference_endpoint.list_inference_endpoint_data import (
    ListInferenceEndpointRequest,
)
from egs.internal.inventory.list_inventory_data import ListInventoryRequest
from egs.internal.workspace.create_workspace_data import CreateWorkspaceRequest
from egs.internal.workspace.delete_workspace_data import (
    DeleteWorkspaceRequest,
    DeleteWorkspaceResponse,
)
from egs.internal.workspace.list_workspaces_data import (
    ListWorkspacesRequest,
    Namespace,
    Workspace,
)
from egs.internal.workspace.workspace_kube_config_data import (
    GenerateWorkspaceKubeConfigRequest,
)


def test_authentication_request_payload():
    req = AuthenticationRequest(api_key="k")
    assert req.request_payload(None) == {"apiKey": "k"}
    assert "api_key" in str(req)
    resp = AuthenticationResponse(token="t")
    assert resp.response_payload({"token": "t"}) == {"token": "t"}
    assert "token" in str(resp)


def test_create_gpr_request_and_response():
    req = CreateGprRequest(
        request_name="r",
        workspace_name="ws",
        node_count=1,
        gpu_per_node_count=2,
        memory_per_gpu=40,
        exit_duration="1h",
        priority=1,
        idle_timeout_duration="10m",
        enforce_idle_timeout=False,
        preferred_clusters=["c1"],
        enable_auto_cluster_selection=True,
        enable_auto_gpu_selection=True,
        enable_eviction=True,
        requeue_on_failure=False,
    )
    assert req.preferredClusters == ["c1"]
    assert "gprName" in str(req)
    resp = CreateGprResponse(gprId="id-1", extra="x")
    assert resp.gpr_id == "id-1"
    assert "gpr_id" in str(resp)


def test_delete_and_release_gpr_dtos():
    assert DeleteGprRequest("g1").gprId == "g1"
    assert "gprId" in str(DeleteGprRequest("g1"))
    assert "{}" in str(DeleteGprResponse()) or str(DeleteGprResponse())
    release = GprReleaseRequest("g1")
    assert release.earlyRelease is True
    assert "earlyRelease" in str(release)
    assert str(GprReleaseResponse()) is not None


def test_update_gpr_dtos():
    name_req = UpdateGprNameRequest("g1", "new")
    assert name_req.gprName == "new"
    assert "gprName" in str(name_req)
    assert str(UpdateGprNameResponse()) is not None
    pri_req = UpdateGprPriorityRequest("g1", 9)
    assert pri_req.priority == 9
    assert "priority" in str(pri_req)
    assert str(UpdateGprPriorityResponse()) is not None


def test_list_workspace_gpr_dtos():
    status = GprStatus(
        provisioning_status="Running",
        failure_reason="",
        num_gpus_allocated=2,
        start_timestamp="t0",
        completion_timestamp="",
        cost="0",
        nodes=["n1"],
        internal_state="ok",
        retry_count=0,
        delayed_count=0,
    )
    assert "Running" in str(status)
    data = GprData(
        gpr_id="g1",
        slice_name="ws",
        cluster_name="c1",
        number_of_gpus=2,
        number_of_gpu_nodes=1,
        instance_type="a2",
        memory_per_gpu=40,
        priority=1,
        gpu_sharing_mode="none",
        estimated_start_time="",
        estimated_wait_time="",
        exit_duration="1h",
        early_release=False,
        gpr_name="r1",
        gpu_shape="A100",
        multi_node=False,
        dedicated_nodes=True,
        enable_rdma=False,
        enable_secondary_network=False,
        status=status,
    )
    resp = ListWorkspaceGprResponse([data])
    assert resp.items[0].gpr_id == "g1"
    assert ListWorkspaceGprRequest("ws").workspace_name == "ws"
    assert "workspace_name" in str(ListWorkspaceGprRequest("ws"))
    assert GetGprByIdRequest("g1").gpr_id == "g1"


def test_workspace_dtos():
    req = CreateWorkspaceRequest("ws", ["c1"], ["ns"], "u", "e@x.com")
    assert req.workspaceName == "ws"
    assert "workspaceName" in str(req)
    assert DeleteWorkspaceRequest("ws").workspaceName == "ws"
    assert str(DeleteWorkspaceResponse()) is not None
    assert str(ListWorkspacesRequest()) is not None
    ns = Namespace("ns1", ["c1"])
    assert "ns1" in str(ns)
    ws = Workspace(
        name="ws",
        overlayNetworkDeploymentMode="single",
        maxClusters=1,
        sliceDescription="d",
        clusters=["c1"],
        namespaces=[ns],
    )
    assert "ws" in str(ws)
    kube_req = GenerateWorkspaceKubeConfigRequest("ws", "c1")
    assert kube_req.clusterName == "c1"
    assert "clusterName" in str(kube_req)


def test_gpr_template_dtos():
    req = CreateGprTemplateRequest(
        name="t",
        cluster_name="c",
        gpu_per_node_count=1,
        num_gpu_nodes=1,
        memory_per_gpu=40,
        gpu_shape="A100",
        instance_type="a2",
        exit_duration="1h",
        priority=1,
        enforce_idle_timeout=False,
        enable_eviction=False,
        requeue_on_failure=False,
    )
    assert not hasattr(req, "idleTimeOutDuration")
    assert "name" in str(req)
    assert DeleteGprTemplateRequest("t").gprTemplateName == "t"
    assert str(DeleteGprTemplateResponse()) == "{}"
    assert str(ListGprTemplatesRequest()) is not None
    update = UpdateGprTemplateRequest(
        name="t",
        cluster_name="c",
        number_of_gpus=1,
        instance_type="a2",
        exit_duration="1h",
        number_of_gpu_nodes=1,
        priority=1,
        memory_per_gpu=40,
        gpu_shape="A100",
        enable_eviction=False,
        requeue_on_failure=False,
        enforce_idle_timeout=False,
    )
    assert not hasattr(update, "idleTimeOutDuration")
    assert str(UpdateGprTemplateResponse()) == "{}"


def test_binding_and_inference_dtos():
    cluster = GprTemplateBindingCluster("c1", "t1", ["t1"])
    assert cluster.clusterName == "c1"
    assert "clusterName" in str(cluster)
    assert DeleteGprTemplateBindingRequest("b1").gprTemplateBindingName == "b1"
    assert str(DeleteGprTemplateBindingResponse()) is not None
    assert str(ListGprTemplateBindingsRequest()) is not None
    update_req = UpdateGprTemplateBindingRequest(
        "ws",
        [UpdateCluster("c1", "t1", ["t1"])],
        True,
    )
    assert update_req.clusters[0]["clusterName"] == "c1"
    assert "workspaceName" in str(update_req)

    assert ListInferenceEndpointRequest("ws").workspace == "ws"
    assert "workspace" in str(ListInferenceEndpointRequest("ws"))
    assert DescribeInferenceEndpointRequest("ws", "ep").endpoint == "ep"
    assert "endpoint" in str(DescribeInferenceEndpointRequest("ws", "ep"))
    delete_req = DeleteInferenceEndpointRequest("ep", "ws", "c1")
    assert delete_req.cluster == "c1"
    assert "cluster" in str(delete_req)
    assert str(DeleteInferenceEndpointResponse()) is not None
    assert ListInventoryRequest() is not None
