import json
import time
from Classes.user import User
from Classes.message import Message

class ChatMessage(object):
    def __init__(self, sender: str, receiver: str, time: time.struct_time, content: str):
        self.sender = sender
        self.receiver = receiver
        self.time = time
        self.content = content
    
    def __repr__(self) -> str:
        return self.to_json()

    def as_message(self):
        return Message(User(self.sender), "CHAT", self.content, User(self.receiver))

    def time_as_string(self):
        def add_zero(n: int):
            if n < 10:
                return f"0{n}"
            return str(n)
        
        if not isinstance(self.time, time.struct_time):
            self.time = time.strptime(str(self.time[:-1]), "[%Y, %m, %d, %H, %M, %S, %w, %j]")
        
        return f"{add_zero(self.time.tm_hour)}:{add_zero(self.time.tm_min)}:{add_zero(self.time.tm_sec)}"

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=None)

    def from_json(message: str):
        return ChatMessage(**json.loads(message, cls=ChatMessageDecoder))

class ChatMessageDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if 'time' in dct:
            dct['time'] = time.strptime(str(dct['time'][:-1]), "[%Y, %m, %d, %H, %M, %S, %w, %j]")
        return dct
