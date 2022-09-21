import json
import os
from typing import Literal

class User(object):
    def __init__(self, username, password: str = "", status: Literal['offline', 'online']='offline', address=("127.0.0.1", 5378), fd = 0):
        self.username = username
        self.password = password
        self.status = status
        self.address = address
        self.fd = fd
    
    def __repr__(self) -> str:
        return self.to_json()

    def save(self):
        with open(f"users/{self.username}.json", "w") as f:
            f.write(self.to_json())
        f.close()
        return True

    def verify_login(self, password):
        with open(f"users/{self.username}.json", "r") as f:
            user = User(**json.loads(f.read()))
        f.close()
        return user.password == password

    def set_status(self, status):
        self.status = status
        self.save()
        return self

    def set_address(self, address):
        self.address = address
        self.save()
        return self

    def set_fd(self, fd):
        self.fd = fd
        self.save()
        return self

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def get_all_users():
        users = []
        for file in os.listdir("users"):
            if file.endswith(".json"):
                with open(f"users/{file}", "r") as f:
                    users.append(User(**json.loads(f.read())))
                f.close()
        return users