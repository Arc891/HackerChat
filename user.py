import json
import bcrypt

class User(object):
    def __init__(self, username, password, socket=None, status='offline', address=("127.0.0.1", 5378)):
        self.username = username
        self.password = password
        self.socket = socket
        self.address = address
        self.status = status
    
    def __repr__(self) -> str:
        return self.to_json()

    def verify_login(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)