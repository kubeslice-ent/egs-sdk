"""
Workload Placement Service.

Provides a service interface and implementation for managing workload placements.
"""

from typing import List, Optional, Protocol

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import BadParameters, ResourceNotFound, UnhandledException
from egs.internal.workload_placement.workload_placement_types import (
    CreateWorkloadPlacementRequest,
    CreateWorkloadPlacementResponse,
    DeleteWorkloadPlacementResponse,
    EnableEGSRequest,
    EnableEGSResponse,
    GetWorkloadPlacementResponse,
    HelmConfig,
    ListWorkloadPlacementResponse,
    ManifestResource,
    UpdateWorkloadPlacementRequest,
    UpdateWorkloadPlacementResponse,
)


class IWorkloadPlacementService(Protocol):
    """
    Interface for Workload Placement Service.

    Defines the contract for all workload placement operations.
    """

    def create(
        self,
        request: CreateWorkloadPlacementRequest,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> CreateWorkloadPlacementResponse:
        """Create a new workload placement."""
        ...

    def list(
        self,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> ListWorkloadPlacementResponse:
        """List all workload placements."""
        ...

    def list_by_workspace(
        self,
        workspace_name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> ListWorkloadPlacementResponse:
        """List all workload placements in a workspace."""
        ...

    def get(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> GetWorkloadPlacementResponse:
        """Get a specific workload placement by name."""
        ...

    def update(
        self,
        name: str,
        helm_configs: Optional[List[HelmConfig]] = None,
        manifest_resources: Optional[List[ManifestResource]] = None,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> UpdateWorkloadPlacementResponse:
        """Update a workload placement's helm configs or manifest resources."""
        ...

    def delete(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> DeleteWorkloadPlacementResponse:
        """Delete a workload placement."""
        ...

    def enable_egs(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> EnableEGSResponse:
        """Enable EGS on a workload placement."""
        ...


class WorkloadPlacement(IWorkloadPlacementService):
    """
    Workload Placement Service implementation.

    Provides methods for creating, listing, getting, updating, and deleting workload placements.

    Usage:
        >>> from egs.workload_placement import workloadPlacement
        >>> response = workloadPlacement.create(request)
        >>> all_placements = workloadPlacement.list()
        >>> placements = workloadPlacement.list_by_workspace(workspace_name="pizza")
        >>> placement = workloadPlacement.get(name="my-placement")
        >>> workloadPlacement.update(name="my-placement", helm_configs=[...])
        >>> workloadPlacement.delete(name="my-placement")
    """

    _instance: Optional["WorkloadPlacement"] = None

    def __new__(cls) -> "WorkloadPlacement":
        """Singleton pattern - returns the same instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create(
        self,
        request: CreateWorkloadPlacementRequest,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> CreateWorkloadPlacementResponse:
        """
        Create a new workload placement.

        Args:
            request: The workload placement configuration.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            CreateWorkloadPlacementResponse with the created placement details.

        Raises:
            BadParameters: If the request contains invalid parameters.
            ResourceNotFound: If the workspace or cluster doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)
        payload = request.model_dump(by_alias=True, exclude_none=True)

        api_response = auth.client.invoke_sdk_operation(
            "/api/v1/workload-placement",
            "POST",
            payload,
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response)
        
        # Type narrowing
        data = api_response.data if isinstance(api_response.data, dict) else {}
        return CreateWorkloadPlacementResponse.from_api_response(data)

    def list(
        self,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> ListWorkloadPlacementResponse:
        """
        List all workload placements.

        Args:
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            ListWorkloadPlacementResponse with all placements.

        Raises:
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            "/api/v1/workload-placement",
            "GET",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response)
        
        # Type narrowing: list returns a list
        data = api_response.data if isinstance(api_response.data, list) else []
        return ListWorkloadPlacementResponse.from_api_response(data)

    def list_by_workspace(
        self,
        workspace_name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> ListWorkloadPlacementResponse:
        """
        List all workload placements in a workspace using path parameter.

        Args:
            workspace_name: The workspace to list placements from.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            ListWorkloadPlacementResponse with the list of placements.

        Raises:
            ResourceNotFound: If the workspace doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-placement/workspace/{workspace_name}",
            "GET",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response)
        
        # Type narrowing: list returns a list
        data = api_response.data if isinstance(api_response.data, list) else []
        return ListWorkloadPlacementResponse.from_api_response(data)

    def get(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> GetWorkloadPlacementResponse:
        """
        Get a specific workload placement by name.

        Args:
            name: The name of the workload placement.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            GetWorkloadPlacementResponse with the placement name.

        Raises:
            ResourceNotFound: If the placement doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-placement/get/{name}",
            "GET",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
        
        # Type narrowing
        data = api_response.data if isinstance(api_response.data, dict) else {}
        return GetWorkloadPlacementResponse.from_api_response(data)

    def update(
        self,
        name: str,
        helm_configs: Optional[List[HelmConfig]] = None,
        manifest_resources: Optional[List[ManifestResource]] = None,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> UpdateWorkloadPlacementResponse:
        """
        Update a workload placement's helm configs or manifest resources.

        Args:
            name: The name of the workload placement to update.
            helm_configs: Optional list of helm configurations to update.
            manifest_resources: Optional list of manifest resources to update.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            UpdateWorkloadPlacementResponse confirming the update.

        Raises:
            BadParameters: If the request contains invalid parameters.
            ResourceNotFound: If the placement doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        request = UpdateWorkloadPlacementRequest(
            name=name,
            helmConfigs=helm_configs,
            manifestResources=manifest_resources,
        )
        payload = request.model_dump(by_alias=True, exclude_none=True)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-placement/{name}",
            "PUT",
            payload,
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
        return UpdateWorkloadPlacementResponse.from_api_response(name)

    def delete(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> DeleteWorkloadPlacementResponse:
        """
        Delete a workload placement.

        Args:
            name: The name of the workload placement to delete.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            DeleteWorkloadPlacementResponse confirming the deletion.

        Raises:
            ResourceNotFound: If the placement doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-placement/{name}",
            "DELETE",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
        return DeleteWorkloadPlacementResponse.from_api_response(name)

    def enable_egs(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> EnableEGSResponse:
        """
        Enable EGS on a workload placement.

        Args:
            name: The name of the workload placement.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            EnableEGSResponse confirming the operation.

        Raises:
            ResourceNotFound: If the placement doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        request = EnableEGSRequest(enableEGS=True)
        payload = request.model_dump(by_alias=True, exclude_none=True)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-placement/{name}/enable-egs",
            "PUT",
            payload,
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
        return EnableEGSResponse.from_api_response(name)

    def _handle_error(
        self,
        api_response: object,
        resource_name: Optional[str] = None,
    ) -> None:
        """Handle API error responses."""
        status_code = getattr(api_response, "status_code", 500)

        if status_code == 400:
            raise BadParameters(api_response)

        if status_code == 404:
            raise ResourceNotFound(
                api_response,
                resource_type="WorkloadPlacement",
                resource_id=resource_name,
            )

        raise UnhandledException(api_response)


# Singleton instance
workloadPlacement = WorkloadPlacement()
