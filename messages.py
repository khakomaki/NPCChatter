from queue import Queue

class Messages:
    
    npc_meter = 0           # % how much of queue messages are the most common word / word combo
    npc_alert = False       # is NPC-meter over threshold (most common word has to also appear >1 times)
    npc_threshold = 75      # >= what % NPC-meter sets alert
    npc_message = ""        # the most common word / word combo
    min_same_word_count = 2 # how many of the same word has to appear at least to alert
    
    def __init__(self, queue_length):
        self.message_queue = Queue(maxsize = queue_length)
        self.word_counts = {}

    def add(self, message):
        # unqueues last if list is full
        if self.message_queue.full():
            self.remove()

        self.message_queue.put(message)
        
        # adds words to dictionary
        words = self.break_into_words(message)
        for word in words:
            count = self.word_counts.get(word, 0)   # gets the count, defaults to 0 if key doesn't exist
            self.word_counts[word] = count + 1      # increments count by 1

        # recalculates NPC-meter
        self.calculate_npc_meter()

        return self.npc_alert

    def remove(self):
        message = self.message_queue.get()
        words = self.break_into_words(message)
        for word in words:
            count = self.word_counts.get(word)
            self.word_counts[word] = count - 1      # decreases count by 1
            if self.word_counts[word] < 1:          # removes word from dictionary if count falls under 1
                self.word_counts.pop(word)

    def break_into_words(self, message):
        return str(message).split()

    def calculate_npc_meter(self):
        highest_count = -1  # assumes that dictionary doesn't count under 0
        highest_count_words = ""
        word_count = 0
        same_word_count = 0

        # makes a string of words with highest count
        for word, count in self.word_counts.items():
            word_count = word_count + count

            if highest_count < count:       # higher count is found
                highest_count = count
                highest_count_words = word
                same_word_count = 1
            elif highest_count == count:    # word with the highest count is found
                highest_count_words = f"{highest_count_words} {word}"
                same_word_count = same_word_count + 1
        
        self.npc_message = highest_count_words

        # how many percent of words are the top similar words
        self.npc_meter = 100 * highest_count * same_word_count / word_count

        # sets alert
        if self.npc_threshold <= self.npc_meter and self.min_same_word_count <= highest_count:
            self.npc_alert = True

    def clear(self):
        self.message_queue = Queue(maxsize = self.message_queue.qsize())
        self.word_counts.clear()
        self.npc_alert = False
        self.npc_message = ""
        self.npc_meter = 0

    def set_queue_length(self, length):
        self.message_queue = Queue(maxsize = length)

    def set_threshold(self, threshold):
        self.npc_threshold = threshold

    def set_min_same_word_count(self, count):
        self.min_same_word_count = count

    def get_npc_message(self):
        return self.npc_message

    def is_npc_alert(self):
        return self.npc_alert

    def howNPC(self) -> int:
        return self.npc_meter


if __name__ == "__main__":
    messages = Messages(5)
    if messages.add("KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("TEST"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()

    if messages.add("KEKW"):
        print(f"{messages.howNPC()} - {messages.npc_message}")
        messages.clear()
