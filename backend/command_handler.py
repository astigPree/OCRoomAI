"""
    This is where the logic of command happen
"""
import typing
from fuzzywuzzy import fuzz

class CommandHandler:

    __commands : dict = None
    __commands_info : dict = None

    __current_command : typing.Union[str , None] = None
    __current_command_info : typing.Union[dict , None] = None

    def updateCommand(self, commands : dict, metadata : dict):
        self.__commands = {}
        for key in commands:
            self.__commands[key] = []
            for pattern in commands[key]:
                self.__commands[key].append(pattern.replace(" ", ""))

        self.__commands_info = metadata

    # ------------- WRITING COMMAND ----------------
    def removeCommand(self) -> typing.NoReturn:
        if self.__current_command or self.__current_command_info:
            self.__current_command = None
            self.__current_command_info = None

    def updateCommandByTextIdentifying(self, text : str , rate  = 90 ) -> typing.NoReturn:
        """ Identify the text without spacing with the patterns and check the relationship"""
        no_space_text = text.replace(" ","")
        related_commands = {} # { 'command' : ratio }
        for key in self.__commands:
            for pattern in self.__commands[key]:
                ratio = fuzz.partial_ratio(pattern , no_space_text)
                if ratio > rate:
                    related_commands[key] = ratio if related_commands[key] < ratio else related_commands[key]

        if not related_commands:
            return

        self.__current_command = max(related_commands, key = related_commands.keys())
        self.__current_command_info = self.__commands_info[self.__current_command]

    # ------------- READING COMMAND ----------------
    def getCurrentCommand(self) -> typing.Union[ tuple[None , None] , tuple[str , dict]]:
        if self.__current_command or self.__current_command_info:
            return None , None
        return self.__current_command , self.__current_command_info

    def isCurrentCommandIsBackend(self) -> bool:
        if self.__current_command_info:
            return self.__current_command_info.get("isBackend")
        return False

    def isThisCurrentCommand(self , command : str ) -> bool:
        if self.__current_command == command:
            return True
        return False


if __name__ == "__main__":
    pass