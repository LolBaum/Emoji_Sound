import socket
import threading

#SERVER = '10.10.5.59'

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SET_NAME_MESSAGE = "!NAME"

print('Server IP: ', SERVER)



class EmojiServer:
    def __init__(self):
        self.threads = []
        self.clients = []

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)


    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            try:
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print(f"[{addr}] {msg}")
                    conn.send('!Server received message'.encode(FORMAT))
                    if msg[0] == "!":
                        if msg == DISCONNECT_MESSAGE:
                            connected = False
                            print(f"[USER DISCONNECTED] ({addr}) dissconnected. [ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
                        if msg == SET_NAME_MESSAGE:
                            pass
                    else:
                        pass
                        #EmSound.send_osc_msg(msg, False)

                    self.share_message(msg)
            except Exception as e:
                print(e)
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
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        except Exception as e:
            print(e)
            print("[ERROR] Server crashed...")
        self.server.close(self)
        self.server.shutdown(self)



    def share_message(self, msg):
        for conn, _ in self.clients:
            try:
                conn.send(msg.encode(FORMAT))
            except Exception as e:
                print(e)
                print("[ERROR] share message")

if __name__ == "__main__":
    print("[STARTING] server is starting...")
    the_server = EmojiServer()
    the_server.start()