import json
import os

class User(object):
    def __init__(self, username, password: str = "", status='offline', address=("127.0.0.1", 5378)):
        self.username = username
        self.password = password
        self.address = address
        self.status = status
    
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