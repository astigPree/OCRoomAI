import re, pickle, datetime, json, os, typing

FACULTY_SCREEN_LOGIN = ( "ADMIN" , "ADMIN") # Username , Password


def whatScreen(self, username : str , password : str) -> typing.Union[None , str]:
    if username == FACULTY_SCREEN_LOGIN[0] and password == FACULTY_SCREEN_LOGIN[1]:
        return "faculty"
    else:
        return None


def saveText(file, tag, text, header=('tags', 'text')) :
    folder = os.path.join(os.path.dirname(__file__), 'Training Data', file)
    if not os.path.exists(folder) :
        with open(folder, 'w') as f :
            f.write(f"{header[0]},{header[1]}\n")

    with open(folder, 'a') as f :
        f.write(f"{tag},{text}\n")


def loadNeededData(filename: str, folder=None, isBytes=False) -> dict :
    filepath = os.path.join(os.path.dirname(__file__), folder, filename) if folder else os.path.join(
        os.path.dirname(__file__), filename)
    with open(filepath, 'rb' if isBytes else 'r') as file :
        return json.load(file) if not isBytes else pickle.load(file)


def loadMainWindowData(self) :
    # TODO: Load the teachers and rooms data
    print("Loaded")
    self.__instructor_data = loadNeededData(filename="instructors_data.json", folder="locations informations")
    self.__room_data = loadNeededData(filename="locations_data.json", folder="locations informations")


def recognizeAlgo(self: object) :

    # return  # TODO: Debugging Only For UI

    from .recognizer import AIMouth, AIEar
    ear = AIEar()
    mouth = AIMouth()

    print("[/] LOAD ALL NEEDED OBJECTS")

    # TODO: Load The Model
    model = loadNeededData('model.pkl', isBytes=True)
    print("[/] LOAD ALL NEEDED MODEL")

    # TODO: Load All Patterns
    rooms_patterns = loadNeededData('rooms_pattern.json', 'wise_data')
    persons_patterns = loadNeededData('instructors_patterns.json', 'wise_data')

    print("[/] LOAD ALL NEEDED DATA")

    # TODO: create filename for incoming new training data
    file = f"new_data {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"
    file2 = f"new_data response {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"

    # TODO: create a loop variables
    person_found = []
    room_found = []
    self.activity.text = "LISTENING"

    print("Start Main Activity".center(40, "-"))
    while not self.stop_all_running :  # Main Loop

        # TODO: Capture the voice
        if not self.cancelRecording:
            self.activity.text = "LISTENING"

        text = ear.captureVoice(language='filipino')

        if not self.cancelRecording:
            self.activity.text = "LISTENING"
            # text = ear.captureVoiceContinues()
        else:
            self.activity.text = "SILENT"

        # TODO:  Check if the text is not error
        if not text :
            continue

        # TODO: Command Handling
        # Update the command based on new text pass by new voice input
        self.command_handler.updateCommandByTextIdentifying(text , rate=80)
        command, _ = self.command_handler.getCurrentCommand()
        # Update the UI COMMAND variable
        self.updateNewCommand(command)

        # Check if the current command is change/modify after updating
        if self.command_handler.isThisCurrentCommand(self.COMMAND):
            print(f"Backend Command : {command}")
            # Check if in the built-in command
            if command == "activated":
                self.cancelRecording = False
                sentence = "Please don't hesitate to ask the location you want to go in Computer Science Building"
                self.updateAITalking(sentence, 5)
                mouth.talk(sentence)
                self.command_handler.removeCommand()
            elif command == "unactivated":
                self.cancelRecording = True
                sentence = "I will stay silent or inactive till you user speak the command of activation"
                self.updateAITalking(sentence, 5)
                mouth.talk(sentence)
            elif command == "shutdown" :
                sentence = "I do have a permission to shutdown or open, Only with keyboard interruptions"
                self.updateAITalking(sentence, 5)
                mouth.talk(sentence)
            elif command == "open" :
                sentence = "I do have a permission to shutdown or open, Only with keyboard interruptions"
                self.updateAITalking(sentence, 5)
                mouth.talk(sentence)
            else:
                pass

            continue # Use to skip the whole continues activities


        # TODO: Check if what the text means using machine learning
        predicted = model.predict([text])
        if predicted[0] == 1 :
            text = text + " " # Add Space for identifying what room it is

            # TODO:  Check if the finding in the text
            for location, pattern in persons_patterns.items() :
                if re.findall(rf"{pattern}", text) :
                    person_found.append(location)

            for location, pattern in rooms_patterns.items() :
                if re.findall(rf"{pattern}", text) :
                    room_found.append(location)

            if person_found :
                for location in person_found :
                    # TODO: tell the current location of instructor based on the where instructor time in
                    # Updating The UI
                    self.location_selected = location
                    self.activity.text = "TALKING"
                    data = self.getGuestScreenData(location)
                    self.updateAITalking(data['directions'][0] , data['directions'][1])
                    # BackEnd action
                    mouth.talk(data["directions"][0])
                    self.doneTalking(True)
                    # mouth.talk("Do you want to know what is this building? say yes")
                    # self.activity.text = "LISTENING"
                    # asked = ear.captureVoice(3)
                    # if asked :
                    #     choice = "no"
                    #     if "yes" in asked or "opo" in asked or "sige" in asked :
                    #         self.activity.text = "TALKING"
                    #         mouth.talk(room_info['office']["directions"][0])
                    #         choice = "yes"
                    #     saveText(file2, choice, asked, header=('choice', 'response'))

            if room_found :
                for location in room_found :
                    # TODO: tell the current location of instructor based on the where instructor time in
                    # Updating The UI
                    self.location_selected = location
                    self.activity.text = "TALKING"
                    data = self.getGuestScreenData(location)
                    self.updateAITalking(data['directions'][0], data['directions'][1])
                    # BackEnd action
                    mouth.talk(data["directions"][0])
                    self.doneTalking(True)
                    # mouth.talk("Do you want to know what is this building? say yes")
                    # self.activity.text = "LISTENING"
                    # asked = ear.captureVoice(3)
                    # if asked :
                    #     choice = "no"
                    #     if "yes" in asked or "opo" in asked or "sige" in asked :
                    #         self.activity.text = "TALKING"
                    #         self.updateAITalking(room_info[location]["brief information"][0],
                    #                              room_info[location]["brief information"][1])
                    #         mouth.talk(room_info[location]["brief information"][0])
                    #         choice = "yes"
                    #     saveText(file2, choice, asked, header=('choice', 'response'))

            if not room_found and not person_found :
                self.activity.text = "TALKING"
                self.updateAITalking("You are talking about the location in the building or a instructor but I cant understand clearly please repeat it", 7)
                mouth.talk(
                    "You are talking about the location in the building or a instructor but I cant understand clearly please repeat it")
                self.doneTalking(True)

            person_found.clear()
            room_found.clear()
            intent = "wheres"

        else :
            # TODO: tell the user can't understand what user talking
            self.activity.text = "TALKING"
            self.updateAITalking(
                "My functions only guiding the location in this building, I cant cope what are you talking.", 4)
            mouth.talk("My functions only guiding the location in this building, I cant cope what are you talking")
            self.doneTalking(True)
            intent = "invalid"

        saveText(file, intent, text)
