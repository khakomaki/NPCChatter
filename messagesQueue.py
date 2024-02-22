from collections import deque

class MessagesQueue:
    """
    Class for storing messages into a queue, where the first message gets popped out first.
    
    Attributes:
        max_size (int) Maximum size of the queue.
        autopop (bool): Enable/disable automatically popping the last message if queue is full.
    """
    
    def __init__(self, max_size: int, autopop=True):
        """
        Initializes the queue.

        Args:
            max_size (int): Maximum size of the queue. Invalid values (<=0) are set to 1.
            autopop (bool, optional): Enable/disable automatically popping the last message if queue is full. Defaults to True.
        """

        if max_size <= 0:
            # sets default size if invalid queue size is given
            self.max_size = 1
        else:
            # sets queue size
            self.max_size = max_size
        
        self.messages = deque(maxlen=self.max_size)
        self.autopop = autopop
    
    def __str__(self) -> str:
        """
        Returns string representation of the queue. Messages are separated by newlines.

        Returns:
            str: Queue in a string form.
        """

        return "\n".join(self.messages)

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
        
        if self.max_size <= len(self.messages):
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
    
    def set_autopop(self, on: bool):
        """
        Sets autopop on/off.

        Args:
            on (bool): Is autopop on or off.
        """
        self.autopop = on

# full list
messages = MessagesQueue(3)
messages.add("hello")
messages.add("hi")
messages.add("good evening")
print(f"{messages}\n")

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

# pop empty queue
popped_message = messages.pop()
print(f"empty string pop: {popped_message}")