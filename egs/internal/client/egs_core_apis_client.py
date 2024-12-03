import http.client
import json

from egs.exceptions import ApiKeyInvalid, ApiKeyExpired, ApiKeyNotFound, ServerUnreachable, Unauthorized
from egs.internal.authentication.authentication_data import AuthenticationRequest, AuthenticationResponse
from egs.internal.client.api_reponse import ApiResponse


class EgsCoreApisClient(object):
    def __init__(self, server_url: str, api_key: str):
        self.scheme = 'http'
        self.server_host = 'host.docker.internal'
        self.server_port = 5000
        self.api_key = api_key

    def exchange_api_key_for_access_token(self) -> AuthenticationResponse:
        """Performs the request authentication"""
        conn = http.client.HTTPConnection(self.server_host, self.server_port)
        req = AuthenticationRequest(api_key=self.api_key)
        payload = json.dumps(req, default=req.request_payload, sort_keys=True)
        headers = {
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/api/v1/auth", payload, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        response = json.loads(data)
        if res.status == 400:
            raise ApiKeyInvalid(res.status)
        elif res.status == 401:
            if response['message'] == 'Api Key has expired':
                raise ApiKeyExpired(response)
            else:
                raise ApiKeyNotFound(response)
        elif res.status != 200:
            raise ServerUnreachable(response)
        return AuthenticationResponse(**response['data'])

    def invoke_sdk_operation(self, resource: str, method: str, request: object = None) -> ApiResponse:
        payload = None
        auth = self.exchange_api_key_for_access_token()
        headers = {
            'Authorization': 'Bearer ' + auth.token
        }
        conn = http.client.HTTPConnection(self.server_host, self.server_port)

        if request is not None:
            payload = json.dumps(request, default=lambda o: o.__dict__, sort_keys=True)
            headers['Content-Type'] = 'application/json'
        conn.request(method, resource, payload, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        response = json.loads(data)
        if res.status == 401 or res.status == 403:
            raise Unauthorized(res)
        return ApiResponse(**response)

def new_egs_core_apis_client(server_url: str, api_key: str) -> EgsCoreApisClient:
    return EgsCoreApisClient(server_url, api_key)
