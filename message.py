import json
from user import *

class Message(object):
    def __init__(self, sender: User, message_type, content = "", receiver: User = None):
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
    "message": {
        "sender": {
            "username": "username",
            "password": "password",
            "socket": "socket",
            "address": "address",
            "status": "status"
        }
        "type": "<message type>", -- HELLO-FROM, WHO, etc.
        "receiver": "username", -- optional (default to None = server)
        "content": "<message content>"
    }
"""