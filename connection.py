import socket
import ssl
import certifi
import threading
import time
import os
import random
from messages import Messages
from dotenv import load_dotenv

load_dotenv()   # loads .env variables

class TwitchConnection:

    PORT = 6697
    SERVER = "irc.chat.twitch.tv"
    CHAT_COMMAND_SYMBOL = "!"
    connected = False
    connection = None

    min_message_interval    = 10
    random_wait_time_lower  = 0.1
    random_wait_time_upper  = 2
    last_bot_message_time   = 0
    npc_response_enabled    = True

    def __init__(self):
        self.oauth = os.environ.get("OAUTH_TOKEN_TWITCH")
        self.nickname = os.environ.get("NICKNAME")
        self.chat = os.environ.get("CHAT")
        self.thread_lock = threading.Lock()
        self.chat_messages = Messages(5)

    def connect(self):
        if self.connected:
            raise TwitchConnectionError("Connection is already established!")

        SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        SSLContext.load_verify_locations(cafile=os.path.relpath(certifi.where()))   # verifying certification for SSL connection

        self.connection = SSLContext.wrap_socket(socket.socket(), server_hostname=self.SERVER)  # SSL wrap
        self.open_connection()

        # starts receiving messages in a separate thread
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
        
        if self.connected:
            # authentication & chat joining messages
            self.send_server_message(f"PASS oauth:{self.oauth}")    # send oauth token
            self.send_server_message(f"NICK {self.nickname}")       # send nickname
            self.send_server_message(f"JOIN #{self.chat}")          # join chat

    def disconnect(self):
        if not self.connected:
            print("Connection already closed")
            return

        self.send_server_message("PART")
        self.close_connection()
        print("Closed connection")

    def open_connection(self):
        # locks threads during opening
        with self.thread_lock:
            try:
                self.connection.connect((self.SERVER, self.PORT))
                self.connected = True
            except Exception as exception:
                print(f"Problems connecting to Twitch server: {exception}")
                self.connected = False

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
                    # print(message)
                    self.process_message(message)

    def process_message(self, received_message):
        command, user, parameters = self.parse_message(received_message)

        match command:
            case "PRIVMSG":
                print(f"{user}: {parameters}")

                # sends NPC-message if threshold is crossed and NPC-messages enabled
                threshold_crossed = self.chat_messages.add(user, parameters)
                if threshold_crossed and self.npc_response_enabled:
                    self.send_bot_message(self.chat_messages.get_npc_message())
                    self.chat_messages.clear()
            case "PING":
                # keep-alive message
                self.send_server_message(f"PONG {parameters}")
            case "PART":
                print("Twitch closed connection")
                self.close_connection()
            case "NOTICE":
                print("Twitch: failed to authenticate")
            case "JOIN":
                print("Joined channel")
            case "421":
                print("Wwitch: unsupported IRC command")
            case "001":
                print("Authentication successful")
            case "002":
                pass
            case "003":
                pass
            case "004":
                pass
            case "353":
                pass
            case "366":
                pass
            case "372":
                pass
            case "375":
                pass
            case "376":
                pass
            case _:
                print(f"Unexpected command: {command}")
        
    def parse_message(self, message: str):
        command = None
        channel = None
        parameters = None

        index = 0

        # skips tags
        if message[index] == '@':
            index = message.find(' ', index) + 1

        # skips nickname & host
        if message[index] == ':':
            index = message.find(' ', index) + 1

        # checks if message has parameters, sets end-index accordingly
        end_index = message.find(':', index)
        if end_index < 0:
            end_index = len(message)

        # command & channel
        command_parts = message[index:end_index].strip().split(' ')
        command = command_parts[0]
        if 1 < len(command_parts):
            channel = command_parts[1]

        # parameters
        if index < end_index + 1:
            parameters = message[end_index + 1:len(message)]

        return command, channel, parameters

    def send_server_message(self, message):
        if not self.connected:
            raise TwitchConnectionError("Can't send messages because connection isn't established!")

        # locks threads during sending to avoid collisions
        with self.thread_lock:
            self.connection.send(f"{message}\r\n".encode("utf-8"))

    def send_chat_message(self, message):
        self.send_server_message(f"PRIVMSG #{self.nickname} :{message}")

    def send_bot_message(self, message):
        # random delay before sending message
        random_wait_time = random.uniform(self.random_wait_time_lower, self.random_wait_time_upper)
        time.sleep(random_wait_time)
        
        # sends message if there's enough time since last message
        if self.last_bot_message_time + self.min_message_interval - time.time() < 0:
            self.send_chat_message(message)
            self.last_bot_message_time = time.time()

    def set_npc_response_enabled(self, enabled: bool):
        self.npc_response_enabled = enabled

    def print_info(self):               # TODO delete
        print(self.oauth)
        print(self.nickname)
        print(self.chat)
        print(self.PORT)
        print(self.connected)

    def sleep_and_disconnect(self):     # TODO delete
        time.sleep(30)
        self.disconnect()


class TwitchConnectionError(Exception):
    pass


if __name__ == "__main__":
    connection = TwitchConnection()
    connection.connect()
    connection.sleep_and_disconnect()
