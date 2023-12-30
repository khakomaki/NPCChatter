from collections import deque, Counter

class Messages:
    
    npc_meter = 0           # % how much of queue messages are the most common word / word combo
    npc_alert = False       # is NPC-meter over threshold (most common word has to also appear >1 times)
    npc_threshold = 75      # >= what % NPC-meter sets alert
    npc_message = ""        # the most common word / word combo
    min_same_word_count = 3 # how many of the same word has to appear at least to alert
    
    
    def __init__(self, queue_length: int):
        self.message_queue = deque(maxlen=queue_length)
        self.word_counts = {}

    def add(self, user: str, message: str):
        # pops last message if queue is full
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
        # return if queue is empty
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
        # counts all unique words
        unique_words = Counter()
        for user_word_counts in self.word_counts.values():
            unique_words.update(user_word_counts.keys())

        # finds most common word
        most_npc_word, highest_count = unique_words.most_common(1)[0] # gives list of tuples, 0 is on top of the list

        # updates NPC-meter & NPC-message
        unique_chatters = len(self.word_counts)
        self.npc_meter = (highest_count / unique_chatters) * 100
        self.npc_message = most_npc_word
        
        # updates NPC-alert (bool threshold & count exceeded or same value)
        self.npc_alert = self.npc_threshold <= self.npc_meter and self.min_same_word_count <= highest_count

    def break_into_words(self, message: str):
        return str(message).split()

    def clear(self):
        self.message_queue.clear()
        self.word_counts.clear()
        self.npc_alert = False
        self.npc_message = ""
        self.npc_meter = 0

    def set_queue_length(self, length: int):
        self.message_queue = deque(maxlen = length)

    def set_threshold(self, threshold: int):
        self.npc_threshold = threshold

    def set_min_same_word_count(self, count: int):
        self.min_same_word_count = count

    def get_npc_message(self) -> str:
        return self.npc_message

    def is_npc_alert(self) -> bool:
        return self.npc_alert

    def howNPC(self) -> int:
        return self.npc_meter


if __name__ == "__main__":
    messages = Messages(5)

    if messages.add("user123", "KEKW KEKW KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("DEV", "TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("chatter", "TEST TEST TEST TEST TEST TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("user123", "KEKW TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("DEV", "KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("other_username", "KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("Mod", "KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()
