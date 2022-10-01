from user import *
from message import *
import os
import time
import socket
import threading
import json
import string

class BAD_RQST_BODY(Exception):
    def __init__(self):
        pass

class UNKNOWN(Exception):
    def __init__(self):
        pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

user_chars = string.ascii_letters + string.digits

host = '127.0.0.1'
port = 5378
host_port = (host, port)
server.bind(host_port)

print("Server turned ON")
server.listen(100)

clients = []
usernames = []

def new_msg(msg_type, sender=None, content="", receiver=None):
    return Message(sender, msg_type, content=content, receiver=receiver).to_json().encode('utf-8')

def error_handler(connection, address, err_type):
    print(f"Exception {err_type} sent to {address}.")
    connection.send(new_msg(err_type))
    return

# TODO: Replace clients and usernames for JSON format: update statuses to offline and remove client for next connection
def disconnect_client(connection, user): 
    user = user.set_status("offline").set_address(None).set_fd(0)
    pop_index = 0 - (len(clients) - clients.index(connection))
    clients.pop(pop_index)
    usernames.pop(pop_index)
    return

def check_socket(connection):
    while True:
        try:
            connection.send(b'')
        except:
            return
    
    
def client_setup(connection, address):
    if len(clients) >= 100:
        connection.send(new_msg("BUSY"))
        return
    
    data = connection.recv(4096)
    print(f"Data received from {address}: {data.decode('utf-8')}")
    time.sleep(0.5)
    msg_data = json.loads(data.decode("utf-8"))
    # print(f"Message data: {msg_data}")

    msg = Message(**msg_data)
    user = User(**msg.sender)

    print(f"[+] {msg.message_type}, {user.username}")
    # print(f"Received {msg} from {address}")

    username = user.username
    
    if msg.message_type == "SIGNUP":
        print("New user signing up.")
        for char in username:
            if char not in user_chars:
                error_handler(connection, address, "BAD-RQST-BODY")
                return

        if os.path.isfile(f"users/{username}.json"):
            error_handler(connection, address, "IN-USE")
            return
        else:
            connection.send(new_msg("HELLO"))
            user.save()
            clients.append(connection)
            usernames.append(username)
            client_thread(connection, address, user)

        # if username not in usernames:
        #     clients.append(connection)
        #     usernames.append(username)
        
        # else:

    elif msg.message_type == "LOGIN":
        if os.path.isfile(f"users/{username}.json"):
            if user.verify_login(user.password):
                connection.send(new_msg("HELLO"))
                clients.append(connection)
                usernames.append(username)
                client_thread(connection, address, user)
            else:
                error_handler(connection, address, "BAD-PASS")
                return
        else:
            error_handler(connection, address, "UNKNOWN")
            return

    else:
        print("Unknown message type.")
        error_handler(connection, address, "BAD-RQST-HDR")
        return
    

def client_thread(connection, address, user):
    print(address, "has started it's thread.")    
    time.sleep(0.5)
    sock_online = threading.Thread(target=check_socket, args=(connection,))
    sock_online.start()

    print(f"User {user.username} has logged in from {address}.")
    user = user.set_status("online").set_address(address).set_fd(connection.fileno())

    while sock_online.is_alive():       
        try:
            data = connection.recv(4096)
            msg_data = json.loads(data.decode("utf-8"))
            msg = Message(**msg_data)

            if msg.message_type == "WHO":                        
                user_string = ""
                users = User.get_all_users()
                for u in users:
                    if u.status == "online":
                        if u.username == user.username:
                            user_string += f"{u.username} (you), "
                        else: user_string += f"{u.username}, "
                
                connection.send(new_msg("WHO-OK", content=user_string[:-2]))
                print(f"Sent WHO-OK {user_string[:-2]} to {address}.")
            
            elif msg.message_type == "SEND":
                send_message = msg.content
                receiver = msg.receiver
                            
                if receiver not in usernames:
                    raise UNKNOWN()
                else: 
                    con_index = usernames.index(receiver)
                    sender_index = clients.index(connection)
                    
                    connection.send(new_msg("SEND-OK"))
                    clients[con_index].send(new_msg("DELIVERY", usernames[sender_index], send_message, usernames[con_index]))
                    # clients[con_index].send(("DELIVERY " + usernames[sender_index] + " " +  send_message + "\n").encode("utf-8"))
                    
            elif msg.message_type == "LOGOUT":
                disconnect_client(connection, user)
                print("Client disconnected")
                return

            elif not data:
                break

        except UNKNOWN:
            print("Exception UNKNOWN sent")
            connection.send(new_msg("UNKNOWN"))
            # connection.send(('UNKNOWN\n').encode('utf-8'))
        
        except BAD_RQST_BODY:
            print("Exception BAD-RQST-BODY sent")
            connection.send(new_msg("BAD-RQST-BODY"))
            # connection.send(('BAD-RQST-BODY\n').encode('utf-8'))

        except ConnectionResetError:
            disconnect_client(connection, user)
            print("Client disconnected forcibly")
            return
    
    disconnect_client(connection, user)
    print("Client disconnected")
    return


while True:
    connected, address = server.accept()

    print(connected, address, "has connected.")

    t = threading.Thread(target=client_setup, args=(connected, address))
    t.start()

server.close()