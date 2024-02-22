from collections import deque

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

        Returns:
            str: Queue in a string form.
        """

        return "\n".join(self.messages)
    
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

    def add(self, message: str) -> bool:
        """
        Adds a message to the queue.
        Pops last message automatically if the queue is full.

        Args:
            message (str): Message to be added.

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
        
        # adds message, returns if the queue was full
        self.messages.append(message)
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
        
        if max_size <= 0:
            # doesn't change size if invalid value is given
            return

# full list
messages = MessagesQueue(3)
messages.add("hello")
messages.add("hi")
messages.add("good evening")
print(f"{messages}\n")
print(f"max size of the queue: {messages.max_size()}")
print(f"current count of the queue: {messages.count()}")

# add to full list (autopop on)
messages.add("chatting chatting chatting...")
print(f"{messages}\n")

# add to full list (autopop off)
messages.set_autopop(False)
messages.add("test message")
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