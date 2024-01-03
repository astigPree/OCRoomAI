import re, pickle, random, datetime, json, os


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
    # TODO: Load All The Information of Locations
    room_info = self.getRoomData()
    teacher_info = self.getInstructorData()

    teachers_locations = [
        "{name} office is situated on the second floor of the red building.",
        "Visit the second floor of the red building to find the office of {name}",
        "The red building's second floor is where {name} office is located.",
        "Looking for {name}? You can find the office on the second floor of the red building.",
        "To meet with {name}, head to the second floor of the red building where the office is.",
        "{name} office is on the second floor of the red building."
    ]

    # TODO: Load All Patterns
    rooms_patterns = loadNeededData('rooms_pattern.json', 'wise_data')
    persons_patterns = loadNeededData('instructors_patterns.json', 'wise_data')

    # return  # TODO: Debugging Only For UI

    # TODO: Load all the needed data and information
    COMMANDS_PATTERNS = self.getCommandPattern()
    COMMAND = "" # Empty Command

    from .recognizer import AIMouth, AIEar
    ear = AIEar()
    mouth = AIMouth()


    # TODO: Load The Model
    tags = {1 : "wheres", 0 : "invalid"}
    model = loadNeededData('model.pkl', isBytes=True)

    # TODO: create filename for incoming new training data
    file = f"new_data {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"
    file2 = f"new_data response {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"

    print("Start Main Activity".center(40, "-"))
    while not self.stop_all_running :  # Main Loop
        self.activity.text = "LISTENING"

        # TODO: Capture the voice
        text = ear.captureVoice(language='filipino')
        # text = ear.captureVoiceContinues()

        # TODO:  Check if the text is not error
        if not text :
            continue

        # TODO: Check if the text is a COMMAND
        NEW_COMMAND = "" # Empty New Command
        for command_key in COMMANDS_PATTERNS:
            for command_text in COMMANDS_PATTERNS[command_key]:
                if command_text == text:
                    NEW_COMMAND = command_key
            if NEW_COMMAND:
                break

        # TODO: Check if there is an existing COMMAND from user if the new COMMAND contradict the past command, remove the past command
        if COMMAND and NEW_COMMAND:
            pass

        # TODO:  Check if what the text means using machine learning
        predicted = model.predict([text])
        if predicted[0] == 1 :

            person_found = []
            # TODO:  Check if the finding in the text
            for location, pattern in persons_patterns.items() :
                if re.findall(rf"{pattern}", text) :
                    person_found.append(location)

            room_found = []
            for location, pattern in rooms_patterns.items() :
                if re.findall(rf"{pattern}", text) :
                    room_found.append(location)

            if person_found :
                for location in person_found :
                    # TODO: tell the current location of instructor based on the where instructor time in
                    speech = random.choice(teachers_locations).format(
                        name=random.choice(teacher_info[location]["person"]))
                    self.activity.text = "TALKING"
                    mouth.talk(speech)
                    mouth.talk("Do you want to know what is this building? say yes")
                    self.activity.text = "LISTENING"
                    asked = ear.captureVoice(3)
                    if asked :
                        choice = "no"
                        if "yes" in asked or "opo" in asked or "sige" in asked :
                            self.activity.text = "TALKING"
                            mouth.talk(room_info['office'][1])
                            choice = "yes"
                        saveText(file2, choice, asked, header=('choice', 'response'))

            if room_found :
                for location in room_found :
                    self.activity.text = "TALKING"
                    self.updateAITalking(room_info[location]["directions"][0], room_info[location]["directions"][1])
                    mouth.talk(room_info[location]["directions"][0])
                    mouth.talk("Do you want to know what is this building? say yes")
                    self.activity.text = "LISTENING"
                    asked = ear.captureVoice(3)
                    if asked :
                        choice = "no"
                        if "yes" in asked or "opo" in asked or "sige" in asked :
                            self.activity.text = "TALKING"
                            self.updateAITalking(room_info[location]["brief information"][0],
                                                 room_info[location]["brief information"][1])
                            mouth.talk(room_info[location]["brief information"][0])
                            choice = "yes"
                        saveText(file2, choice, asked, header=('choice', 'response'))

            if not room_found and not person_found :
                self.activity.text = "TALKING"
                mouth.talk(
                    "You are talking about the location in the building or a instructor but I cant understand clearly please repeat it")

            intent = "wheres"

        else :
            # TODO: tell the user can't understand what user talking
            self.activity.text = "TALKING"
            self.updateAITalking(
                "My functions only guiding the location in this building, I cant cope what are you talking.", 4)
            mouth.talk("My functions only guiding the location in this building, I cant cope what are you talking")
            intent = "invalid"

        saveText(file, intent, text)
