from terminal import NPCChatter
from connection import TwitchConnection

if __name__ == "__main__":
    connection = TwitchConnection()
    npc = NPCChatter(connection)
    npc.run()
