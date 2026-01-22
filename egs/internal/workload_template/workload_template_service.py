"""
Workload Template Service.

Provides a service interface and implementation for managing workload templates.
"""

from typing import List, Optional, Protocol

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import BadParameters, ResourceNotFound, UnhandledException
from egs.internal.workload_template.workload_template_types import (
    CreateWorkloadTemplateRequest,
    CreateWorkloadTemplateResponse,
    DeleteWorkloadTemplateResponse,
    GetWorkloadTemplateResponse,
    ListWorkloadTemplateResponse,
    UpdateWorkloadTemplateRequest,
    UpdateWorkloadTemplateResponse,
)

# Reuse types for update parameters
from egs.internal.workload_placement.workload_placement_types import (
    HelmConfig,
    ManifestResource,
)


class IWorkloadTemplateService(Protocol):
    """
    Interface for Workload Template Service.

    Defines the contract for all workload template operations.
    """

    def create(
        self,
        request: CreateWorkloadTemplateRequest,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> CreateWorkloadTemplateResponse:
        """Create a new workload template."""
        ...

    def list(
        self,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> ListWorkloadTemplateResponse:
        """List all workload templates."""
        ...

    def get(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> GetWorkloadTemplateResponse:
        """Get a specific workload template by name."""
        ...

    def update(
        self,
        name: str,
        request: UpdateWorkloadTemplateRequest,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> UpdateWorkloadTemplateResponse:
        """Update a workload template."""
        ...

    def delete(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> DeleteWorkloadTemplateResponse:
        """Delete a workload template."""
        ...


class WorkloadTemplate(IWorkloadTemplateService):
    """
    Workload Template Service implementation.

    Provides methods for creating, listing, getting, updating, and deleting workload templates.

    Usage:
        >>> from egs.workload_template import workloadTemplate
        >>> response = workloadTemplate.create(request)
        >>> templates = workloadTemplate.list()
        >>> template = workloadTemplate.get(name="my-template")
        >>> workloadTemplate.update(name="my-template", request=update_request)
        >>> workloadTemplate.delete(name="my-template")
    """

    _instance: Optional["WorkloadTemplate"] = None

    def __new__(cls) -> "WorkloadTemplate":
        """Singleton pattern - returns the same instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create(
        self,
        request: CreateWorkloadTemplateRequest,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> CreateWorkloadTemplateResponse:
        """
        Create a new workload template.

        Args:
            request: The workload template configuration.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            CreateWorkloadTemplateResponse with the created template details.

        Raises:
            BadParameters: If the request contains invalid parameters.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)
        payload = request.model_dump(by_alias=True, exclude_none=True)

        api_response = auth.client.invoke_sdk_operation(
            "/api/v1/workload-template",
            "POST",
            payload,
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response)
        
        # Type narrowing: create returns a dict
        data = api_response.data if isinstance(api_response.data, dict) else {}
        return CreateWorkloadTemplateResponse.from_api_response(data)

    def list(
        self,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> ListWorkloadTemplateResponse:
        """
        List all workload templates.

        Args:
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            ListWorkloadTemplateResponse with all templates.

        Raises:
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            "/api/v1/workload-template",
            "GET",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response)
        return ListWorkloadTemplateResponse.from_api_response(api_response.data)

    def get(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> GetWorkloadTemplateResponse:
        """
        Get a specific workload template by name.

        Args:
            name: The name of the workload template.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            GetWorkloadTemplateResponse with the template details.

        Raises:
            ResourceNotFound: If the template doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-template/{name}",
            "GET",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
                
        # Type narrowing: get returns a dict
        data = api_response.data if isinstance(api_response.data, dict) else {}
        return GetWorkloadTemplateResponse.from_api_response(data)

    def update(
        self,
        name: str,
        request: UpdateWorkloadTemplateRequest,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> UpdateWorkloadTemplateResponse:
        """
        Update a workload template.

        Args:
            name: The name of the workload template to update.
            request: The update request with fields to update.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            UpdateWorkloadTemplateResponse confirming the update.

        Raises:
            BadParameters: If the request contains invalid parameters.
            ResourceNotFound: If the template doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        payload = request.model_dump(by_alias=True, exclude_none=True)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-template/{name}",
            "PUT",
            payload,
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
        return UpdateWorkloadTemplateResponse.from_api_response(name)

    def delete(
        self,
        name: str,
        authenticated_session: Optional[AuthenticatedSession] = None,
    ) -> DeleteWorkloadTemplateResponse:
        """
        Delete a workload template.

        Args:
            name: The name of the workload template to delete.
            authenticated_session: Optional auth session (uses global if not provided).

        Returns:
            DeleteWorkloadTemplateResponse confirming the deletion.

        Raises:
            ResourceNotFound: If the template doesn't exist.
            UnhandledException: For unexpected server errors.
        """
        auth = egs.get_authenticated_session(authenticated_session)

        api_response = auth.client.invoke_sdk_operation(
            f"/api/v1/workload-template/{name}",
            "DELETE",
        )

        if not 200 <= api_response.status_code < 300:
            self._handle_error(api_response, resource_name=name)
        return DeleteWorkloadTemplateResponse.from_api_response(name)

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
                resource_type="WorkloadTemplate",
                resource_id=resource_name,
            )

        raise UnhandledException(api_response)


# Singleton instance
workloadTemplate = WorkloadTemplate()
