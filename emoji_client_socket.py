import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGroupBox, QGridLayout, QLineEdit, QLabel
from PyQt5 import QtCore
import threading
import time

import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SET_NAME_MESSAGE = "!NAME"
INSTRUCTION_MESSAGE = "!INSTRUCTION"
#SERVER = "172.25.128.1"
#SERVER = "127.0.1.1"
#SERVER = "84.238.39.36"
SERVER = "10.10.5.59"
#SERVER = "79.244.144.34"
ADDR = (SERVER, PORT)

START = "start"
VERBUNDEN = "connected"
NICHT_VERBUNDEN = "not connected"
ZUSTAND = START

MAX_VERBINDUNGS_VERSUCHE = 3
VERBINDUNGS_VERSUCHE = 0

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.settimeout(3)

EMOJIS = ['😂', '❤', '♥', '😍', '😭', '😘', '😊', '👌', '💕', '👏', '😁', '☺', '♡', '👍', '😩', '🙏', '✌', '😏', '😉',
          '🙌', '🙈', '💪', '😄', '😒', '💃', '💖', '😃', '😔', '😱', '🎉', '😜', '☯', '🌸', '💜', '💙', '✨', '😳', '💗',
          '★', '█', '☀', '😡', '😎', '😢', '💋', '😋', '🙊', '😴', '🎶', '💞', '😌', '🔥', '💯', '🔫', '💛', '💁', '💚',
          '♫', '😞', '😆', '😝', '😪', '�', '😫', '😅', '👊', '💀', '😀', '😚', '😻', '©', '👀', '💘', '🐓', '☕', '👋',
          '✋', '🎊', '🍕', '❄', '😥', '😕', '💥', '💔', '😤', '😈', '►', '✈', '🔝', '😰', '👿', '☹', '🔋', '✂', '🚫',
          '📌', '😕', '😐', '🔧', '😒', '😿', '😩', '😦', '┻', '👮', '┳', '😾', '🍈', '🙍', '🍱', '😑', '😠']

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
        print(f"[STATE] {ZUSTAND}")



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'EmojiSound Client'
        self.username = ""
        self.left = 300
        self.top = 300
        self.width = 120
        self.height = 100
        self.emoji_panels = []
        self.emoji_buttons = []
        self.funcs = []
        self.messages = []
        self.messages_label = QLabel(self)
        self.messages_box = []
        self.textboxes = {"IP": 0,
                          "port": 0}
        self.zustandslabel = QLabel(self)
        self.instructionlabel = QLabel(self)
        self.instructions = []
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

        windowLayout.addWidget(self.instructionlabel, 3, 1)
        self.instructionlabel.setAlignment(QtCore.Qt.AlignLeft)
        self.instructionlabel.setStyleSheet("border : 1px solid lightgray;")
        self.instructionlabel.setMinimumWidth(150)
        #self.instructionlabel.setMaximumSize(200,1000)
        self.instructionlabel.setWordWrap(True)



        clear_instruction_button = QPushButton("Clear Instructions", self)
        windowLayout.addWidget(clear_instruction_button, 2, 1)
        clear_instruction_button.clicked.connect(self.clear_instructions)


        windowLayout.addWidget(self.messages_box, 2, 0)

        windowLayout.setColumnStretch(0, 0)
        windowLayout.setColumnStretch(1, 2)



        for i in range(len(self.emoji_panels)):
            windowLayout.addWidget(self.emoji_panels[i],3,i)
        self.setLayout(windowLayout)

        self.show()


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

        button_size_textbox_x = QLineEdit(self)
        button_size_textbox_x.setText(str(40))  # Global
        func_layout.addWidget(button_size_textbox_x, row_button+2, 0)
        self.textboxes["button_size_x"] = button_size_textbox_x

        button_size_textbox_y = QLineEdit(self)
        button_size_textbox_y.setText(str(40))  # Global
        func_layout.addWidget(button_size_textbox_y, row_button + 2, 1)
        self.textboxes["button_size_y"] = button_size_textbox_y

        button_size_button = QPushButton("Set Button Size", self)
        func_layout.addWidget(button_size_button, row_button+2, 2)
        button_size_button.clicked.connect(self.set_global_button_size)

        set_name_textbox = QLineEdit(self)
        set_name_textbox.setText(str(self.username))  # Global
        func_layout.addWidget(set_name_textbox, row_button + 3, 1)
        self.textboxes["set_name"] = set_name_textbox

        set_name_button = QPushButton("Set Name", self)
        func_layout.addWidget(set_name_button, row_button + 3, 2)
        set_name_button.clicked.connect(self.set_username)

        #func_layout.addWidget(self.messages_label, row_label+2, 3)

        horizontalGroupBox.setLayout(func_layout)

        self.funcs = horizontalGroupBox

    def get_addr(self):
        IP = self.textboxes["IP"].text()
        port = int(self.textboxes["port"].text())
        return (IP, port)

    def set_username(self):
        self.username = self.textboxes["set_name"].text()
        print(f"[INFO] Setting your Username to {self.username}")
        send(SET_NAME_MESSAGE + self.username)


    def clear_instructions(self):
        self.instructions = []
        self.instructionlabel.setText("")

    def set_global_button_size(self):
        try:
            x = int(self.textboxes["button_size_x"].text())
            y = int(self.textboxes["button_size_y"].text())
            print(f"[INFO] resizing Buttons to ({x}, {y})")
            for b in self.emoji_buttons:
                b.set_size(x,y)
        except Exception as e:
            print(e)
            print("[ERROR] in set_global_button_size()")


    def button_connect(self):
        addr = self.get_addr()
        self.connect(addr)

    def msgs_to_string(self):
        string = ""
        for m in self.messages:
            string += m
        return string

    def update_msgs(self):
        if len(self.messages) > 27:
            self.messages.pop(0)
        self.messages_label.setText(self.msgs_to_string())

    def make_msg_box(self):
        horizontalGroupBox = QGroupBox("Messages")
        msg_layout = QGridLayout()

        self.messages_label.setText("no messages yet")
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
            self.emoji_buttons.append(button)
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
            self.emoji_buttons.append(button)
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
                try:
                    #print(f"[Info] client started listening for answers from the server")
                    msg = CLIENT.recv(2048).decode(FORMAT)
                    if len(msg) > 0:
                        if msg[0] != "!":
                            self.messages.append(msg)
                            self.update_msgs()
                        else:
                            if INSTRUCTION_MESSAGE in msg:
                                new_instruction = msg[len(INSTRUCTION_MESSAGE):]
                                self.instructions.append(new_instruction)
                                print("instructions: ", self.instructions)
                                self.instructionlabel.setText(self.instructions_as_text())
                                print(self.instructionlabel.text())

                        print(msg)
                        time.sleep(0.1)
                except Exception as e:
                    print(e)
                    print("[ERROR] in client_receive()")

    def instructions_as_text(self):
        text = ""
        for i in self.instructions:
            text += i
            text += "\n"
        return text





    def connect(self, addr):  # Einfache Verbindung zu nur einem Server
        global ADDR
        global CLIENT
        global ZUSTAND
        print(f"Connecting to {addr}.")

        print(f"[STATE] {ZUSTAND}")


        if ZUSTAND == START:
            try:
                CLIENT.connect(addr)
                ZUSTAND = VERBUNDEN
            except Exception as error:
                print(f"Connection ERROR in state {ZUSTAND}")
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
                CLIENT.settimeout(None)
            except Exception as error:
                print(f"Connection ERROR in state {ZUSTAND}")
                print(error)
                ZUSTAND = NICHT_VERBUNDEN

        if ZUSTAND == NICHT_VERBUNDEN:
            try:
                CLIENT.close()
                CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as error:
                print(f"Connection ERROR in state {ZUSTAND}")  # Debug
                print("Connection couldn't be closed")
            try:
                CLIENT.connect(addr)
                if self.username != "":
                    self.set_username()
                ZUSTAND = VERBUNDEN
            except Exception as error:
                print(f"Connection ERROR in state {ZUSTAND}")  # Debug
                print(error)
                ZUSTAND = NICHT_VERBUNDEN


        print(f"[STATE] {ZUSTAND}")

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

    def set_size(self, x, y):
        self.setMaximumWidth(x)
        self.setMaximumHeight(y)




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
