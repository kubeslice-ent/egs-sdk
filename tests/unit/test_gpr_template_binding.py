import pytest

from egs.exceptions import UnhandledException
from egs.gpr_template_binding import (
    create_gpr_template_binding,
    delete_gpr_template_binding,
    get_gpr_template_binding,
    list_gpr_template_bindings,
    update_gpr_template_binding,
)
from tests.conftest import make_api_response

CLUSTERS = [
    {
        "clusterName": "c1",
        "defaultTemplateName": "tpl-1",
        "templates": ["tpl-1", "tpl-2"],
    }
]


def test_create_gpr_template_binding_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "name": "ws-1",
            "namespace": "kubeslice-system",
            "clusters": CLUSTERS,
            "enableAutoGPR": True,
        }
    )
    result = create_gpr_template_binding(
        workspace_name="ws-1",
        clusters=CLUSTERS,
        enable_auto_gpr=True,
        authenticated_session=mock_session,
    )
    assert result.name == "ws-1"
    assert result.enable_auto_gpr is True
    assert result.clusters[0].clusterName == "c1"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/gpr-template-binding"
    assert method == "POST"
    assert req.workspaceName == "ws-1"
    assert req.enableAutoGPR is True


def test_create_gpr_template_binding_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        create_gpr_template_binding(
            "ws-1", CLUSTERS, True, authenticated_session=mock_session
        )


def test_get_gpr_template_binding_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "name": "ws-1",
            "clusters": [
                {
                    "clusterName": "c1",
                    "defaultTemplateName": "tpl-1",
                    "templates": ["tpl-1"],
                    "defaultTemplateStatus": "Ready",
                    "templateStatus": {"tpl-1": "Ready"},
                }
            ],
            "enableAutoGPR": False,
        }
    )
    result = get_gpr_template_binding("ws-1", authenticated_session=mock_session)
    assert result.name == "ws-1"
    assert result.clusters[0].defaultTemplateStatus == "Ready"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/gpr-template-binding?gprTemplateBindingName=ws-1"


def test_get_gpr_template_binding_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        get_gpr_template_binding("ws-1", authenticated_session=mock_session)


def test_list_gpr_template_bindings_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "templateBindings": [
                {
                    "name": "ws-1",
                    "clusters": [
                        {
                            "clusterName": "c1",
                            "defaultTemplateName": "tpl-1",
                            "templates": ["tpl-1"],
                            "defaultTemplateStatus": "Ready",
                            "templateStatus": {},
                        }
                    ],
                    "enableAutoGPR": True,
                }
            ]
        }
    )
    result = list_gpr_template_bindings(authenticated_session=mock_session)
    assert len(result.templateBindings) == 1
    assert result.templateBindings[0].name == "ws-1"


def test_list_gpr_template_bindings_empty(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})
    result = list_gpr_template_bindings(authenticated_session=mock_session)
    assert result.templateBindings == []


def test_list_gpr_template_bindings_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        list_gpr_template_bindings(authenticated_session=mock_session)


def test_update_gpr_template_binding_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "name": "ws-1",
            "namespace": "ns",
            "clusters": [
                {
                    "clusterName": "c1",
                    "defaultTemplateName": "tpl-1",
                    "templates": ["tpl-1"],
                    "defaultTemplateStatus": "Ready",
                    "templateStatus": {"tpl-1": "ok"},
                }
            ],
            "enableAutoGPR": True,
        }
    )
    result = update_gpr_template_binding(
        workspace_name="ws-1",
        clusters=CLUSTERS,
        enable_auto_gpr=True,
        authenticated_session=mock_session,
    )
    assert result.name == "ws-1"
    assert result.enable_auto_gpr is True
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "PUT"
    assert req.workspaceName == "ws-1"
    assert isinstance(req.clusters[0], dict)


def test_update_gpr_template_binding_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        update_gpr_template_binding(
            "ws-1", CLUSTERS, False, authenticated_session=mock_session
        )


def test_delete_gpr_template_binding_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    result = delete_gpr_template_binding("ws-1", authenticated_session=mock_session)
    assert result is not None
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "DELETE"
    assert req.gprTemplateBindingName == "ws-1"


def test_delete_gpr_template_binding_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        delete_gpr_template_binding("ws-1", authenticated_session=mock_session)
