import http.client
import json

from egs.exceptions import (
    ApiKeyExpired,
    ApiKeyInvalid,
    ApiKeyNotFound,
    ServerUnreachable,
    Unauthorized,
)
from egs.internal.authentication.authentication_data import (
    AuthenticationRequest,
    AuthenticationResponse,
)
from egs.internal.client.api_reponse import ApiResponse
from egs.util.string_util import serialize


class EgsCoreApisClient(object):
    def __init__(self, server_url: str, api_key: str):
        self.api_key = api_key
        """ Identify the HTTP Scheme """
        scheme_part = server_url.index("://")
        if scheme_part == -1:
            self.scheme = "http"
        else:
            self.scheme = server_url[:scheme_part]
            server_url = server_url[scheme_part + 3 :]

        """ Identify the prefix """
        url_parts = server_url.split("/")
        if len(url_parts) > 1:
            prefix = "/".join(url_parts[1:])
            if prefix != "":
                prefix = "/" + prefix
            self.prefix = prefix
        else:
            self.prefix = ""

        """ Identify the host and port """
        if ":" in url_parts[0]:
            host_port = url_parts[0].split(":")
            self.server_host = host_port[0]
            self.server_port = int(host_port[1])
        else:
            self.server_host = url_parts[0]
            if self.scheme == "http":
                self.server_port = 80
            else:
                self.server_port = 443

    def exchange_api_key_for_access_token(self) -> AuthenticationResponse:
        """Performs the request authentication"""
        conn = http.client.HTTPConnection(self.server_host, self.server_port)
        if self.scheme == "https":
            conn = http.client.HTTPSConnection(self.server_host, self.server_port)
        req = AuthenticationRequest(api_key=self.api_key)
        payload = json.dumps(req, default=req.request_payload, sort_keys=True)
        headers = {"Content-Type": "application/json"}
        conn.request("POST", self.prefix + "/api/v1/auth", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        response = json.loads(data)
        if res.status == 400:
            raise ApiKeyInvalid(res.status)
        elif res.status == 401:
            if response["message"] == "Api Key has expired":
                raise ApiKeyExpired(response)
            else:
                raise ApiKeyNotFound(response)
        elif res.status != 200:
            raise ServerUnreachable(response)
        return AuthenticationResponse(**response["data"])

    def invoke_sdk_operation(
        self, resource: str, method: str, request: object = None
    ) -> ApiResponse:
        payload = None
        auth = self.exchange_api_key_for_access_token()
        headers = {"Authorization": "Bearer " + auth.token}
        conn = http.client.HTTPConnection(self.server_host, self.server_port)
        if self.scheme == "https":
            conn = http.client.HTTPSConnection(self.server_host, self.server_port)
        if request is not None:
            payload = json.dumps(request, default=lambda o: o.__dict__, sort_keys=True)
            headers["Content-Type"] = "application/json"
        conn.request(method, self.prefix + resource, payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        response = json.loads(data)
        if res.status == 401 or res.status == 403:
            raise Unauthorized(res)
        return ApiResponse(**response)

    def __str__(self):
        return serialize(self)


def new_egs_core_apis_client(server_url: str, api_key: str) -> EgsCoreApisClient:
    return EgsCoreApisClient(server_url, api_key)
