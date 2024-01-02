import socket
import ssl
import certifi
import threading
import time
import os
import random
import logging
import requests
from messages import Messages
from dotenv import load_dotenv

# loads .env variables
load_dotenv()

# sets up logging configuration
logging.basicConfig(level=logging.INFO, format="%(message)s")

class TwitchConnection:

    PORT                    = 6697
    SERVER                  = "irc.chat.twitch.tv"
    CHAT_COMMAND_SYMBOL     = '!'

    connected               = False
    connection              = None
    min_message_interval    = 30
    random_wait_time_lower  = 0.1
    random_wait_time_upper  = 2
    last_bot_message_time   = 0
    npc_response_enabled    = True
    last_bot_message        = ""
    same_message_count      = 0
    max_same_message_count  = 1
    sub_emotes_enabled      = False
    follower_emotes_enabled = True

    def __init__(self):
        self.oauth = os.environ.get("OAUTH_TOKEN_TWITCH")
        self.nickname = os.environ.get("NICKNAME")
        self.chat = os.environ.get("CHAT")
        self.client_id = os.environ.get("CLIENT_ID")
        self.thread_lock = threading.Lock()
        self.chat_messages = Messages()

        self.broadcaster_id = self.get_broadcaster_id()
        self.channel_sub_emotes, self.channel_follower_emotes = self.get_channel_emotes(self.broadcaster_id)
        print(self.broadcaster_id)
        print(self.channel_sub_emotes)
        print(self.channel_follower_emotes)

    def connect(self):
        """Creates SSL socket, tries to establish SSL connection to the server, authenticate and join a chat."""
        if self.is_connected():
            raise TwitchConnectionError("Connection is already established!")

        # context for SSL connection
        SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        SSLContext.load_verify_locations(cafile=os.path.relpath(certifi.where()))   # verifying certification for SSL connection

        # SSL wrap
        self.connection = SSLContext.wrap_socket(socket.socket(), server_hostname=self.SERVER)
        self.open_connection()

        # starts receiving messages in a separate thread
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()
        
        # authentication & chat joining messages
        if self.is_connected():
            self.send_server_message(f"PASS oauth:{self.oauth}")    # send oauth token
            self.send_server_message(f"NICK {self.nickname}")       # send nickname
            self.send_server_message(f"JOIN #{self.chat}")          # join chat

    def disconnect(self):
        """
        Sends parting message to server.
        Doesn't close the connection, waits for server to send message.
        """
        if not self.is_connected():
            logging.info("Connection already closed")
            return

        self.send_server_message(f"PART #{self.chat}")

    def open_connection(self):
        """Tries to open a connection to the server."""
        with self.thread_lock:  # locks threads during opening
            try:
                self.connection.connect((self.SERVER, self.PORT))
                self.connected = True

            except ssl.SSLError as exception:
                logging.error(f"Problems with SSL connecting to Twitch server: {exception}")
                self.connected = False
            
            except socket.error as exception:
                logging.error(f"Problems with socket connecting to Twitch server: {exception}")
                self.connected = False

    def close_connection(self):
        """Closes connection to the server."""
        with self.thread_lock:  # locks threads during closing
            self.connection.close()
            self.connected = False

    def receive_messages(self):
        """
        Listens messages from the connection while connected.
        Processes received messages.
        """
        while self.connected:
            received_message = self.connection.recv(1024).decode("utf-8")
            
            if received_message:
                messages = received_message.split("\r\n")   # received message might contain multiple messages
                for message in messages:
                    if len(message) < 1:
                        continue
                    logging.debug(message)
                    self.process_message(message)

    def process_message(self, received_message):
        """Reacts to message according to parsed command."""
        user, _, command, parameters = self.parse_message(received_message)

        match command:
            case "PRIVMSG":
                logging.debug(f"{user}: {parameters}")
                self.handle_bot_command(parameters)
                self.handle_npc_messages(user, parameters)
            case "PING":
                # keep-alive message
                self.send_server_message(f"PONG {parameters}")
            case "PART":
                logging.info("Twitch closed connection")
                self.close_connection()
            case "NOTICE":
                logging.warning("Twitch: failed to authenticate")
            case "JOIN":
                logging.info(f"Joined channel #{self.chat}")
            case "421":
                logging.warning("Twitch: unsupported IRC command")
            case "001":
                logging.info("Authentication successful")
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
                logging.warning(f"Unexpected command: {command}")
        
    def parse_message(self, message: str):
        """Parses the given IRC message."""
        nick = None
        host = None
        command = None
        parameters = None

        index = 0

        # skips tags
        if message[index] == '@':
            index = message.find(' ', index) + 1

        # skips nickname & host
        if message[index] == ':':
            end_index = message.find(' ', index)

            # parses nickname and host from source part
            nickhost = message[index + 1:end_index]
            if 0 < len(nickhost):
                nickhost_parts = nickhost.split('!')
                nick = nickhost_parts[0]
                if 1 < len(nickhost_parts):
                    host = nickhost_parts[1]

            index = end_index + 1

        # checks if message has parameters, sets end-index accordingly
        end_index = message.find(':', index)
        if end_index < 0:
            end_index = len(message)

        # command & channel
        command_parts = message[index:end_index].strip().split(' ')
        command = command_parts[0]
        # if 1 < len(command_parts):
        #     channel = command_parts[1]

        # parameters
        if index < end_index + 1:
            parameters = message[end_index + 1:len(message)]

        return nick, host, command, parameters
    
    def handle_bot_command(self, parameters: str):
        """Checks if the message is bot command, parses command part and executes command if found."""
        if parameters[0] == self.CHAT_COMMAND_SYMBOL:
            # parses command part
            command_end = parameters.find(' ')
            if command_end < 0:
                command_end = len(parameters)
            bot_command = parameters[1:command_end].upper()
        else:
            return

        match bot_command:
            case "NPC":
                npc_meter = self.chat_messages.howNPC()
                self.send_chat_message(f"NPC-meter: {npc_meter}%")
            case _:
                pass

    def handle_npc_messages(self, user: str, parameters: str):
        """Adds message to queue, reacts to NPC-alert if NPC-messages are enabled."""
        threshold_crossed = self.chat_messages.add(user, parameters)

        # sends NPC-message if threshold is crossed and NPC-messages enabled
        if threshold_crossed and self.npc_response_enabled:
            self.send_bot_message(self.chat_messages.get_npc_message())
            self.chat_messages.clear()

    def send_server_message(self, message: str):
        """Sends message to server. Ends every line with CR + LF."""
        if not self.is_connected():
            raise TwitchConnectionError("Can't send messages because connection isn't established!")

        # locks threads during sending to avoid collisions
        with self.thread_lock:
            self.connection.send(f"{message}\r\n".encode("utf-8"))

    def send_chat_message(self, message: str):
        """Sends message to Twitch chat."""

        # updates bot message information
        self.update_last_bot_message(message)
        
        # sends if ok
        if self.can_send(message):
            self.send_server_message(f"PRIVMSG #{self.chat} :{message}")
            self.last_bot_message_time = time.time()
            logging.info(f"Sent message: '{message}'")

    def send_bot_message(self, message: str):
        """
        Same as sending chat message, but prevents sending messages too frequently.
        Preferred for automated messages.
        """
        # random delay before sending message
        random_wait_time = random.uniform(self.random_wait_time_lower, self.random_wait_time_upper)
        time.sleep(random_wait_time)

        # sends as chat message
        self.send_chat_message(message)

    def update_last_bot_message(self, message: str):
        if message == self.last_bot_message:
            self.same_message_count += 1
        else:
            self.same_message_count = 1
            self.last_bot_message = message

    def can_send(self, message: str) -> bool:
        # doesnt't send if it would exceed maximum same message count
        if self.max_same_message_count < self.same_message_count:
            return False
        
        # doesn't send if there's not enough time since last message
        if 0 <= self.last_bot_message_time + self.min_message_interval - time.time():
            return False
        
        # doesn't send if the message contains sub emote
        if not self.sub_emotes_enabled and message.split(' ')[0] in self.channel_sub_emotes:
            logging.info("Didn't send message because it contains sub emote!")
            return False
        
        # doesn't send if the message contains follower emote
        if not self.follower_emotes_enabled and message.split(' ')[0] in self.channel_follower_emotes:
            logging.info("Didn't send message because it contains follower emote!")
            return False
        
        return True
    
    def get_channel_emotes(self, broadcaster_id: str) -> list[tuple]:
        # sends request for channel emote info
        url = f"https://api.twitch.tv/helix/chat/emotes?broadcaster_id={broadcaster_id}"
        headers = {
            "Authorization": f"Bearer {self.oauth}",
            "Client-ID": self.client_id
        }
        response = requests.get(url, headers=headers)

        # parses response for channel emotes
        if response.status_code == 200:
            data = response.json()
            if data:
                sub_emotes = []
                follower_emotes = []

                # add sub emotes
                for emote in data.get("data", []):
                    emote_type = emote.get("emote_type", None)
                    emote_name = emote.get("name", None)

                    if emote_type == "subscriptions" and emote_name != None:
                        sub_emotes.append(emote_name)

                    if emote_type == "follower" and emote_name != None:
                        follower_emotes.append(emote_name)
                return sub_emotes, follower_emotes
            else:
                raise TwitchConnectionError(f"Problems getting channel emotes: {response.status_code}")


    def get_broadcaster_id(self) -> str:
        # sends request for broadcaster info
        url = f"https://api.twitch.tv/helix/users?login={self.chat}"
        headers = {
            "Authorization": f"Bearer {self.oauth}",
            "Client-ID": self.client_id
        }
        response = requests.get(url, headers=headers)

        # parses response for id
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                return str(data[0]["id"])
            else:
                raise TwitchConnectionError(f"Couldn't get channel id for #{self.chat}")
        else:
            raise TwitchConnectionError(f"Problems getting channel id: {response.status_code}")


    def is_connected(self):
        with self.thread_lock:
            return self.connected

    def toggle_npc_response(self):
        self.npc_response_enabled = not self.npc_response_enabled
        logging.info(f"NPC-response enabled: {self.npc_response_enabled}")

    def set_queue_length(self, length: int):
        self.chat_messages.set_queue_length(length)

    def get_queue_length(self) -> int:
        return self.chat_messages.get_queue_length()

    def set_min_same_word_count(self, count: int):
        self.chat_messages.set_min_same_word_count(count)

    def get_min_same_word_count(self) -> int:
        return self.chat_messages.get_min_same_word_count()

    def set_threshold(self, percentage: int):
        self.chat_messages.set_threshold(percentage)

    def get_threshold(self) -> int:
        return self.chat_messages.get_threshold()

    def set_max_same_bot_message_count(self, count: int):
        self.max_same_message_count = count

    def get_max_same_bot_message_count(self) -> int:
        return self.max_same_message_count
    
    def set_min_bot_message_interval(self, interval: int):
        self.min_message_interval = interval

    def get_min_bot_message_interval(self) -> int:
        return self.min_message_interval

    def sleep_and_disconnect(self):     # TODO delete
        time.sleep(30)
        self.disconnect()


class TwitchConnectionError(Exception):
    pass


if __name__ == "__main__":
    connection = TwitchConnection()
    connection.connect()
    connection.sleep_and_disconnect()
