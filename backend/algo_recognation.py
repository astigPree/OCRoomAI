import os


def saveText(file, tag, text, header=('tags', 'text')) :
    folder = os.path.join(os.path.dirname(__file__), 'Training Data', file)
    if not os.path.exists(folder) :
        with open(folder, 'w') as f :
            f.write(f"{header[0]},{header[1]}\n")

    with open(folder, 'a') as f :
        f.write(f"{tag},{text}\n")


def recognizeAlgo(self: object) :
    import re, pickle, random, datetime, json

    from .recognizer import AIMouth, AIEar
    file = f"new_data {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"
    file2 = f"new_data response {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"

    ear = AIEar()
    mouth = AIMouth()

    # Load All The Information of Locations
    rooms_information_fullpath = os.path.join(os.path.dirname(__file__), 'wise_data', 'rooms_information.json')
    instructor_information_fullpath = os.path.join(os.path.dirname(__file__), 'wise_data',
                                                   'instructor_information.json')
    with open(rooms_information_fullpath, 'r') as jf :
        room_info = json.load(jf)
    with open(instructor_information_fullpath, 'r') as jf :
        teacher_info = json.load(jf)

    teachers_locations = [
        "{name} office is situated on the second floor of the red building.",
        "Visit the second floor of the red building to find the office of {name}",
        "The red building's second floor is where {name} office is located.",
        "Looking for {name}? You can find the office on the second floor of the red building.",
        "To meet with {name}, head to the second floor of the red building where the office is.",
        "{name} office is on the second floor of the red building."
    ]

    # Load All Patterns
    instructor_pattern_fullpath = os.path.join(os.path.dirname(__file__), 'wise_data', 'instructors_patterns.json')
    room_pattern_fullpath = os.path.join(os.path.dirname(__file__), 'wise_data', 'rooms_pattern.json')
    with open(instructor_pattern_fullpath, 'r') as jf :
        persons_patterns = json.load(jf)
    with open(room_pattern_fullpath, 'r') as jf :
        rooms_patterns = json.load(jf)

    # Load The Model
    tags = {1 : "wheres", 0 : "invalid"}
    model_fullpath = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_fullpath, "rb") as pf :
        model = pickle.load(pf)

    print("Start Main Activity".center(40, "-"))
    while True :  # Main Loop
        self.activity.text = "LISTENING"

        # Capture the voice
        text = ear.captureVoice(language='filipino')
        # text = ear.captureVoiceContinues()

        # Check if the text is not error
        if not text:
            continue

        # Check if what the text means using machine learning
        predicted = model.predict([text])
        if predicted[0] == 1 :

            person_found = []
            # Check if the finding in the text
            for location, pattern in persons_patterns.items() :
                if re.findall(rf"{pattern}", text) :
                    person_found.append(location)

            room_found = []
            for location, pattern in rooms_patterns.items() :
                if re.findall(rf"{pattern}", text) :
                    room_found.append(location)

            if person_found :
                for location in person_found :
                    speech = random.choice(teachers_locations).format(name=random.choice(teacher_info[location]))
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
                    mouth.talk(room_info[location][0])
                    mouth.talk("Do you want to know what is this building? say yes")
                    self.activity.text = "LISTENING"
                    asked = ear.captureVoice(3)
                    if asked :
                        choice = "no"
                        if "yes" in asked or "opo" in asked or "sige" in asked :
                            self.activity.text = "TALKING"
                            mouth.talk(room_info[location][1])
                            choice = "yes"
                        saveText(file2, choice, asked, header=('choice', 'response'))

            if not room_found and not person_found :
                self.activity.text = "TALKING"
                mouth.talk(
                    "You are talking about the location in the building or a instructor but I cant understand clearly please repeat it")

            intent = "wheres"

        else :
            self.activity.text = "TALKING"
            self.updateAITalking("My functions only guiding the location in this building, I cant cope what are you talking.", 4)
            mouth.talk("My functions only guiding the location in this building, I cant cope what are you talking")
            intent = "invalid"

        saveText(file, intent, text)
