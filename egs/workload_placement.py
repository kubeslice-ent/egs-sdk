from typing import Any, Dict, List
from urllib.parse import quote

import yaml

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.workload_placement.workload_placement_data import (
    CreateWorkloadPlacementRequest,
    ManifestResource,
    WorkloadPlacementResponse,
    WorkloadPlacementStep,
)


def _validate_required_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _parse_manifest_documents(manifest: Any) -> List[Dict[str, Any]]:
    """Parse a manifest string/object into validated Kubernetes documents."""
    if isinstance(manifest, dict):
        documents = [manifest]
    elif isinstance(manifest, list):
        documents = manifest
    elif isinstance(manifest, str):
        if not manifest.strip():
            raise ValueError("manifest is required")
        try:
            documents = [doc for doc in yaml.safe_load_all(manifest) if doc is not None]
        except yaml.YAMLError as exc:
            raise ValueError(f"invalid Kubernetes YAML/JSON manifest: {exc}") from exc
    else:
        raise ValueError("manifest must be a YAML/JSON string, dictionary, or list of dictionaries")

    if not documents:
        raise ValueError("manifest must contain at least one Kubernetes resource")

    validated = []
    for index, document in enumerate(documents, start=1):
        if not isinstance(document, dict):
            raise ValueError(f"manifest document {index} must be a Kubernetes object")
        if not document.get("apiVersion"):
            raise ValueError(f"manifest document {index} is missing apiVersion")
        if not document.get("kind"):
            raise ValueError(f"manifest document {index} is missing kind")
        metadata = document.get("metadata")
        if not isinstance(metadata, dict) or not metadata.get("name"):
            raise ValueError(f"manifest document {index} is missing metadata.name")
        validated.append(document)

    return validated


def _manifest_resource_names(documents: List[Dict[str, Any]]) -> List[str]:
    """Generate stable, unique Workload Placement step names.

    Kubernetes allows different resource kinds to share metadata.name (for
    example Deployment/foo and Service/foo), while Workload Placement step names
    need to identify a single manifest resource. Preserve metadata.name when it
    is unique and add kind/index only when required to avoid collisions.
    """
    used = set()
    names = []

    for index, document in enumerate(documents, start=1):
        metadata_name = str(document["metadata"]["name"])
        candidate = metadata_name
        if candidate in used:
            kind = str(document["kind"]).lower()
            candidate = f"{metadata_name}-{kind}"
        suffix = 2
        base_candidate = candidate
        while candidate in used:
            candidate = f"{base_candidate}-{suffix}"
            suffix += 1
        used.add(candidate)
        names.append(candidate)

    return names


def create_workload_placement_from_manifest(
        workspace_name: str,
        workload_name: str,
        cluster_names: List[str],
        manifest: Any,
        authenticated_session: AuthenticatedSession = None
) -> WorkloadPlacementResponse:
    """Create a Workload Placement from arbitrary Kubernetes YAML/JSON.

    Multi-document YAML (``---`` separated) is supported. Each Kubernetes
    document is sent as a manifest resource through the existing Workload
    Placement API.
    """
    _validate_required_text(workspace_name, "workspace_name")
    _validate_required_text(workload_name, "workload_name")
    if not isinstance(cluster_names, list) or not cluster_names:
        raise ValueError("cluster_names must contain at least one cluster")
    if any(not isinstance(cluster, str) or not cluster.strip() for cluster in cluster_names):
        raise ValueError("cluster_names must contain non-empty cluster names")

    documents = _parse_manifest_documents(manifest)
    resource_names = _manifest_resource_names(documents)

    manifest_resources = [
        ManifestResource(name=name, manifest=document)
        for name, document in zip(resource_names, documents)
    ]
    steps = [WorkloadPlacementStep(name=name) for name in resource_names]

    req = CreateWorkloadPlacementRequest(
        workspace_name=workspace_name,
        workload_name=workload_name,
        cluster_names=cluster_names,
        steps=steps,
        manifest_resources=manifest_resources,
    )

    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation('/api/v1/workload-placement', 'POST', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkloadPlacementResponse(api_response.data)


def get_workload_placement(
        workload_name: str,
        authenticated_session: AuthenticatedSession = None
) -> WorkloadPlacementResponse:
    _validate_required_text(workload_name, "workload_name")
    auth = egs.get_authenticated_session(authenticated_session)
    path = '/api/v1/workload-placement/get/' + quote(workload_name, safe='')
    api_response = auth.client.invoke_sdk_operation(path, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkloadPlacementResponse(api_response.data)


def list_workload_placements(
        authenticated_session: AuthenticatedSession = None
) -> WorkloadPlacementResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation('/api/v1/workload-placement', 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkloadPlacementResponse(api_response.data)


def list_workload_placements_by_workspace(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
) -> WorkloadPlacementResponse:
    _validate_required_text(workspace_name, "workspace_name")
    auth = egs.get_authenticated_session(authenticated_session)
    path = '/api/v1/workload-placement/workspace/' + quote(workspace_name, safe='')
    api_response = auth.client.invoke_sdk_operation(path, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkloadPlacementResponse(api_response.data)


def delete_workload_placement(
        workload_name: str,
        authenticated_session: AuthenticatedSession = None
) -> WorkloadPlacementResponse:
    _validate_required_text(workload_name, "workload_name")
    auth = egs.get_authenticated_session(authenticated_session)
    path = '/api/v1/workload-placement' + quote(workload_name, safe='')
    api_response = auth.client.invoke_sdk_operation(path, 'DELETE')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkloadPlacementResponse(api_response.data)
