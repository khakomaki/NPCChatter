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
    connected = False
    connection = None

    def __init__(self):
        self.oauth = os.environ.get("OAUTH_TOKEN_TWITCH")
        self.nickname = os.environ.get("NICKNAME")
        self.chat = os.environ.get("CHAT")

    def connect(self):
        if self.connected:
            raise TwitchConnectionError("connection is already established!")

        SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        SSLContext.load_verify_locations(cafile=os.path.relpath(certifi.where()))   # verifying certification for SSL connection

        self.connection = SSLContext.wrap_socket(socket.socket(), server_hostname=self.SERVER)  # SSL wrap
        self.connection.connect((self.SERVER, self.PORT))   # connects to server
        self.connected = True

        # starts receiving messages in a separate thread
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
        
        self.connection.send(f"PASS oauth:{self.oauth}\r\n".encode("utf-8"))    # send oauth token
        self.connection.send(f"NICK {self.nickname}\r\n".encode("utf-8"))       # send nickname
        self.connection.send(f"JOIN #{self.chat}\r\n".encode("utf-8"))          # join chat

    def disconnect(self):
        if not self.connected:
            raise TwitchConnectionError("connection is already closed!")
        
        self.connection.send(f"PART\r\n".encode("utf-8"))
        self.connection.close()
        self.connection = None
        self.connected = False

    def receive_messages(self):
        # listens until disconnected
        while self.connected:
            received_message = self.connection.recv(1024).decode("utf-8")
            
            if received_message:
                messages = received_message.split("\r\n")   # received message might contain multiple messages
                for message in messages:
                    print(message)
                    # self.respond(message)

    def respond(self, received_message):            # TODO: parse command part
        match str(received_message).startswith():
            case "PING":
                # sends keep-alive message
                self.connection.send(f"PONG {received_message}\r\n".encode("utf-8"))
            case "PART":
                # informs user, disconnects
                print("channel banned bot!")
                self.disconnect()
            case _:
                return

    def print_info(self):               # TODO delete
        print(self.oauth)
        print(self.nickname)
        print(self.chat)
        print(self.PORT)
        print(self.connected)

    def sleep_and_disconnect(self):     # TODO delete
        time.sleep(10)
        self.disconnect()


class TwitchConnectionError(Exception):
    pass


if __name__ == "__main__":
    connection = TwitchConnection()
    connection.print_info()
    connection.connect()
    connection.sleep_and_disconnect()
