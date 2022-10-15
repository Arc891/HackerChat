#!/usr/bin/env python3

from Classes.chatmessage import ChatMessage
from Classes.user import User
from Classes.message import Message
from Classes.chat import Chat
from Classes.exceptions import *
import os
import time
import socket
import threading
import json
import string

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

user_chars = string.ascii_letters + string.digits

HOST = '127.0.0.1'
PORT = 5378
HOST_PORT = (HOST, PORT)
server.bind(HOST_PORT)

ONLINE = 0

print("Server turned ON")
server.listen(100)

def new_msg(msg_type: str, sender: User=None, content: str="", receiver: User=None):
    """Quick constructor for new messages to sent to the server"""
    return Message(sender, msg_type, content=content, receiver=receiver).to_json().encode('utf-8')

def error_handler(connection: socket.socket, address, err_type: str):
    print(f"Exception {err_type} sent to {address}.")
    connection.send(new_msg(err_type))
    return

def disconnect_client(user): 
    global ONLINE
    user = user.set_status("offline").set_address(None).set_fd(0)
    ONLINE -= 1
    return

def check_socket(connection):
    while True:
        try:
            connection.send(b'')
        except:
            return
    
    
def client_setup(connection: socket.socket, address):
    global ONLINE
    if ONLINE >= 100:
        connection.send(new_msg("BUSY"))
        return
    
    data = connection.recv(4096)
    msg_data = json.loads(data.decode("utf-8"))

    msg = Message(**msg_data)
    user = User(**msg.sender)

    print(f"[+] {msg.message_type}, {user.name}")

    username = user.name
    
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
            client_thread(connection, address, user)

    elif msg.message_type == "LOGIN":
        if os.path.isfile(f"users/{username}.json"):
            if user.verify_login(user.password):
                connection.send(new_msg("HELLO"))
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
    

def create_chat_name(n1: str, n2: str):
    """Takes 2 usernames and returns them in alphabetical order"""
    ln1 = n1.lower()
    ln2 = n2.lower()
    if ln1[0] < ln2[0]:
        return n1, n2
    elif ln1[0] > ln2[0]:
        return n2, n1
    else:
        return create_chat_name(n1[1:], n2[1:])

def client_thread(connection: socket.socket, address, user: User):
    global ONLINE

    sock_online = threading.Thread(target=check_socket, args=(connection,))
    sock_online.start()

    print(f"User {user.name} has logged in from {address}.")
    user = user.set_status("online").set_address(address).set_fd(connection.fileno())
    ONLINE += 1

    while sock_online.is_alive():       
        try:
            data = connection.recv(4096)
            msg_data = json.loads(data.decode("utf-8"))
            msg = Message(**msg_data)
            print(f"Received {msg.message_type} from {user.name}")
            if msg.message_type == "WHO":                        
                user_string = ""
                users = User.get_all_users()
                for u in users:
                    if u.status == "online":
                        if u.name == user.name:
                            user_string += f"{u.name} (you), "
                        else: user_string += f"{u.name}, "
                
                connection.send(new_msg("WHO-OK", content=user_string[:-2]))
                print(f"Sent WHO-OK {user_string[:-2]} to {address}.")
            
            elif msg.message_type == "SEND":
                send_message = msg.content
                receiver = User(**msg.receiver)
                print(f"Sending message {send_message} to {receiver.name}")
                if not os.path.exists(f"users/{receiver.name}.json"):
                    raise UNKNOWN()
                else:
                    receiver = User.load(receiver.name)
                    u1, u2 = create_chat_name(user.name, receiver.name)
                    
                    chat_name = f"{u1}-{u2}"

                    if not os.path.exists(f"chats/{chat_name}.json"):
                        chat = Chat(f"{chat_name}", [user, receiver], []).save()
                    
                    with open(f"chats/{chat_name}.json", "r") as f:
                        chat = Chat(**json.load(f))
                        add_msg = ChatMessage(user.name, receiver.name, time.localtime(), send_message)
                        chat.add_message(add_msg)

                    connection.send(new_msg("SEND-OK"))
                    if receiver.fd != 0:
                        socket.fromfd(receiver.fd, socket.AF_INET, socket.SOCK_STREAM).send(new_msg("DELIVERY", sender=user, content=send_message))

            elif msg.message_type == "CHAT":
                sender = User(**msg.sender)
                receiver = User(**msg.receiver)

                if not os.path.exists(f"users/{receiver.name}.json"):
                    raise UNKNOWN()
            
                u1, u2 = create_chat_name(sender.name, receiver.name)
                chat_name = f"{u1}-{u2}"
                
                if not os.path.exists(f"chats/{chat_name}.json"):
                    raise BAD_RQST_BODY()
                
                chat = Chat.load(chat_name)
                
                print(f"Sending: {chat.name}: {chat.info}")
                connection.send(new_msg("CHAT-OK", content=chat.to_json(), receiver=sender))

            elif msg.message_type == "LOGOUT":
                disconnect_client(user)
                print("Client disconnected")
                return

            elif not data:
                break
            
            else:
                raise BAD_RQST_HDR()

        except UNKNOWN:
            print("Exception UNKNOWN sent")
            connection.send(new_msg("UNKNOWN"))
        
        except BAD_RQST_BODY:
            print("Exception BAD-RQST-BODY sent")
            connection.send(new_msg("BAD-RQST-BODY"))
        
        except BAD_RQST_HDR:
            print("Exception BAD-RQST-HDR sent")
            connection.send(new_msg("BAD-RQST-HDR"))

        except ConnectionResetError:
            disconnect_client(user)
            print("Client disconnected forcibly")
            return
    
    disconnect_client(user)
    print("Client disconnected")
    return


while True:
    connected, address = server.accept()

    print(connected, address, "has connected.")

    t = threading.Thread(target=client_setup, args=(connected, address))
    t.start()

server.close()