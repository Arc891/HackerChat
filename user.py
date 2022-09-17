class User(object):
    def __init__(self, username, password, socket, address):
        self.username = username
        self.password = password
        self.socket = socket
        self.address = address
        self.status = 'offline'