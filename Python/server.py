import socket
import threading
from EmojiSound import EmojiSound
import sys
import time
import math

# Setting the Server IP via argv. Default value: "127.0.0.1"
system_args = sys.argv[1:]
if len(system_args) == 0:
    SERVER = "127.0.0.1"
elif len(system_args) >= 1:
    SERVER = system_args[0]

'''the following Variables must have the same Value in the client and the server script'''
# information needed for the Socket Connection
HEADER = 64
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SET_NAME_MESSAGE = "!NAME"
INSTRUCTION_MESSAGE = "!INSTRUCTION"
FORCE_DISCONNECT_MESSAGE = "!FORCEDISCONNECT"
AZIMUTH_MESSAGE = "!AZIMUTH"
ELEVATION_MESSAGE = "!ELEVATION"



print('Server IP: ', SERVER)

EmSound = EmojiSound(SERVER)

'''
The EmojiServer class includes all methods used to handle incoming messages from multiple clients.
'''
class EmojiServer:
    def __init__(self):
        self.threads = []
        self.clients = []
        self.SHUTDOWN = False

        # creating the socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)


    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        username = ""
        identification = addr
        azimuth = 0
        elevation = 0

        connected = True
        while connected:
            if self.SHUTDOWN:
                break
            try:
                # receiving and decoding the messages
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print(f"[{identification}] {msg}")
                    conn.send('!Server received message\n'.encode(FORMAT))
                    # Checking for Control Messages which begin with a "!"
                    if msg[0] == "!":
                        # Client is disconnecting
                        if msg == DISCONNECT_MESSAGE:
                            connected = False
                            print(f"[USER DISCONNECTED] ({identification}) dissconnected. [ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
                        # set the azimuth value
                        elif AZIMUTH_MESSAGE in msg:
                            if msg[len(AZIMUTH_MESSAGE):].isnumeric():
                                azimuth = int(msg[len(AZIMUTH_MESSAGE):])
                                azimuth = (azimuth-50)/50*math.pi/2
                                print(azimuth)
                        # set the elevation value
                        elif ELEVATION_MESSAGE in msg:
                            if msg[len(ELEVATION_MESSAGE):].isnumeric():
                                elevation = int(msg[len(ELEVATION_MESSAGE):])
                                elevation = (elevation-50)/50*math.pi/2
                                print(elevation)
                        # set the Username
                        elif SET_NAME_MESSAGE in msg:
                            old_id = identification
                            username = msg[len(SET_NAME_MESSAGE):]
                            conn.send(("!Your name has been set to " + username).encode(FORMAT))
                            if username != "":
                                identification = username
                            else:
                                identification = addr
                            print(f"[Info] '{old_id}' changed their name to '{identification}'")
                        # -- currently unused
                        elif INSTRUCTION_MESSAGE in msg:
                            self.share_message(f"{INSTRUCTION_MESSAGE}{identification}: {msg[len(INSTRUCTION_MESSAGE):]}\n")
                    else:
                        # the message will be shared with all other clients
                        self.share_message(msg)
                        # the message, azimuth and elevation will be send to the SuperCollider Server
                        EmSound.send_osc_msg(msg, False, azimuth, elevation)

            except Exception as e:
                print(e)
                if identification != addr:
                    print(f"[ERROR] connection to {identification} ({addr}) broke up. [ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
                else:
                    print(f"[ERROR] connection to {addr} broke up. [ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
                connected = False

        # closing the connection
        conn.close()
        print(f"[INFO] connection to ({identification}) has been closed.")

        for c in self.clients:
            if (conn, addr) == c:
                self.clients.remove(c)
                print(f"[INFO] Client ({identification}) has removed from the list. {len(self.clients)} clients remaining")

    # As long as the server isn't shutting down it will listen for upcoming connections
    # new Connections will be handled in their own thread
    def start(self):
        try:
            self.server.listen()
            print(f"[LISTENING] Server is listening on {SERVER}")
            while True:
                if self.SHUTDOWN:
                    break
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

    # tries to close all connections and then shut the server down properly
    # after shutting the server down the used ports stays in use, so the server can't be restarted.
    # this function is a workaround to prevent this bug. (unfortunately it still doesn't always work)
    def end(self):
        self.SHUTDOWN = True
        try:
            # forces all clients to disconnect
            self.share_message(FORCE_DISCONNECT_MESSAGE)
            print("Sending FORCE DISCONNECT to all clients")
            time.sleep(1)
            print("joining all threads")
            for i, t in enumerate(self.threads):
                print(f"joining thread {i}")
                t.join(2)
                print(f"[WARNING] Thread {i} is still running" if t.is_alive() else f"Thread {i} is turned off")

            print("trying to close all connections")
            if len(self.clients) > 0:
                for c in self.clients:
                    print(f"trying to close connection to {c[1]}")
                    c[0].close()
            print("shutting the socket down, and closing it.")
            self.server.shutdown(socket.SHUT_RDWR)
            self.server.close()
        except Exception as e:
            print(e)
            print("[ERROR] Couldn't shut server down properly... ")
        finally:
            print("Program is finally going to exit(sys.exit())")
            sys.exit()

    # sends the message "msg" to all connected clients
    def share_message(self, msg):
        for conn, addr in self.clients:
            try:
                conn.send(msg.encode(FORMAT))
            except Exception as e:
                print(e)
                print(f"[ERROR] in share message. Couldn't share '{msg}' with {addr}")


if __name__ == "__main__":
    print("[STARTING] server is starting...")
    the_server = EmojiServer()
    the_server.start()
