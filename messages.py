from collections import deque, Counter
from typing import Dict

class Messages:
    
    npc_meter           = 0         # % how much of queue messages are the most common word / word combo
    npc_alert           = False     # is NPC-meter over threshold (most common word has to also appear >1 times)
    npc_threshold       = 75        # >= what % NPC-meter sets alert
    npc_word            = ""        # the most common word
    npc_word_count      = 0         # how many times most common word occurs in queue
    npc_word_mfc        = 0         # how many times most common word occurs most frequently
    npc_message         = ""        # the most common word / word combo
    min_same_word_count = 2         # how many of the same word has to appear at least to alert
    unique_chatters     = 0         # how many different users have chats in the queue

    SAME_WORD_THRESHOLD = 75        # how many % same count to connect next most common word to NPC-word
    SAME_FREQ_THRESHOLD = 75        # how many % same frequency to connect next most common word to NPC-word
    
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

        # updates info
        self.update_messages_info()

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


    def update_messages_info(self):
        """Updates NPC-meter, NPC-message, NPC-word, NPC-word count, NPC-alert and unique chatters"""
        self.update_npc_word()
        self.update_npc_meter()
        self.update_npc_message()
        self.update_npc_alert()

    def update_npc_word(self):
        """most common word in queue, how many of the messages contain it and most common times it appears in messages"""
        # counts all unique words
        unique_words = Counter()
        for user_word_counts in self.word_counts.values():
            unique_words.update(user_word_counts.keys())

        # ordered list of most common words and the counts
        most_common = unique_words.most_common()

        # finds most common word and its count
        self.npc_word, self.npc_word_count = most_common[0]

        # finds how many times the most common word appears the most
        self.npc_word_mfc = self.calculate_word_frequency(self.npc_word)

        # adds to the NPC-word if fits to thresholds
        for word, count in most_common[1:]:
            if (self.SAME_WORD_THRESHOLD / 100) <= (count / self.npc_word_count):
                if (self.SAME_FREQ_THRESHOLD / 100) <= (self.calculate_word_frequency(word) / self.npc_word_mfc):
                    self.npc_word += f" {word}"
    
    def calculate_word_frequency(self, word: str) -> int:
        """calculates how many times given word appears in user messages the most"""
        word_counts = {}
        for user_word_counts in self.word_counts.values():
            word_count = user_word_counts.get(word, 0)

            # adds count if over 0
            if 0 < word_count:
                word_counts[word_count] = word_counts.get(word_count, 0) + 1

        return max(word_counts, key=word_counts.get)

    def update_npc_meter(self):
        """% of unique chatters' messages that contain the most common word"""
        self.unique_chatters = len(self.word_counts)
        self.npc_meter = (self.npc_word_count / self.unique_chatters) * 100

    def update_npc_message(self):
        """most common word * most common times it appears in a message"""
        self.npc_message = ' '.join([self.npc_word] * self.npc_word_mfc)

    def update_npc_alert(self):
        """true if threshold and minimum same word count are exceeded"""
        self.npc_alert = self.npc_threshold <= self.npc_meter and self.min_same_word_count <= self.npc_word_count

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
    
    def get_unique_chatters(self) -> int:
        return self.unique_chatters
    
    def get_npc_word(self) -> str:
        return self.npc_word


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
    
    
