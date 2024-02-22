from collections import Counter, deque

class MessagesQueue:
    """
    Class for storing messages into a queue, where the first message gets popped out first.
    
    Attributes:
        autopop (bool): Enable/disable automatically popping the last message if queue is full.
    """
    
    def __init__(self, max_size: int, autopop=True):
        """
        Initializes the queue.

        Args:
            max_size (int): Maximum size of the queue. Invalid values (<=0) are set to 1.
            autopop (bool, optional): Enable/disable automatically popping the last message if queue is full. Defaults to True.
        """

        # default for invalid sizes
        size = 1

        if 0 < max_size:
            # sets queue size
            size = max_size
        
        self.messages = deque(maxlen=size)
        self.autopop = autopop
    
    def __str__(self) -> str:
        """
        Returns string representation of the queue. Messages are separated by newlines.
        Doesn't print extra parameters.
        
        Example:
            "Donald Duck: hi chat!"
            "Mickey Mouse: hi Donald!"
            "Harry Potter: Abracadabra"

        Returns:
            str: Queue in a string form.
        """

        return "\n".join(f"{user}: {user_message}, {params}" for user, user_message, params in self.messages)
    
    def max_size(self) -> int:
        """
        Returns the max size of the queue.

        Returns:
            int: Max size of the queue. 
        """
        return self.messages.maxlen
    
    def count(self) -> int:
        """
        Returns how many messages are in the queue.

        Returns:
            int: Message count.
        """

        return len(self.messages)

    def add(self, username: str, message: str, parameters: dict = None) -> bool:
        """
        Adds a message to the queue.
        Pops last message automatically if the queue is full.

        Args:
            username (str): Message sender.
            message (str): Message to be added.
            parameters (dict, optional): Extra parameters related to message.

        Returns:
            bool: Boolean for "was the queue full?". 
        """
        full = False
        
        if self.max_size() <= len(self.messages):
            # queue is full
            full = True

            if self.autopop:
                # pops the last message on autopop
                self.pop()
            else:
                # returns that queue was full without adding
                return full
        
        # creates a dictionary if there isn't yet
        if parameters == None:
            parameters = {}

        # adds word counts to parameters
        word_counts = Counter(message.split())
        parameters['word_counter'] = word_counts

        # adds message, returns if the queue was full
        self.messages.append((username, message, parameters))
        return full

    def pop(self) -> str:
        """
        Removes the last message from the queue.

        Returns:
            str: Popped message. None if the queue was empty.
        """

        if len(self.messages) <= 0:
            # returns None when popping from empty list
            return None
        
        return self.messages.popleft()
    
    def clear(self):
        """
        Clears the message queue.
        """
        self.messages.clear()
    
    def set_autopop(self, on: bool):
        """
        Sets autopop on/off.

        Args:
            on (bool): Is autopop on or off.
        """
        self.autopop = on

    def set_size(self, max_size: int):
        """
        Sets new queue size. Pops oldest messages if they don't fit to new size.
        Doesn't change size if invalid value is given.

        Args:
            max_size (int): New maximum queue size.
        """

        if max_size <= 0:
            # doesn't change size if invalid value is given
            return
        
        # appends old messages to new queue
        new_queue = deque(maxlen=max_size)
        while self.messages:
            new_queue.append(self.messages.popleft())
        
        # replaces old queue with new
        self.messages = new_queue

if __name__ == '__main__':
    
    # full list
    messages = MessagesQueue(3)
    messages.add("user123", "hello")
    messages.add("Donald Duck", "hi", {"subscriber": True})
    messages.add("Mickey Mouse", "good evening")
    print(f"{messages}\n")
    print(f"max size of the queue: {messages.max_size()}")
    print(f"current count of the queue: {messages.count()}")

    # add to full list (autopop on)
    messages.add("Donald Duck", "chatting chatting chatting...", {"subscriber": True})
    print(f"{messages}\n")

    # add to full list (autopop off)
    messages.set_autopop(False)
    messages.add("dev", "test message", {"developer_code": 3})
    print(f"{messages}\n")

    # pop last x2
    messages.pop()
    messages.pop()
    print(f"{messages}\n")

    # pop and take last
    popped_message = messages.pop()
    print(f"popped message: {popped_message}")
    print(f"current count of the queue: {messages.count()}\n")

    # pop empty queue
    popped_message = messages.pop()
    print(f"empty string pop: {popped_message}")

    # changing queue size (no messages)
    messages.set_size(5)
    print(f"{messages}\n")

    # new messages
    messages.add("Pluto", "WOOF!")
    messages.add("Hello Kitty", "meow")
    messages.add("picky piglet", "oink")
    messages.add("Ron Weasly", "that's rubbish!")
    print(f"{messages}\n")

    # changing queue size
    messages.set_size(2)
    print(f"{messages}\n")