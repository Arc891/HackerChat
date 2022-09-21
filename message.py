import json
from user import *

class Message(object):
    def __init__(self, sender: User, message_type: str, content: str = "", receiver: User = None):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
    
    def __repr__(self) -> str:
        return self.to_json()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


"""
Message format:
{
    "message": {
        "sender": {
            "username": "username",
            "password": "password",
            "address": "address",
            "status": "status"
        }
        "type": "<message type>", -- HELLO-FROM, WHO, etc.
        "receiver": "username", -- optional (default to None = server)
        "content": "<message content>"
    }
}


class Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if 'sender' in dct:
            dct['sender'] = User(**dct['sender'])
        if 'receiver' in dct:
            dct['receiver'] = User(**dct['receiver'])
        return dct
"""