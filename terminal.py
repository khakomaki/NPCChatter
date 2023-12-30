from connection import *

class NPCChatter:

    same_word_count = 3
    history_size = 5
    min_message_interval = 10
    max_message_interval = 60

    def __init__(self, connection: TwitchConnection):
        self.connection = connection
        self.commands = {
            "CON": NPCCommand(self.connect, "connects to chat"),
            "DISC": NPCCommand(self.disconnect, "disconnects from chat"),
            "EXIT": NPCCommand(self.exit, "closes the NPCChatter"),
            "INFO": NPCCommand(self.print_info, "lists current attribute values"),
            "HELP": NPCCommand(self.print_help, "lists all of the commands with help texts"),
            "HS": NPCCommand(self.set_history_size, "set history size, how many messages are stored until forgetting"),
            "MAXD": NPCCommand(self.set_max_message_interval, "set maximum of random delay between messages"),
            "MIND": NPCCommand(self.set_min_message_interval, "set minimum of random delay between messages"),
            "MSG": NPCCommand(self.send_message, "sends message to chat"),
            "WC": NPCCommand(self.set_same_word_count, "how many times a word has to at least appear to consider it npc"),
        }

    def set_same_word_count(self, *args):
        self.set_num_attr("same_word_count", *args)
        self.connection.set_min_same_word_count(self.same_word_count)

    def set_history_size(self, *args):
        self.set_num_attr("history_size", *args)
        self.connection.set_queue_length(self.history_size)

    def set_min_message_interval(self, *args):
        self.set_num_attr("min_message_interval", *args)

    def set_max_message_interval(self, *args):
        self.set_num_attr("max_message_interval", *args)

    def connect(self):
        self.connection.connect()

    def disconnect(self):
        self.connection.disconnect()

    def send_message(self, *args):
        # merges arguments to 1 string
        message = ' '.join(map(str, args))
        self.connection.send_chat_message(message)

    def print_info(self, *_):
        print("========== Chatter settings info ==========")
        print(f"Same word count: {self.same_word_count}")
        print(f"History size: {self.history_size}")
        print(f"Minimum message interval: {self.min_message_interval}")
        print(f"Maximum message interval: {self.max_message_interval}")
        print("========================================")

    def print_help(self, *_):
        print("========== Available commands ==========")
        for command, command_function in self.commands.items():
            print(f"{command} - {command_function.get_help_text()}")
        print("========================================")

    def set_num_attr(self, attribute_name, *args):
        if not (hasattr(self, attribute_name)):
            raise NPCError(f"Given attribute '{attribute_name}' doesn't exist!")

        if not isinstance(attribute_name, str):
            raise NPCError("Given attribute name isn't a string!")

        if len(args) < 1:
            raise NPCError("You forgot to give the value!")

        user_value = args[0]    # resf of values are ignored
        if not user_value.isdigit():
            raise NPCError(f"Given argument '{user_value}' isn't a number!")

        user_value = int(user_value)
        if user_value < 1:
            raise NPCError(f"Given value '{user_value}' is invalid!")

        setattr(self, attribute_name, user_value)
        print(f"{attribute_name.upper()} set to [{getattr(self, attribute_name)}]")

    def exit(self):
        self.disconnect()
        exit()

    def run(self):
        print(f"Welcome to NPC-terminal. 'EXIT' to close, 'HELP' for list of commands.")

        while True:
            try:
                # takes input, removes unnecessary whitespaces, splits
                user_input = input("> ").strip().split()

                # skips empty lines
                if len(user_input) < 1:
                    continue

                user_command = user_input[0].upper()
                user_arguments = user_input[1:]

                # looks for command name and executes if found
                if user_command in self.commands:
                    command = self.commands.get(user_command)
                    command.execute(*user_arguments)
                else:
                    print(f"Didn't find any commands named '{user_command}'!")

            except NPCError as error:
                print(error)
            
            except TwitchConnectionError as error:
                print(error)

            except Exception as error:
                print(f"Unexpected error: {error}")


class NPCCommand:
    def __init__(self, function, help_text):
        self.function = function
        self.help_text = help_text

    def execute(self, *args):
        return self.function(*args)

    def get_help_text(self):
        return self.help_text


class NPCError(Exception):
    pass
