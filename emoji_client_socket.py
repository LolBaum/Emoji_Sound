import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QLineEdit, QLabel
from PyQt5 import QtCore
import threading
import time


import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SET_NAME_MESSAGE = "!NAME"
#SERVER = "172.25.128.1"
#SERVER = "127.0.1.1"
SERVER = "84.238.39.36"
ADDR = (SERVER, PORT)

START = "start"
VERBUNDEN = "verbunden"
NICHT_VERBUNDEN = "nicht verbunden"
ZUSTAND = START

MAX_VERBINDUNGS_VERSUCHE = 3
VERBINDUNGS_VERSUCHE = 0

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





EMOJIS = ['😂', '❤', '♥', '😍', '😭', '😘', '😊', '👌', '💕', '👏', '😁', '☺', '♡', '👍', '😩', '🙏', '✌', '😏', '😉', '🙌', '🙈', '💪', '😄', '😒', '💃', '💖', '😃', '😔', '😱', '🎉', '😜', '☯', '🌸', '💜', '💙', '✨', '😳', '💗', '★', '█', '☀', '😡', '😎', '😢', '💋', '😋', '🙊', '😴', '🎶', '💞', '😌', '🔥', '💯', '🔫', '💛', '💁', '💚', '♫', '😞', '😆', '😝', '😪', '�', '😫', '😅', '👊', '💀', '😀', '😚', '😻', '©', '👀', '💘', '🐓', '☕', '👋', '✋', '🎊', '🍕', '❄', '😥', '😕', '💥', '💔', '😤', '😈', '►', '✈', '🔝', '😰', '👿', '☹', '🔋', '✂', '🚫', '📌', '😕', '😐', '🔧', '😒', '😿', '😩', '😦', '┻', '👮', '┳', '😾', '🍈', '🙍', '🍱', '😑', '😠']

# def connect(addr):  # Einfache Verbindung zu nur einem Server
#     global ADDR
#     global CONNECTED
#     print("pre check: ", CONNECTED)
#     check_connection()
#     print("after check: ", CONNECTED)
#
#     print(f"Connecting to {addr}.")
#
#     try:
#         if CONNECTED:
#             if ADDR == addr:
#                 print(f"Already connected to THIS IP.")
#                 send("testing connection")
#             else:
#                 print(f"You were connected to {addr}.")
#                 send(DISCONNECT_MESSAGE)
#                 CLIENT.close()
#                 print(f"Connection to {addr} has been closed for new connection.")
#                 CLIENT.connect(addr)
#         else:
#             CLIENT.connect(addr)
#     except Exception as error:
#         print(f"[ERROR] trying to connect to {addr}")
#         print(error)
#
#     ADDR = addr






