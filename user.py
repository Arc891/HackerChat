import json

class User(object):
    def __init__(self, username, password, socket=None, address=("127.0.0.1", 5378)):
        self.username = username
        self.password = password
        self.socket = socket
        self.address = address
        self.status = 'offline'
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)