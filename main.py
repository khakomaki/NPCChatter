import logging
from terminal import NPCChatter
from connection import TwitchConnection

# sets up logging configuration
logging.basicConfig(level=logging.INFO, format="%(message)s")

if __name__ == "__main__":
    try:
        connection = TwitchConnection()
        npc = NPCChatter(connection)
        npc.run()
    except:
        logging.error("Couldn't establish connection. Either Twitch is down or credentials are wrong.")
        logging.info("Process terminated")
