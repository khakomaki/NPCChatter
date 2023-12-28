import socket
import ssl
import certifi
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()   # loads .env variables

class TwitchConnection:

    PORT = 6697
    SERVER = "irc.chat.twitch.tv"
    CHAT_COMMAND_SYMBOL = "!"
    connected = False
    connection = None

    def __init__(self):
        self.oauth = os.environ.get("OAUTH_TOKEN_TWITCH")
        self.nickname = os.environ.get("NICKNAME")
        self.chat = os.environ.get("CHAT")
        self.thread_lock = threading.Lock()

    def connect(self):
        if self.connected:
            raise TwitchConnectionError("connection is already established!")

        SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        SSLContext.load_verify_locations(cafile=os.path.relpath(certifi.where()))   # verifying certification for SSL connection

        self.connection = SSLContext.wrap_socket(socket.socket(), server_hostname=self.SERVER)  # SSL wrap
        self.open_connection()

        # starts receiving messages in a separate thread
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
        
        # authentication & chat joining messages
        self.send_server_message(f"PASS oauth:{self.oauth}")    # send oauth token
        self.send_server_message(f"NICK {self.nickname}")       # send nickname
        self.send_server_message(f"JOIN #{self.chat}")          # join chat

    def disconnect(self):
        if not self.connected:
            raise TwitchConnectionError("connection is already closed!")
            
        self.send_server_message("PART")
        self.close_connection()

    def open_connection(self):
        # locks threads during opening
        with self.thread_lock:
            self.connection.connect((self.SERVER, self.PORT))
            self.connected = True

    def close_connection(self):
        # locks threads during closing
        with self.thread_lock:
            self.connection.close()
            self.connected = False

    def receive_messages(self):
        # listens until disconnected
        while self.connected:
            received_message = self.connection.recv(1024).decode("utf-8")
            
            if received_message:
                messages = received_message.split("\r\n")   # received message might contain multiple messages
                for message in messages:
                    if len(message) < 1:
                        continue
                    print(message)
                    # self.respond(message)

    def respond(self, received_message):            # TODO: parse command part
        match str(received_message).startswith():
            case "PING":
                # keep-alive message
                self.send_server_message(f"PONG {received_message}")
            case "PART":
                self.close_connection()
            case _:
                return

    def send_server_message(self, message):
        if not self.connected:
            raise TwitchConnectionError("can't send messages because connection isn't established!")

        # locks threads during sending to avoid collisions
        with self.thread_lock:
            self.connection.send(f"{message}\r\n".encode("utf-8"))

    def send_chat_message(self, message):
        self.send_server_message(f"PRIVMSG #{self.nickname} :{message}")

    def print_info(self):               # TODO delete
        print(self.oauth)
        print(self.nickname)
        print(self.chat)
        print(self.PORT)
        print(self.connected)

    def sleep_and_disconnect(self):     # TODO delete
        time.sleep(20)
        self.disconnect()


class TwitchConnectionError(Exception):
    pass


if __name__ == "__main__":
    connection = TwitchConnection()
    connection.print_info()
    connection.connect()
    connection.sleep_and_disconnect()
