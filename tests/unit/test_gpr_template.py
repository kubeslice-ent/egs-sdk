import pytest

from egs.exceptions import UnhandledException
from egs.gpr_template import (
    create_gpr_template,
    delete_gpr_template,
    get_gpr_template,
    list_gpr_templates,
    update_gpr_template,
)
from tests.conftest import make_api_response

CREATE_KWARGS = dict(
    name="tpl-1",
    cluster_name="c1",
    gpu_per_node_count=2,
    num_gpu_nodes=1,
    memory_per_gpu=40,
    gpu_shape="A100",
    instance_type="a2",
    exit_duration="1h",
    priority=5,
    enforce_idle_timeout=True,
    enable_eviction=False,
    requeue_on_failure=True,
    idle_timeout_duration="30m",
)


def test_create_gpr_template_requires_idle_timeout(mock_session):
    with pytest.raises(ValueError, match="idle_timeout_duration"):
        create_gpr_template(
            name="tpl-1",
            cluster_name="c1",
            gpu_per_node_count=2,
            num_gpu_nodes=1,
            memory_per_gpu=40,
            gpu_shape="A100",
            instance_type="a2",
            exit_duration="1h",
            priority=5,
            enforce_idle_timeout=True,
            enable_eviction=False,
            requeue_on_failure=True,
            idle_timeout_duration=None,
            authenticated_session=mock_session,
        )


def test_create_gpr_template_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprTemplateName": "tpl-1"}
    )
    name = create_gpr_template(**CREATE_KWARGS, authenticated_session=mock_session)
    assert name == "tpl-1"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/gpr-template"
    assert method == "POST"
    assert req.name == "tpl-1"
    assert req.idleTimeOutDuration == "30m"


def test_create_gpr_template_without_idle_enforcement(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprTemplateName": "tpl-2"}
    )
    kwargs = dict(CREATE_KWARGS)
    kwargs["enforce_idle_timeout"] = False
    kwargs["idle_timeout_duration"] = None
    name = create_gpr_template(**kwargs, authenticated_session=mock_session)
    assert name == "tpl-2"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert not hasattr(req, "idleTimeOutDuration")


def test_create_gpr_template_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        create_gpr_template(**CREATE_KWARGS, authenticated_session=mock_session)


def test_get_gpr_template_success(mock_session, gpr_template_payload):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data=gpr_template_payload
    )
    result = get_gpr_template("tpl-1", authenticated_session=mock_session)
    assert result.name == "tpl-1"
    assert result.idle_timeout_duration == "30m"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/gpr-template?gprTemplateName=tpl-1"


def test_get_gpr_template_without_idle(mock_session, gpr_template_payload):
    payload = dict(gpr_template_payload)
    payload["enforceIdleTimeOut"] = False
    payload.pop("idleTimeOutDuration", None)
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data=payload
    )
    result = get_gpr_template("tpl-1", authenticated_session=mock_session)
    assert result.enforce_idle_timeout is False
    assert not hasattr(result, "idle_timeout_duration")


def test_get_gpr_template_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        get_gpr_template("tpl-1", authenticated_session=mock_session)


def test_list_gpr_templates_success(mock_session, gpr_template_payload):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"items": [gpr_template_payload]}
    )
    result = list_gpr_templates(authenticated_session=mock_session)
    assert len(result.items) == 1
    assert result.items[0].name == "tpl-1"


def test_list_gpr_templates_empty_items(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})
    result = list_gpr_templates(authenticated_session=mock_session)
    assert result.items == []


def test_list_gpr_templates_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        list_gpr_templates(authenticated_session=mock_session)


def test_update_gpr_template_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    result = update_gpr_template(
        name="tpl-1",
        cluster_name="c1",
        number_of_gpus=2,
        instance_type="a2",
        exit_duration="1h",
        number_of_gpu_nodes=1,
        priority=5,
        memory_per_gpu=40,
        gpu_shape="A100",
        enable_eviction=False,
        requeue_on_failure=True,
        enforce_idle_timeout=True,
        idle_timeout_duration="30m",
        authenticated_session=mock_session,
    )
    assert result is not None
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "PUT"
    assert req.idleTimeOutDuration == "30m"


def test_update_gpr_template_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        update_gpr_template(
            name="tpl-1",
            cluster_name="c1",
            number_of_gpus=2,
            instance_type="a2",
            exit_duration="1h",
            number_of_gpu_nodes=1,
            priority=5,
            memory_per_gpu=40,
            gpu_shape="A100",
            enable_eviction=False,
            requeue_on_failure=True,
            enforce_idle_timeout=False,
            authenticated_session=mock_session,
        )


def test_delete_gpr_template_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    result = delete_gpr_template("tpl-1", authenticated_session=mock_session)
    assert result is not None
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "DELETE"
    assert req.gprTemplateName == "tpl-1"


def test_delete_gpr_template_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        delete_gpr_template("tpl-1", authenticated_session=mock_session)
