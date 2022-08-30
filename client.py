from code import interact
import socket
import threading
import time

from psutil import boot_time

interface = """\033c
-------------------------------------------------
| Welcome to the chatroom!                      |
|                                               |
| Type !quit to exit.                           |
| Type !who to see who is in the chatroom.      |
| Type @username to send a message to username. |
|                                               |"""

bottom_line = "-------------------------------------------------"

UNKNOWN = "UNKNOWN\n".encode("utf-8")
SEND_OK = "SEND-OK\n".encode("utf-8")
DELIVERY = "DELIVERY".encode("utf-8")

def print_interface():
    print(interface, bottom_line, sep="\n")


def data_receive(s, host_port):
    while s.connect_ex(host_port) != 9:
        data = b''
        while b'\n' not in data:
            data += s.recv(2)
        decoded_data = data.decode("utf-8")
        if not data:
            break
        elif data == UNKNOWN:
            print("Data is unknown")
            time.sleep(0.1)
            try:
                s.getsockname()
            except OSError:
                break
            print('Server:', decoded_data[:len(decoded_data)-1])
            break
        elif data == SEND_OK:
            # print("Data is send ok")
            print(data)
            break
        elif DELIVERY in data:
            print("Data is delivered")
            decoded_data = decoded_data.split(" ")
            
            print(decoded_data[1], end=": ")
            for word in decoded_data[2:-1]:
                print(word, end=" ")
            print("\n| > ", end=" ")
        else:
            print('| Server:', decoded_data[:len(decoded_data)-1])

def messenger_function():
    HOST = '127.0.0.1'      # The server's hostname or IP address
    PORT = 5378             # The port used by the server
    host_port = (HOST, PORT)

    user = input('What\'s your username? ')
    msg = " "
    hello = "HELLO-FROM " + user + "\n"
    who = "WHO\n"

    enter = True
    name = False

    string_bytes = hello.encode("utf-8")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while not name:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(host_port)
        s.sendall(string_bytes)
        data = s.recv(4096)
        decoded_data = data.decode("utf-8")
        print('Server:', decoded_data[:len(decoded_data)-1])

        if data == ("HELLO " + user + "\n").encode("utf-8"):
            string_bytes = b''
            name = True
            break 

        else:
            print(data)
            s.close()
            if data == ("BAD-RQST-BODY\n").encode("utf-8"):
                user = input('Username is invalid, please enter another: ')
            else:
                user = input('Username is taken, please enter another: ')
            hello = "HELLO-FROM " + user + "\n"
            string_bytes = hello.encode("utf-8")
    
    t = threading.Thread(target=data_receive, args=(s, host_port), daemon=True)
    t.start()
    msg = " "
    print_interface()
    
    while msg != "!quit": 

        if not enter:
            print("|", end=" ")
            msg = input('> ').strip()

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
    messenger_function()


if __name__ == "__main__":
    main()