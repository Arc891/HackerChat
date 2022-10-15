import json
import os
from typing import Literal

class User(object):
    def __init__(self, name: str, password: str = "", status: Literal['offline', 'online'] = 'offline', address: tuple[str, int] = None, fd = 0):
        self.name = name
        self.password = password
        self.status = status
        self.address = address
        self.fd = fd
    
    def __repr__(self) -> str:
        return self.to_json()

    def load(name: str):
        if os.path.isfile(f"users/{name}.json"):
            with open(f"users/{name}.json", "r") as f:
                user = User(**json.load(f))
            return user
        else:
            return None

    def save(self):
        with open(f"users/{self.name}.json", "w") as f:
            f.write(self.to_json())
        return self

    def verify_login(self, password: str):
        with open(f"users/{self.name}.json", "r") as f:
            user = User(**json.load(f))
        return user.password == password

    def set_status(self, status: Literal['offline', 'online']):
        self.status = status
        self.save()
        return self

    def set_address(self, address: tuple[str, int]):
        self.address = address
        self.save()
        return self

    def set_fd(self, fd: int):
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
        return users