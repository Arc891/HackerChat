import socket
import random
import time
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back

# init colors
init()

interface = """\033c
--------------------------------------------------------------------------------------------------
| [*] Welcome to the chatroom!                                                                   |
|                                                                                                |
| Type 'q' to exit.                                                                              |
| Type !who to see who is in the chatroom.                                                       |
| Type @username to send a message to username.                                                  |
|                                                                                                |"""
empty_row =   "|                                                                                                |"
bottom_line = "--------------------------------------------------------------------------------------------------"

colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]


client_color = random.choice(colors)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002 
separator_token = "<SEP>" 

print(interface)
print(empty_row)

s = socket.socket()

print(f"\033[A", end="| ")
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")

s.connect((SERVER_HOST, SERVER_PORT))

print(f"{empty_row}\n\033[A", end="| ")
print("[+] Connected.")
print(f"{empty_row}\n\033[A", end="| ")

name = input("[.] Enter your name: ")

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print(f"{empty_row}\n\033[A", end="| ")
        print(f"{message}")

# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

while True:
    # input message we want to send to the server
    time.sleep(0.1)
    print(f"{empty_row}\n\033[A", end="|")
    to_send =  input(" ")
    print ("\033[A\033[A") 
    # a way to exit the program
    if to_send.lower() == 'q':
        break
    # add the datetime, name & the color of the sender
    date_now = datetime.now().strftime('%H:%M:%S') 
    to_send = f"{client_color}[{date_now}] {name}{separator_token}{to_send}{Fore.RESET}"
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()