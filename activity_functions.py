import os
import json
from typing import Union


class Settings :
    application_file = "settings.eric"
    # Mode; 0 = Processing , 1 = Listening, 2 = Talking, 3 = Behave
    __settings = {
        "action" : True,
        "language" : "filipino",
        "mode" : 0,
    }

    command_folder = "wise_data"
    command_filename = "command_keywords.json"
    commands : dict = None

    def __init__(self) :
        if os.path.exists(self.application_file) :
            with open(self.application_file, 'r') as jf :
                self.__settings = json.load(jf)
        else :
            with open(self.application_file, 'w') as jf :
                json.dump(self.__settings, jf)

        with open(os.path.join(self.command_folder, self.command_filename), 'r') as jf:
            self.commands = json.load(jf)

    def save(self):
        with open(self.application_file, 'w') as jf:
            json.dump(self.__settings , jf)

    def getUsedLanguage(self) :
        return self.__settings['language']

    def changeLanguage(self) :
        if self.__settings['language'] == "filipino" :
            self.__settings['language'] = "english"
        else :
            self.__settings['language'] = "filipino"

    def getAction(self):
        return self.__settings['action']

    def deactivateAction(self):
        self.__settings['action'] = False

    def activateAction(self):
        self.__settings['action'] = True

    def mood(self):
        return self.__settings['mode']


class TextHandle :
    conjunctions = ["o", "at", "and", "or", "tapos"]

    def __init__(self) :
        from word2number import w2n
        self.converter = w2n

    def isThereANumber(self, text: str) :
        try :
            self.converter.word_to_num(text)
            return True
        except ValueError :
            return False

    def extract_numbers_from_string_to_list(self, input_str: str) -> list[int, ...] :
        # Tokenize the input string into words
        tokens = input_str.split()

        # Initialize an empty list to store the numbers
        numbers = []

        # Iterate through the tokens
        for token in tokens :
            try :
                # Try to convert the token to a number using word2number
                number = self.converter.word_to_num(token)
                numbers.append(number)
            except ValueError :
                # Ignore tokens that are not numbers
                if token in self.conjunctions:
                    numbers.append("m")

        return numbers

    def extract_numbers_from_string_directly(self, input_str : str) -> Union[None , int] :
        return self.converter.word_to_num(input_str) if self.isThereANumber(input_str) else None


if __name__ == "__main__":
    pass