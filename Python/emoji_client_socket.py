# Luzie Ahrens and Laurin Dahm
# 22.09.2021

# Interface for sending Emoji-Messages to the Python-Server

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGroupBox, QGridLayout, QLineEdit, QLabel, QSlider
from PyQt5 import QtCore
import threading
import time
import socket

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
FORMAT = 'utf-8'
# Messages beginning with a "!" are used to call particular functions on the server
DISCONNECT_MESSAGE = "!DISCONNECT"
SET_NAME_MESSAGE = "!NAME"
INSTRUCTION_MESSAGE = "!INSTRUCTION"
FORCE_DISCONNECT_MESSAGE = "!FORCEDISCONNECT"
AZIMUTH_MESSAGE = "!AZIMUTH"
ELEVATION_MESSAGE = "!ELEVATION"

# State variables to store and display the state of the connection
START = "start"
CONNECTED = "connected"
NOT_CONNECTED = "not connected"
STATE = START

MAX_CONNECTION_ATTEMPTS = 3
CONNECTION_ATTEMPTS = 0

# creating the Socket
ADDR = (SERVER, PORT)
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.settimeout(3)

# List of all Emojis that will be shown in the interface.
EMOJIS = ["🙏", "🤘", "😏", "😉", "🙌", "🙈", "💪", "😄", "😒", "💃", "💖", "😃", "😔", "😱", "🎉", "😜", "☯️", "🌸", "💜",
          "💙", "✨", "😳", "💗", "⭐️", "❄️", "😡", "😎", "😢", "💋", "😋", "🙊", "😴", "🎶", "💞", "😌", "🔥", "💯", "🔫",
          "💛", "💁", "💚", "🎵", "😞", "😆", "😝", "😪", "😫", "😅", "👊", "💀", "😀", "😚", "😻", "©️", "👀", "💘", "🐓",
          "👋", "✋", "🎊", "🍕", "😥", "😕", "💥", "💔", "😤", "😈", "▶️", "✈️", "🔝", "😰", "👿", "☹️", "🔋", "✂️", "🚫",
          "📌", "😕", "😐", "🔧", "😒", "😿", "😩", "😦", "👮", "😾", "🍈", "🙍", "🍱", "😑", "😠"]

# Sending a Message through the Socket connection to server. An exception will set the state to NOT_CONNECTED
def send(msg):
    global CLIENT
    global STATE
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        CLIENT.send(send_length)
        CLIENT.send(message)
    except Exception as e:
        print(f"[ERROR] while sending to {ADDR}")
        print(f"[ERROR]: {e}")
        STATE = NOT_CONNECTED
        print(f"[STATE] {STATE}")

# sends the disconnect message to close the socket connection
def disconnect():
    global STATE
    print(DISCONNECT_MESSAGE)
    send(DISCONNECT_MESSAGE)
    STATE = NOT_CONNECTED


