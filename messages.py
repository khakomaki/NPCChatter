from messagesQueue import MessagesQueue
from collections import Counter

class NPCMessages:
    """
    Stores messages for calculating NPC statistics.
    """
    
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
        """
        Initalizes NPCMessages.

        Args:
            queue_length (int, optional): Maximum length of the message queue. Defaults to 10.
        """

        self.message_queue = MessagesQueue(queue_length)

    def add(self, user: str, message: str) -> bool:
        """
        Adds message to queues.
        Pops last message if queue is full.

        Args:
            user (str): Message sender.
            message (str): Message to be added.

        Returns:
            bool: Is the npc alert on.
        """

        # adds to queue & updates statistics
        self.message_queue.add(user, message)
        self.update_messages_info()

        return self.npc_alert

    def pop(self) -> tuple:
        """
        Removes oldest message from queue & updates statistics.
        """

        # pops from queue & updates statistics
        popped_message = self.message_queue.pop()
        self.update_messages_info()

        return popped_message

    def update_messages_info(self):
        """Updates NPC-statistics"""
        self.update_user_words()
        self.update_npc_word()
        self.update_npc_meter()
        self.update_npc_message()
        self.update_npc_alert()

    def update_user_words(self):
        """Updates word counts of each chatter"""

        # replaces old dictionary
        self.user_word_counts = {}

        for message_info in self.message_queue.messages:
            # adds word counts to users
            user, _, parameters = message_info
            if self.user_word_counts.get(user):
                self.user_word_counts[user] += parameters['word_counter']
            else:
                self.user_word_counts[user] = parameters['word_counter']

    def update_npc_word(self):
        """most common word in queue, how many of the messages contain it and most common times it appears in messages"""
        
        # counts all unique words
        unique_words = Counter()
        for user_word_count in self.user_word_counts.values():
            unique_words.update(user_word_count)

        
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

        for user_word_count in self.user_word_counts.values():
            # counts words in the message
            word_count = user_word_count.get(word, 0)

            # adds count if over 0
            if 0 < word_count:
                word_counts[word_count] = word_counts.get(word_count, 0) + 1

        return max(word_counts, key=word_counts.get)

    def update_npc_meter(self):
        """% of unique chatters' messages that contain the most common word"""
        npc_word_message_count = 0

        # count of user messages including npc word
        for user_word_count in self.user_word_counts.values():
            
            # npc word might consist of multiple words
            words = self.npc_word.split()
            for word in words:
                if word in user_word_count:
                    npc_word_message_count += 1
                    break
        
        # unique chatters
        self.unique_chatters = len(self.user_word_counts)

        # avoid division by 0
        if self.unique_chatters <= 0:
            self.npc_meter = 0
            return
        
        # calculate percentage
        self.npc_meter = (npc_word_message_count / self.unique_chatters) * 100

    def update_npc_message(self):
        """most common word * most common times it appears in a message"""
        self.npc_message = ' '.join([self.npc_word] * self.npc_word_mfc)

    def update_npc_alert(self):
        """true if threshold and minimum same word count are exceeded"""
        self.npc_alert = self.npc_threshold <= self.npc_meter and self.min_same_word_count <= self.npc_word_count

    def clear(self):
        """Clears messages, word counts and message related attributes."""
        self.message_queue.clear()
        self.npc_alert = False
        self.npc_message = ""
        self.npc_meter = 0

    def set_queue_length(self, length: int):
        """Sets new queue max length"""
        self.message_queue.set_size(length)

    def get_queue_length(self) -> int:
        """Gives queue max length"""
        return self.message_queue.max_size()

    def set_threshold(self, threshold: int):
        """Sets threshold (NPC-meter%) to send NPC-message"""
        self.npc_threshold = threshold

    def get_threshold(self) -> int:
        """Gives NPC-meter% threshold"""
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


messages = NPCMessages(5)
messages.set_threshold(60)
messages.set_min_same_word_count(3)

messages.add("user123", "KEKW KEKW KEKW ICANT")
messages.add("dev", "TEST HELLO")
messages.add("bananaman", "banana")
messages.add("chatter", "TEST TEST TEST TEST TEST TEST")
messages.add("user123", "KEKW KEKW KEKW TEST")

print(f"How NPC: {messages.howNPC()}")

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