import json
from Classes.user import *
from Classes.message import *
from Classes.chatmessage import *

class Chat:
    def __init__(self, name: str, users: list[User], messages: list[ChatMessage], info: str = ""):
        self.name = name
        self.info = info
        self.users = users
        self.messages = messages

    def save(self):
        with open(f"chats/{self.name}.json", "w") as f:
            f.write(self.to_json())
        f.close()
        return True


    
    def set_info(self, info):
        self.info = info
        self.save()
        return self

    def __repr__(self) -> str:
        return self.to_json()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)