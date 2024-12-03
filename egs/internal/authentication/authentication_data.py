class AuthenticationRequest(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def request_payload(self, obj):
        return {
            'apiKey': self.api_key
        }

class AuthenticationResponse(object):
    def __init__(self, token: str):
        self.token = token

    def response_payload(self, obj):
        return {
            'token': obj['token']
        }


