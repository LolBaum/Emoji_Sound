import socket
import threading
from EmojiSound import EmojiSound
import sys



HEADER = 64
PORT = 5050

system_args = sys.argv[1:]
if len(system_args) == 0:
    SERVER = "127.0.0.1"
elif len(system_args) >= 1:
    SERVER = system_args[0]
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SET_NAME_MESSAGE = "!NAME"
INSTRUCTION_MESSAGE = "!INSTRUCTION"
FORCE_DISCONNECT_MESSAGE = "!FORCEDISCONNECT"

print('Server IP: ', SERVER)


EmSound = EmojiSound(SERVER)


class EmojiServer:
    def __init__(self):
        self.threads = []
        self.clients = []

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)


    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        username = ""
        identification = addr

        connected = True
        while connected:
            try:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print(f"[{identification}] {msg}")
                    conn.send('!Server received message'.encode(FORMAT))
                    if msg[0] == "!":
                        if msg == DISCONNECT_MESSAGE:
                            connected = False
                            print(f"[USER DISCONNECTED] ({identification}) dissconnected. [ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
                        if SET_NAME_MESSAGE in msg:
                            old_id = identification
                            username = msg[len(SET_NAME_MESSAGE):]
                            conn.send(("!Your name has been set to " + username).encode(FORMAT))
                            if username != "":
                                identification = username
                            else:
                                identification = addr
                            print(f"[Info] '{old_id}' changed their name to '{identification}'")
                        if INSTRUCTION_MESSAGE in msg:
                            self.share_message(f"{INSTRUCTION_MESSAGE}{identification}: {msg[len(INSTRUCTION_MESSAGE):]}\n")
                    else:
                        self.share_message(msg)
                        EmSound.send_osc_msg(msg, False)

                    #self.share_message(msg)
            except Exception as e:
                print(e)
                if identification != addr:
                    print(f"[ERROR] connection to {identification} ({addr}) broke up. [ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
                else:
                    print(f"[ERROR] connection to {addr} broke up. [ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
                connected = False

        for c in self.clients:
            if (conn, addr) == c:
                self.clients.remove(c)

        conn.close()



    def start(self):
        try:
            self.server.listen()
            print(f"[LISTENING] Server is listening on {SERVER}")
            while True:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                self.threads.append(thread)
                self.clients.append((conn, addr))
                thread.deamon = True
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        except Exception as e:
            print(e)
            print("[ERROR] Server crashed...")
        finally:
            print("Server is shutting down")
            self.end()

    def end(self):
        try:
            if len(self.clients) > 0:
                for c in self.clients:
                    c[0].close()
            self.server.shutdown(socket.SHUT_RDWR)
            self.server.close()
        except Exception as e:
            print(e)
            print("[ERROR] Couldn't shut server down properly... ")
        finally:
            sys.exit()



    def share_message(self, msg):
        for conn, _ in self.clients:
            try:
                conn.send(msg.encode(FORMAT))
            except Exception as e:
                print(e)
                print("[ERROR] in share message")

if __name__ == "__main__":
    print("[STARTING] server is starting...")
    the_server = EmojiServer()
    the_server.start()
