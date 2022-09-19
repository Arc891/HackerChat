from code import interact
from hashlib import sha256
from user import *
from message import *
import socket
import threading
import time
import os
import getpass

from psutil import boot_time

WAI = "."
INF = "*"
SUC = "+"
ERR = "!"
INP = ">"
SER = "S"

LOGIN = False
SIGNUP = False

HOST = '127.0.0.1'      # The server's hostname or IP address
PORT = 5378             # The port used by the server
host_port = (HOST, PORT)

T_WIDTH = os.get_terminal_size().columns
T_HEIGHT = os.get_terminal_size().lines

LOGO_FULL_WIDTH = 'logo-full-width.txt' # 57 chars wide
LOGO_HALF_WIDTH = 'logo-half-width.txt' # 35 chars wide

UNKNOWN = "UNKNOWN\n".encode("utf-8")
SEND_OK = "SEND-OK\n".encode("utf-8")
DELIVERY = "DELIVERY".encode("utf-8")

"""
Prints an empty row and places the cursor at the start of the line to overwrite it.
"""
def print_empty_row():
    global T_WIDTH
    print(f"| {'':^{T_WIDTH-4}} |")
    print(f"\033[A", end="| ")


def print_line():
    global T_WIDTH
    print("-" * T_WIDTH)


""" 
Custom print function in style of the terminal, 
taking a 2nd parameter which defines the icon between the square brackets. 
"""
def cprint(msg, pre=INF):
    global T_WIDTH
    print_empty_row()
    print(f"[{pre}] {msg:<{T_WIDTH-8}} |")
    # print(f"\033[A", end="| > ")



"""
Custom input function in style of the terminal, 
taking a 2nd parameter checking if the input is going to be a password,
if so, the input will be hidden while typed.
"""
def cinput(msg, pwd=False):
    global T_WIDTH
    print_empty_row()
    if pwd: return getpass.getpass(f"\033[A| [{INP}] {msg}") # Moves cursor up one line and adds layout since getpass() adds a newline
    return input(f"[{INP}] {msg}")

"""
Checks the width of the screen and prints the appropriate logo to the middle of the screen.
"""
def print_logo_middle():
    global T_WIDTH
    # The full logo is 57 characters wide, so accounting for the bars on the side totals to 59 chars to display
    logo_name = LOGO_FULL_WIDTH if T_WIDTH >= 59 else LOGO_HALF_WIDTH 
    with open(logo_name, 'r') as f:
        for line in f:
            print(f"| {line[:-1]:^{T_WIDTH-4}} |")
    f.close()



"""
Prints the welcoming interface when starting the application. 
"""
def print_interface(clear=False):
    global T_WIDTH
    instructions = ['Type !quit to exit.', 
                    'Type !who to see who is in the chatroom.', 
                    'Type @username to send a message to username.']
    
    line = "-" * T_WIDTH
    
    if clear: print("\033c", end="")

    print(line)
    print_logo_middle()
    for i in instructions: cprint(i, INF)
    print(line)



"""
A function to keep track of the terminal width, 
and will resize the current display if the width changes.
"""
def dynamic_rescaler():
    global T_WIDTH
    while True:
        if os.get_terminal_size().columns is not T_WIDTH:
            T_WIDTH = os.get_terminal_size().columns
            print_interface()



def data_receive(s, host_port):
    while s.connect_ex(host_port) != 9:
        data = s.recv(4096)
        decoded_data = data.decode("utf-8")
        
        if not data:
            break
        
        print(decoded_data)
        msg = Message(**json.loads(decoded_data))

        if msg.message_type == UNKNOWN:
            cprint("Data is unknown", ERR)
            time.sleep(0.1)
            try:
                s.getsockname()
            except OSError:
                break
            cprint(decoded_data[:len(decoded_data)-1], SER)
            break
        elif msg.message_type == SEND_OK:
            # print("Data is send ok")
            cprint(data, SER)
            break
        elif msg.message_type == "DELIVERY":
            cprint("Data is delivered", SER)
            
            print(msg.content)
            cprint("\n", INP)
        else:
            cprint(f"Online: {msg.content}", SER)


def messenger_function():
    global SIGNUP, LOGIN
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    cprint(f"Connecting to {HOST}:{PORT}...", INF)

    try: 
        s.connect((HOST, PORT))
    except ConnectionRefusedError:
        cprint(f"Connection to {HOST}:{PORT} failed. Server is most likely offline.", ERR)
        return
    
    cprint("Connected.", SUC)
    while True:
        login_type = cinput("Do you want to login or register? (l/r): ")
        if login_type == "l":
            LOGIN = True
            break
        elif login_type == "r":
            SIGNUP = True
            break
        else:
            cprint("Invalid input. Try again.", ERR)
            continue
    
    user = cinput("Enter your name: ")
    pwd = cinput("Enter your password: ", pwd=True)
    
    while SIGNUP:
        if pwd == "": pwd = cinput("Enter your password: ", pwd=True)
        pwd_check = cinput("Confirm your password: ", pwd=True)
        if pwd != pwd_check:
            cprint("Passwords do not match. Try again.", ERR)
            pwd = ""
            continue
        else: 
            break

    pwd = sha256(pwd.encode("utf-8")).hexdigest()

    # remember = cinput("Do you want to remember your login details? (y/n): ")
    
    
    u = User(user, pwd) 
    msg_type = "SIGNUP" if SIGNUP else "LOGIN"
    message2 = Message(u, msg_type)
    print(s)
    print(message2.to_json())

    
    msg = " "
    hello = "HELLO-FROM " + user + "\n"
    who = "WHO\n"

    enter = True

    string_bytes = message2.to_json().encode("utf-8")


    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(host_port)
        s.sendall(string_bytes)
        data = s.recv(4096)
        decoded_data = data.decode("utf-8")
        msg = Message(**json.loads(decoded_data))

        if msg.message_type == "HELLO":
            string_bytes = b''
            break

        else:
            print(msg)
            s.close()
            if msg.message_type == "BAD-RQST-BODY":
                user = input('Username is invalid, please enter another: ')
            else:
                user = input('Username is taken, please enter another: ')
            hello = "HELLO-FROM " + user + "\n"
            string_bytes = Message(User(user, pwd), msg_type)
    
    t = threading.Thread(target=data_receive, args=(s, host_port), daemon=True)
    t.start()
    msg = " "
    print_interface(clear=True)
    
    while msg != "!quit": 

        if not enter:
            msg = cinput("")

        enter = False

        if (msg == "!quit"):
            text_message = "SEND @ Bye! \n"
            string_bytes = text_message.encode("utf-8")
            s.sendall(string_bytes)
            time.sleep(0.1)
            s.close()
            break

        elif (msg == "!who"):
            string_bytes = who.encode("utf-8")

        elif (msg[0] == "@"):
            text_message = "SEND " + msg[1:] + " \n"
            string_bytes = text_message.encode("utf-8")         
            
        s.sendall(string_bytes)
        time.sleep(1/100)
       
    print(f"Cya later, {user}!")
    threading._shutdown()
    
    t.join()
    exit()

def main():
    print_interface()
    messenger_function()


if __name__ == "__main__":
    print(T_WIDTH)
    t_width = threading.Thread(target=dynamic_rescaler, daemon=True)
    t_width.start()
    main()