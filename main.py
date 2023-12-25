class NPCChatter:
    def __init__(self):
        self.commands = {
            "WC": NPCCommand(self.set_same_word_count, "how many times a word has to appear in a row to type the same"),
            "EXIT": NPCCommand(self.exit, "closes the NPCChatter"),
            "HELP": NPCCommand(self.print_help, "lists all of the commands with help texts")
        }
        self.same_word_count = 3

    def set_same_word_count(self, *args):
        if len(args) < 1:
            raise NPCError("You forgot to give the count!")

        if not args[0].isdigit():
            raise NPCError("The given argument isn't a number!")

        self.same_word_count = int(args[0])
        print(f"Same word count set to [ {self.same_word_count} ]")

    def print_help(self, *_):
        print("========== Available commands ==========")
        for command, command_function in self.commands.items():
            print(f"{command} - {command_function.get_help_text()}")
        print("========================================")

    @staticmethod
    def exit(*_):
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
                print(f"Error: {error}")

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


if __name__ == '__main__':
    npc = NPCChatter()
    npc.run()