def send(msg):
    global CLIENT
    global ZUSTAND
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        CLIENT.send(send_length)
        CLIENT.send(message)
        #print(CLIENT.recv(2048).decode(FORMAT))
    except:
        print(f"[ERROR] while sending to {ADDR}")
        ZUSTAND = NICHT_VERBUNDEN
        print(f"[ZUSTAND] {ZUSTAND}")



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'PyQt5 layout - pythonspot.com'
        self.left = 300
        self.top = 300
        self.width = 120
        self.height = 100
        self.emoji_panels = []
        self.funcs = []
        self.messages = []
        self.messages_label = QLabel(self)
        self.messages_box = []
        self.textboxes = {"IP": 0,
                          "port": 0}
        self.zustandslabel = QLabel(self)
        self.initUI()

        self.setWindowTitle("Emoji Client")

        self.connect(ADDR)
        self.is_running = True

        self.thread = threading.Thread(target=self.client_receive)
        self.thread.start()


        timerTime = QtCore.QTimer(self)
        timerTime.timeout.connect(self.update_status)
        timerTime.start(1000)
        #self.make_emoji_Grid(10,5)


        #self.make_emoji_Button('\U0001F607', 20)

        # button = QPushButton('Click me \U0001F602', self)
        # button2 = QPushButton('\U0001F607', self)  # Todo: Knopf bewegen
        # a=25
        # button2.setStyleSheet("font-size:"+str(a)+"px");
        # button2.resize(a+15, a+15)
        # button.resize(150, 50)
        #button.clicked.connect(self.on_click)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #self.make_emoji_Grid(78, 10)
        #self.make_emoji_Grid(78, 10, 127744)
        #self.make_emoji_Grid(78, 10, 128000)
        self.make_selected_emoji_Grid(10, EMOJIS)
        self.make_func_Grid()
        self.make_msg_box()
        windowLayout = QGridLayout()

        windowLayout.addWidget(self.funcs, 0,0)

        windowLayout.addWidget(self.zustandslabel, 0, 1)
        windowLayout.addWidget(self.messages_box, 2, 0)



        for i in range(len(self.emoji_panels)):
            windowLayout.addWidget(self.emoji_panels[i],3,i)
        self.setLayout(windowLayout)

        self.show()


    def make_Grid(self):
        self.a = QGroupBox("test")
        test_layout = QGridLayout()
        self.a.setLayout(test_layout)

    def make_func_Grid(self):
        row_button = 1
        row_label = 0
        horizontalGroupBox = QGroupBox("Functions")
        func_layout = QGridLayout()

        disconnect_button = QPushButton("disconnect", self)
        func_layout.addWidget(disconnect_button, row_button, 0)
        disconnect_button.clicked.connect(disconnect)

        connect_button = QPushButton("connect", self)
        func_layout.addWidget(connect_button, row_button,1)
        connect_button.clicked.connect(self.button_connect)

        server_IP_textbox = QLineEdit(self)
        server_IP_textbox.setText(SERVER)  # Global
        func_layout.addWidget(server_IP_textbox, row_button, 2)
        self.textboxes["IP"] = server_IP_textbox
        server_IP_label = QLabel(self)
        server_IP_label.setText("Server IP")
        func_layout.addWidget(server_IP_label, row_label, 2)


        server_port_textbox = QLineEdit(self)
        server_port_textbox.setText(str(PORT))  # Global
        func_layout.addWidget(server_port_textbox, row_button, 3)
        self.textboxes["port"] = server_port_textbox
        server_port_label = QLabel(self)
        server_port_label.setText("Server port")
        func_layout.addWidget(server_port_label, row_label, 3)

        func_layout.addWidget(self.messages_label, row_label+2, 3)

        horizontalGroupBox.setLayout(func_layout)

        self.funcs = horizontalGroupBox

    def get_addr(self):
        IP = self.textboxes["IP"].text()
        port = int(self.textboxes["port"].text())
        return (IP, port)

    def button_connect(self):
        addr = self.get_addr()
        self.connect(addr)

    def msgs_to_string(self):
        string = ""
        for m in self.messages:
            string += m
        return string

    def update_msgs(self):
        if len(self.messages) > 20:
            self.messages.pop(0)
        self.messages_label.setText(self.msgs_to_string())

    def make_msg_box(self):
        horizontalGroupBox = QGroupBox("Messages")
        msg_layout = QGridLayout()

        self.messages_label.setText("noch keine Nachrichten")
        msg_layout.addWidget(self.messages_label, 0,0)

        horizontalGroupBox.setLayout(msg_layout)

        self.messages_box = horizontalGroupBox



    def make_emoji_Grid(self, n, x, start_code = 128514):
        horizontalGroupBox = QGroupBox("Emojis")
        emoji_layout = QGridLayout()
        #layout.setColumnStretch(1, 4)
        #layout.setColumnStretch(2, 4)



        for i in range(n):
            button = MyEmojiButton(self, 20, chr(start_code + i))
            #print(button.text())
            emoji_layout.addWidget(button, i//x, i%x) #chr(128514)
            button.clicked.connect(button.myprint)

        horizontalGroupBox.setLayout(emoji_layout)

        self.emoji_panels.append(horizontalGroupBox)

    def make_selected_emoji_Grid_from_int(self, x, emojilist):
        horizontalGroupBox = QGroupBox("selected Emojis")
        emoji_layout = QGridLayout()

        for i in range(len(emojilist)):
            button = MyEmojiButton(self, 20, chr(emojilist[i]))
            #print(button.text())
            emoji_layout.addWidget(button, i//x, i%x) #chr(128514)
            button.clicked.connect(button.myprint)

        horizontalGroupBox.setLayout(emoji_layout)

        self.emoji_panels.append(horizontalGroupBox)

    def make_selected_emoji_Grid(self, x, emojilist):
        horizontalGroupBox = QGroupBox("selected Emojis")
        emoji_layout = QGridLayout()

        for i in range(len(emojilist)):
            button = MyEmojiButton(self, 20, emojilist[i])
            #print(button.text())
            emoji_layout.addWidget(button, i//x, i%x) #chr(128514)
            button.clicked.connect(button.myprint)

        horizontalGroupBox.setLayout(emoji_layout)

        self.emoji_panels.append(horizontalGroupBox)

    def update_status(self):
        if ZUSTAND == START:
            self.zustandslabel.setText(f"<font color=black>{ZUSTAND}</font>")
        elif ZUSTAND == VERBUNDEN:
            self.zustandslabel.setText(f"<font color=green>{ZUSTAND}</font>")
        elif ZUSTAND == NICHT_VERBUNDEN:
            self.zustandslabel.setText(f"<font color=red>{ZUSTAND}</font>")


    def client_receive(self):
        while self.is_running:
            if ZUSTAND == VERBUNDEN:
                #print(f"[Info] client started listening for answers from the server")
                msg = CLIENT.recv(2048).decode(FORMAT)
                if len(msg) > 0:
                    if msg[0] != "!":
                        self.messages.append(msg)
                        self.update_msgs()
                    print(msg)
                    time.sleep(0.1)





    def connect(self, addr):  # Einfache Verbindung zu nur einem Server
        global ADDR
        global CLIENT
        global ZUSTAND
        print(f"Connecting to {addr}.")

        print(f"[ZUSTAND] {ZUSTAND}")


        if ZUSTAND == START:
            try:
                CLIENT.connect(addr)
                ZUSTAND = VERBUNDEN
            except Exception as error:
                print(f"Verbindungsfehler im Zustand {ZUSTAND}")
                print(error)
                ZUSTAND = START

        if ZUSTAND == VERBUNDEN:
            try:
                if ADDR == addr:
                    send("!testing connection")
                else:
                    print(f"You were connected to {addr}.")
                    send(DISCONNECT_MESSAGE)
                    CLIENT.close()
                    print(f"Connection to {addr} has been closed for new connection.")
                    CLIENT.connect(addr)
            except Exception as error:
                print(f"Verbindungsfehler im Zustand {ZUSTAND}")
                print(error)
                ZUSTAND = NICHT_VERBUNDEN

        if ZUSTAND == NICHT_VERBUNDEN:
            try:
                CLIENT.close()
                CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as error:
                print(f"Verbindungsfehler im Zustand {ZUSTAND}")  # Debug
                print("Konnte Verbindung nicht schlißen")
            try:
                CLIENT.connect(addr)
                ZUSTAND = VERBUNDEN
            except Exception as error:
                print(f"Verbindungsfehler im Zustand {ZUSTAND}")  # Debug
                print(error)
                ZUSTAND = NICHT_VERBUNDEN


        print(f"[ZUSTAND] {ZUSTAND}")

        ADDR = addr
        self.update_status()


class MyEmojiButton(QPushButton):
    def __init__(self, window, size, text="button"):
        super().__init__(text,window)
        self.setStyleSheet("font-size:" + str(size) + "px");
        self.setMaximumWidth(size + 15)
        self.setMaximumHeight(size + 15)
        self.mytext = text
        #self.setToolTip(emoji.demojize(text))
        self.setToolTip("")

    def myprint(self):
        #print(emoji.demojize(self.mytext))
        print(self.mytext)
        send(self.mytext)



def disconnect():
    global ZUSTAND
    print(DISCONNECT_MESSAGE)
    send(DISCONNECT_MESSAGE)
    ZUSTAND = NICHT_VERBUNDEN



if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    status = app.exec_()
    w.is_running = False
    send(DISCONNECT_MESSAGE)
    sys.exit(status)


    #my_label = Label(root, text='41' + u'\u00A2').pack()
