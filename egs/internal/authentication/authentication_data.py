from egs.util.string_util import serialize

class AuthenticationRequest(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def __str__(self):
        return serialize(self)

    def request_payload(self, obj):
        return {
            'apiKey': self.api_key
        }

class AuthenticationResponse(object):
    def __init__(self, token: str):
        self.token = token

    def __str__(self):
        return serialize(self)

    def response_payload(self, obj):
        return {
            'token': obj['token']
        }


