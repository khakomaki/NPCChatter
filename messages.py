from collections import deque, Counter
from typing import Dict

class Messages:
    
    npc_meter           = 0         # % how much of queue messages are the most common word / word combo
    npc_alert           = False     # is NPC-meter over threshold (most common word has to also appear >1 times)
    npc_threshold       = 75        # >= what % NPC-meter sets alert
    npc_message         = ""        # the most common word / word combo
    min_same_word_count = 5         # how many of the same word has to appear at least to alert
    
    def __init__(self, queue_length = 10):
        self.queue_length = queue_length
        self.message_queue = deque(maxlen=queue_length)
        self.word_counts: Dict[str, Counter] = {}

    def add(self, user: str, message: str) -> bool:
        """
        Adds message to queue as the latest. Counts message words to user's word counts.
        Pops last message if queue is full.
        """
        if len(self.message_queue) == self.message_queue.maxlen:
            self.pop()

        words = self.break_into_words(message)

        # adds words and their counters to user's word counts
        user_word_counts = self.word_counts.setdefault(user, Counter())
        user_word_counts += Counter(words)

        # adds to queue
        self.message_queue.appendleft((user, words))

        # recalculates NPC-meter
        self.calculate_npc_meter()

        return self.npc_alert

    def pop(self):
        """
        Removes oldest message from queue and decreases its words from user's word counts.
        Doesn't do anything if queue is empty.
        """
        if len(self.message_queue) < 1:
            return

        # removes from queue
        user, words = self.message_queue.pop()
        
        # updates word counts
        user_word_counts = self.word_counts.get(user, Counter())
        user_word_counts -= Counter(words)

        # removes from user word counts if it becomes empty
        if len(user_word_counts) < 1:
            self.word_counts.pop(user, None)


    def calculate_npc_meter(self):
        """
        Updates NPC-meter, NPC-message and NPC-alert.

        NPC-message: most common word * most common times it appears in a message
        NPC-meter: % of unique chatter's messages that contain most common word
        NPC-alert: true if threshold =< NPC-meter
        """
        # counts all unique words
        unique_words = Counter()
        for user_word_counts in self.word_counts.values():
            unique_words.update(user_word_counts.keys())

        # finds most common word
        most_npc_word, highest_count = unique_words.most_common(1)[0] # gives list of tuples, 0 is on top of the list

        # updates NPC-meter
        unique_chatters = len(self.word_counts)
        self.npc_meter = (highest_count / unique_chatters) * 100
        
        # finds how many times the most common word appears the most
        npc_word_counts = {}
        for user_word_counts in self.word_counts.values():
            npc_word_count = user_word_counts.get(most_npc_word, 0)

            # adds count if over 0
            if 0 < npc_word_count:
                npc_word_counts[npc_word_count] = npc_word_counts.get(npc_word_count, 0) + 1

        # updates NPC-message to most common word * most common count of it
        most_frequent_count = max(npc_word_counts, key=npc_word_counts.get)
        self.npc_message = ' '.join([most_npc_word] * most_frequent_count)

        # updates NPC-alert (bool threshold & count exceeded or same value)
        self.npc_alert = self.npc_threshold <= self.npc_meter and self.min_same_word_count <= highest_count

    def break_into_words(self, message: str):
        return message.split()

    def clear(self):
        """Clears messages, word counts and message related attributes."""
        self.message_queue.clear()
        self.word_counts.clear()
        self.npc_alert = False
        self.npc_message = ""
        self.npc_meter = 0

    def set_queue_length(self, length: int):
        """
        Clears messages and creates new deque.
        Previously queued messages are cleared.
        """
        self.clear()
        self.message_queue = deque(maxlen=length)   # throws error if trying to set invalid
        self.queue_length = length

    def get_queue_length(self) -> int:
        return self.message_queue.maxlen

    def set_threshold(self, threshold: int):
        self.npc_threshold = threshold

    def get_threshold(self) -> int:
        return self.npc_threshold

    def set_min_same_word_count(self, count: int):
        self.clear()
        self.min_same_word_count = count

    def get_min_same_word_count(self) -> int:
        return self.min_same_word_count

    def get_npc_message(self) -> str:
        return self.npc_message

    def is_npc_alert(self) -> bool:
        return self.npc_alert

    def howNPC(self) -> int:
        return self.npc_meter


if __name__ == "__main__":
    messages = Messages(5)

    if messages.add("user123", "KEKW KEKW KEKW ICANT"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("DEV", "TEST HELLO"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("chatter", "TEST TEST TEST TEST TEST TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("user123", "KEKW KEKW KEKW TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("DEV", "KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("other_username", "KEKW KEKW KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("Mod", "KEKW KEKW KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()
    
    