'''
The MainWindow class includes the most elements of the application and creates the GUI on initialization.
It inherits form a QWidget.
'''
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'EmojiSound Client'
        self.username = ""
        self.left = 300
        self.top = 300
        self.width = 120
        self.height = 100

        # All UI-elements are "declared"
        self.emoji_panels = []
        self.emoji_buttons = []
        self.funcs = []
        self.messages = []
        self.messages_label = QLabel(self)
        self.messages_box = []
        self.textboxes = {"IP": 0,
                          "port": 0}
        self.zustandslabel = QLabel(self)
        self.azimuthSlider = QSlider(QtCore.Qt.Horizontal)
        self.elevationSlider = QSlider(QtCore.Qt.Horizontal)

        # initializing the UI
        self.initUI()

        self.is_running = True

        # Another thread is started to receive messages while the application is running
        self.thread = threading.Thread(target=self.client_receive)
        self.thread.start()

        # creating a timer for the staus update
        timerTime = QtCore.QTimer(self)
        timerTime.timeout.connect(self.update_status)
        timerTime.start(1000)


    def initUI(self):
        # setting up the Window
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # initializing the Emoji Buttons, as well as several controls for the application
        self.make_selected_emoji_Grid(10, EMOJIS)
        self.make_func_Grid()
        self.make_msg_box()

        # the UI-elements are added to the window layout
        windowLayout = QGridLayout()
        windowLayout.addWidget(self.funcs, 0,0)
        windowLayout.addWidget(self.zustandslabel, 0, 1)
        windowLayout.addWidget(self.messages_box, 2, 0)
        windowLayout.setColumnStretch(0, 0)
        windowLayout.setColumnStretch(1, 2)

        # the emoji panels (currently just one) added to the layout
        for i in range(len(self.emoji_panels)):
            windowLayout.addWidget(self.emoji_panels[i],3,i)

        # the layout will be applied and displayed afterwards
        self.setLayout(windowLayout)
        self.show()


    def make_func_Grid(self):
        # Creation a Grid for the control functions
        row_button = 1
        row_label = 0
        horizontalGroupBox = QGroupBox("Functions")
        func_layout = QGridLayout()

        # In the following several Buttons will be created an connected with their corresponding functions
        # Button to disconnect
        disconnect_button = QPushButton("disconnect", self)
        func_layout.addWidget(disconnect_button, row_button, 0)
        disconnect_button.clicked.connect(disconnect)

        # Button to connect
        connect_button = QPushButton("connect", self)
        func_layout.addWidget(connect_button, row_button,1)
        connect_button.clicked.connect(self.button_connect)

        # Textbox for the Server IP
        server_IP_textbox = QLineEdit(self)
        server_IP_textbox.setText(SERVER)  # Global
        func_layout.addWidget(server_IP_textbox, row_button, 2)
        self.textboxes["IP"] = server_IP_textbox
        # Label for the Server IP
        server_IP_label = QLabel(self)
        server_IP_label.setText("Server IP")
        func_layout.addWidget(server_IP_label, row_label, 2)

        # Textbox for the Port
        server_port_textbox = QLineEdit(self)
        server_port_textbox.setText(str(PORT))  # Global
        func_layout.addWidget(server_port_textbox, row_button, 3)
        self.textboxes["port"] = server_port_textbox
        # Label for the Port
        server_port_label = QLabel(self)
        server_port_label.setText("Server port")
        func_layout.addWidget(server_port_label, row_label, 3)

        # Textbox for the username
        set_name_textbox = QLineEdit(self)
        set_name_textbox.setText(str(self.username))  # Global
        func_layout.addWidget(set_name_textbox, row_button + 3, 1)
        self.textboxes["set_name"] = set_name_textbox
        # Button to set the username
        set_name_button = QPushButton("Set Name", self)
        func_layout.addWidget(set_name_button, row_button + 3, 2)
        set_name_button.clicked.connect(self.set_username)

        # Slider to control the Azimuth
        azimuthLabel = QLabel(self)
        azimuthLabel.setText("Azimuth")
        func_layout.addWidget(azimuthLabel, row_button+4, 0)
        func_layout.addWidget(self.azimuthSlider, row_button+4, 1)
        self.azimuthSlider.setRange(0, 99)
        self.azimuthSlider.setValue(49)
        self.azimuthSlider.valueChanged.connect(self.changeValue_azimuth)

        # Slider to control the Elevation
        elevationLabel = QLabel(self)
        elevationLabel.setText("Elevation")
        func_layout.addWidget(elevationLabel, row_button+5, 0)
        func_layout.addWidget(self.elevationSlider, row_button+5, 1)
        self.elevationSlider.setRange(0, 99)
        self.elevationSlider.setValue(49)
        self.elevationSlider.valueChanged.connect(self.changeValue_elevation)

        # the Layout is being applied
        horizontalGroupBox.setLayout(func_layout)
        self.funcs = horizontalGroupBox

    # returns IP and Port from the textboxes as Tuple
    def get_addr(self):
        IP = self.textboxes["IP"].text()
        port = int(self.textboxes["port"].text())
        return (IP, port)

    # sets the username to the content aof the set_name textbox
    # Sends the name change to the server
    def set_username(self):
        self.username = self.textboxes["set_name"].text()
        print(f"[INFO] Setting your Username to {self.username}")
        send(SET_NAME_MESSAGE + self.username)

    # -- currently unused
    def clear_instructions(self):
        self.instructions = []
        self.instructionlabel.setText("")

    # -- currently unused
    # Sets the size of the Emoji Buttons
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

    # called by "connect"-Button
    # calls the connect method
    def button_connect(self):
        addr = self.get_addr()
        self.connect(addr)

    # returns a string from all received messages
    def msgs_to_string(self):
        string = ""
        for m in self.messages:
            string += m
        return string

    # updates the message list. Removes the last element if the list gets to long
    def update_msgs(self):
        if len(self.messages) > 27:
            self.messages.pop(0)
        self.messages_label.setText(self.msgs_to_string())

    # sends the server the azimuth Value (args: value)
    def changeValue_azimuth(self, value):
        send(AZIMUTH_MESSAGE + str(value))

    # sends the server the azimuth elevation (args: value)
    def changeValue_elevation(self, value):
        send(ELEVATION_MESSAGE + str(value))

    # creates a message box to display the sent emojis
    def make_msg_box(self):
        horizontalGroupBox = QGroupBox("Messages")
        msg_layout = QGridLayout()

        self.messages_label.setText("no messages yet")
        msg_layout.addWidget(self.messages_label, 0,0)

        horizontalGroupBox.setLayout(msg_layout)

        self.messages_box = horizontalGroupBox

    # --unused
    # --outdated
    # used to create a grid of Emoji Buttons
    def make_emoji_Grid(self, n, x, start_code = 128514):
        horizontalGroupBox = QGroupBox("Emojis")
        emoji_layout = QGridLayout()

        for i in range(n):
            button = EmojiButton(self, 20, chr(start_code + i))
            emoji_layout.addWidget(button, i//x, i%x) #chr(128514)
            button.clicked.connect(button.myprint)

        horizontalGroupBox.setLayout(emoji_layout)
        self.emoji_panels.append(horizontalGroupBox)

    # -- currently unused
    # creates a grid of Emoji Buttons from their unicode integer values
    # args: number of columns (int), list of emojis
    def make_selected_emoji_Grid_from_int(self, x, emojilist):
        horizontalGroupBox = QGroupBox("selected Emojis")
        emoji_layout = QGridLayout()

        for i in range(len(emojilist)):
            button = EmojiButton(self, 20, chr(emojilist[i]))
            self.emoji_buttons.append(button)
            emoji_layout.addWidget(button, i//x, i%x) #chr(128514)
            button.clicked.connect(button.myprint)

        horizontalGroupBox.setLayout(emoji_layout)
        self.emoji_panels.append(horizontalGroupBox)

    # creates a grid of Emoji Buttons from a list of strings
    # args: number of columns (int), list of emojis as strings/characters
    def make_selected_emoji_Grid(self, x, emojilist):
        horizontalGroupBox = QGroupBox("selected Emojis")
        emoji_layout = QGridLayout()

        for i in range(len(emojilist)):
            button = EmojiButton(self, 20, emojilist[i])
            self.emoji_buttons.append(button)
            emoji_layout.addWidget(button, i//x, i%x) #chr(128514)
            button.clicked.connect(button.myprint)

        horizontalGroupBox.setLayout(emoji_layout)
        self.emoji_panels.append(horizontalGroupBox)

    # updates the connection state
    def update_status(self):
        if STATE == START:
            self.zustandslabel.setText(f"<font color=black>{STATE}</font>")
        elif STATE == CONNECTED:
            self.zustandslabel.setText(f"<font color=green>{STATE}</font>")
        elif STATE == NOT_CONNECTED:
            self.zustandslabel.setText(f"<font color=red>{STATE}</font>")

    # function is called by the receive thread
    # receives and handels messages from the sever, as long as the application is running
    def client_receive(self):
        while self.is_running:
            if STATE == CONNECTED:
                try:
                    # decoding the message
                    msg = CLIENT.recv(2048).decode(FORMAT)
                    if len(msg) > 0:
                        # if the message doesn't begin with a "!" it will be displayed
                        if msg[0] != "!":
                            self.messages.append(msg[:1])
                            self.update_msgs()
                        # Checking for functional messages (currently just Forced disconnect)
                        else:
                            if FORCE_DISCONNECT_MESSAGE in msg:
                                print("[WARNING] Server Forced client to disconnect")
                                disconnect()
                        if "!Server received message" in msg:
                            pass
                        else:
                            print(msg+"\n")
                        time.sleep(0.1)
                except Exception as e:
                    print(e)
                    print("[ERROR] in client_receive()")

    # -- currently unused
    # returns the instructions as a string
    def instructions_as_text(self):
        text = ""
        for i in self.instructions:
            text += i
            text += "\n"
        return text

    # connects to the given IP addres (IP, port)
    def connect(self, addr):
        global ADDR
        global CLIENT
        global STATE
        print(f"Connecting to {addr}.")
        print(f"[STATE] {STATE}")

        # connection behavior depends on the connection state

        # simply connects to the server
        if STATE == START:
            try:
                CLIENT.connect(addr)
                STATE = CONNECTED
            except Exception as error:
                print(f"Connection ERROR in state {STATE}")
                print(error)
                STATE = START

        # connects to the server and closes connection to the current server if it has a different Address
        if STATE == CONNECTED:
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
                print(f"Connection ERROR in state {STATE}")
                print(error)
                STATE = NOT_CONNECTED

        # tries to create a connection (in case of an error)
        if STATE == NOT_CONNECTED:
            try:
                CLIENT.close()
                CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as error:
                print(f"Connection ERROR in state {STATE}")  # Debug
                print("Connection couldn't be closed")
            try:
                CLIENT.connect(addr)
                if self.username != "":
                    self.set_username()
                STATE = CONNECTED
            except Exception as error:
                print(f"Connection ERROR in state {STATE}")  # Debug
                print(error)
                STATE = NOT_CONNECTED


        print(f"[STATE] {STATE}")

        ADDR = addr
        self.update_status()

# Class EmojiButton inherits from QPushButton
# Button displays an emoji
# on Button press it will send the emoji to the server
class EmojiButton(QPushButton):
    def __init__(self, window, size, text="button"):
        super().__init__(text,window)
        self.setStyleSheet("font-size:" + str(size) + "px");
        self.setMaximumWidth(size + 23)
        self.setMaximumHeight(size + 15)
        self.mytext = text
        #self.setToolTip(emoji.demojize(text))
        self.setToolTip("")

    # prints and sends the text of the button
    def myprint(self):
        print(self.mytext)
        send(self.mytext)

    # resizes the button to the width x and the height y
    def set_size(self, x, y):
        self.setMaximumWidth(x)
        self.setMaximumHeight(y)






if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    status = app.exec_()
    w.is_running = False
    send(DISCONNECT_MESSAGE)
    sys.exit(status)
