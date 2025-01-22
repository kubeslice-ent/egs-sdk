import json

def serialize(obj: any):
    """Serialize an object to a string."""
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True)