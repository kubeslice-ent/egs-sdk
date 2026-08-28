"""
Unit tests for egs.continuum.

These tests mock the EGS core-apis client, so they run entirely offline and do
not need a live gateway. Run with:  python -m unittest tests.test_continuum
(from the repository root), or with pytest.
"""
import json
import unittest

import egs
from egs.continuum import (
    create_continuum_group,
    delete_continuum_group,
    get_capacity_landscape,
    get_continuum_group_detail,
    get_continuum_metrics,
    list_continuum_groups,
    update_continuum_group,
)
from egs.exceptions import UnhandledException
from egs.internal.client.api_reponse import ApiResponse


def ok(data):
    return ApiResponse(status="OK", message="", statusCode=200, data=data)


class FakeClient(object):
    """Records the last invocation and returns a queued ApiResponse."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke_sdk_operation(self, resource, method, request=None):
        self.calls.append({"resource": resource, "method": method, "request": request})
        return self.response

    @property
    def last(self):
        return self.calls[-1]

    def body_dict(self):
        """Serialize the last request body the way the real client would."""
        req = self.last["request"]
        if req is None:
            return None
        return json.loads(json.dumps(req, default=lambda o: o.__dict__))


class FakeSession(object):
    def __init__(self, response):
        self.client = FakeClient(response)


class TestContinuum(unittest.TestCase):
    # ---- list ----
    def test_list(self):
        session = FakeSession(ok({
            "continuumGroups": [
                {
                    "name": "Cust. Edge",
                    "label": "on premise edge",
                    "icon": "router",
                    "clusters": ["worker-1", "worker-2"],
                    "createdTimestamp": "2026-01-01T00:00:00Z",
                }
            ]
        }))
        resp = list_continuum_groups(authenticated_session=session)
        self.assertEqual(session.client.last["resource"], "/api/v1/continuum-group/list")
        self.assertEqual(session.client.last["method"], "GET")
        self.assertIsNone(session.client.last["request"])
        self.assertEqual(len(resp.continuum_groups), 1)
        g = resp.continuum_groups[0]
        self.assertEqual(g.name, "Cust. Edge")
        self.assertEqual(g.clusters, ["worker-1", "worker-2"])
        self.assertEqual(g.created_timestamp, "2026-01-01T00:00:00Z")

    def test_list_empty(self):
        session = FakeSession(ok({"continuumGroups": None}))
        resp = list_continuum_groups(authenticated_session=session)
        self.assertEqual(resp.continuum_groups, [])

    # ---- create ----
    def test_create(self):
        session = FakeSession(ok({
            "name": "Telco Far Edge",
            "label": "far edge",
            "icon": "router",
            "clusters": [],
            "createdTimestamp": "2026-02-02T00:00:00Z",
        }))
        g = create_continuum_group(
            "Telco Far Edge", "far edge", "router", authenticated_session=session
        )
        self.assertEqual(session.client.last["resource"], "/api/v1/continuum-group/create")
        self.assertEqual(session.client.last["method"], "POST")
        self.assertEqual(
            session.client.body_dict(),
            {"name": "Telco Far Edge", "label": "far edge", "icon": "router"},
        )
        self.assertEqual(g.name, "Telco Far Edge")
        self.assertEqual(g.clusters, [])

    # ---- update ----
    def test_update_encodes_name_and_sends_only_label_icon(self):
        session = FakeSession(ok({
            "name": "AI Fty./ Hyperscaler",
            "label": "new label",
            "icon": "cloud",
            "clusters": ["w"],
            "createdTimestamp": "t",
        }))
        g = update_continuum_group(
            "AI Fty./ Hyperscaler", "new label", "cloud", authenticated_session=session
        )
        # name goes in the query, url-encoded (space -> %20, / -> %2F)
        self.assertEqual(
            session.client.last["resource"],
            "/api/v1/continuum-group?name=AI%20Fty.%2F%20Hyperscaler",
        )
        self.assertEqual(session.client.last["method"], "PUT")
        # body carries only label + icon, never name
        self.assertEqual(session.client.body_dict(), {"label": "new label", "icon": "cloud"})
        self.assertEqual(g.label, "new label")

    # ---- delete ----
    def test_delete(self):
        session = FakeSession(ok({"message": "deleted", "status": "OK"}))
        resp = delete_continuum_group("Cust. Devices", authenticated_session=session)
        self.assertEqual(
            session.client.last["resource"],
            "/api/v1/continuum-group?name=Cust.%20Devices",
        )
        self.assertEqual(session.client.last["method"], "DELETE")
        self.assertIsNone(session.client.last["request"])
        self.assertEqual(resp.message, "deleted")
        self.assertEqual(resp.status, "OK")

    # ---- metrics (continuum map aggregate) ----
    def test_metrics(self):
        data = {
            "overallMetrics": {"totalGPUs": 7, "allocatedGPUs": 1},
            "tierCards": [{"name": "Cust. Edge", "totalGPUs": 7}],
            "workspaceTierMatrix": [{"workspaceName": "mig-gpr", "tierAllocations": []}],
        }
        session = FakeSession(ok(data))
        resp = get_continuum_metrics(authenticated_session=session)
        self.assertEqual(session.client.last["resource"], "/api/v1/continuum-group/metrics")
        self.assertEqual(session.client.last["method"], "GET")
        self.assertEqual(resp.overall_metrics["totalGPUs"], 7)
        self.assertEqual(resp.tier_cards[0]["name"], "Cust. Edge")
        self.assertEqual(resp.workspace_tier_matrix[0]["workspaceName"], "mig-gpr")

    def test_metrics_missing_blocks_default_empty(self):
        session = FakeSession(ok({}))
        resp = get_continuum_metrics(authenticated_session=session)
        self.assertIsNone(resp.overall_metrics)
        self.assertEqual(resp.tier_cards, [])
        self.assertEqual(resp.workspace_tier_matrix, [])

    # ---- detail ----
    def test_detail(self):
        data = {
            "tierSummary": {"name": "Cust. Edge", "capacityUtilization": 14.29},
            "clusters": [{"name": "worker-1"}],
            "activeWorkloads": [{"name": "wl-1", "status": "Running"}],
        }
        session = FakeSession(ok(data))
        resp = get_continuum_group_detail("Cust. Edge", authenticated_session=session)
        self.assertEqual(
            session.client.last["resource"],
            "/api/v1/continuum-group/detail?name=Cust.%20Edge",
        )
        self.assertEqual(resp.tier_summary["capacityUtilization"], 14.29)
        self.assertEqual(resp.clusters[0]["name"], "worker-1")
        self.assertEqual(resp.active_workloads[0]["name"], "wl-1")

    # ---- capacity landscape ----
    def test_capacity_landscape(self):
        session = FakeSession(ok({"capacityLandscape": {"any": "shape"}}))
        resp = get_capacity_landscape("mig-gpr", authenticated_session=session)
        self.assertEqual(
            session.client.last["resource"],
            "/api/v1/continuum-group/capacity-landscape?workspace=mig-gpr",
        )
        self.assertEqual(session.client.last["method"], "GET")
        self.assertEqual(resp.capacity_landscape, {"any": "shape"})

    # ---- error path ----
    def test_non_200_raises(self):
        session = FakeSession(
            ApiResponse(status="ERR", message="boom", statusCode=500, data=None)
        )
        with self.assertRaises(UnhandledException):
            list_continuum_groups(authenticated_session=session)

    # ---- global session fallback ----
    def test_uses_global_session_when_none_passed(self):
        session = FakeSession(ok({"continuumGroups": []}))
        egs.update_global_session(session)
        try:
            list_continuum_groups()
            self.assertEqual(
                session.client.last["resource"], "/api/v1/continuum-group/list"
            )
        finally:
            egs.update_global_session(None)


if __name__ == "__main__":
    unittest.main()
