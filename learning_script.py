"""
    This script is used to make a console artificial intelligence
    Just to be used as a learning way for incoming booth
"""
import json
import os


def txtToCsv():
    os.chdir('Training Data')
    datas = []
    for file in os.listdir(os.getcwd()):
        if file.startswith('new_data') and file.endswith('.txt'):
            datas.append(file)

    for file in datas:
        os.rename(file, f"{file[:-4]}.csv")


def dataMaker(file) :
    import os
    from recognizer import AIEar

    folder = "Training Data"
    filename = os.path.join(folder, file)
    rec = AIEar()
    print("starting ............ ")
    print("Click Enter to save \nClick 'n' to stop \nClick any letter to pass ")
    while True :
        print("Recording ...")
        text = rec.captureVoice(language='filipino')
        if not text or text == "<unk>" :
            continue
        if "<unk>" in text :
            text = text.replace("<unk>", "")
        print(f"Result : \" {text} \" ")

        act = input(f"Save to {file}? ")
        if act == "" :
            if not os.path.exists(filename) :
                with open(filename, 'w') as f :
                    f.write(f"\"{text}\",\n")
            else :
                with open(filename, 'a') as f :
                    f.write(f"\"{text}\",\n")
        elif act == "n" :
            break
        else :
            pass

    rec.closeMicrophone()


def learningMethod():
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    import pandas as pd
    import pickle

    allTable = pd.read_csv("Training Data/past_data.csv")
    # allTable = pd.concat([wheresTable, invalidTable] , axis="rows" ) # use to add all the data

    allTable["wheres"] = allTable["tags"].apply(lambda x : 1 if x == "wheres" else 0)

    # X_train , X_test , y_train, y_test = train_test_split(allTable.text , allTable.wheres, test_size=0.2)

    # Training a model and turning it to number
    model = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('nb', MultinomialNB())
    ])
    model.fit(allTable.text.values , allTable.wheres.values)
    # y_pred = model.predict(X_test)
    # print(classification_report(y_test, y_pred))

    print("Predicting")
    pred = model.predict(["good morning po sa inyu"])
    print(pred)

    verify = input("Do you want to save it?")
    if verify == "y":
        with open("new_model.pkl", 'wb') as pf:
            pickle.dump(model , pf)


def saveText(file, tag, text, header=('tags', 'text')):
    folder = 'Training Data'
    if not os.path.exists(os.path.join(folder, file)) :
        with open(os.path.join(folder, file) , 'w' ) as f:
            f.write(f"{header[0]},{header[1]}\n")

    with open(os.path.join(folder, file) , 'a' ) as f:
        f.write(f"{tag},{text}\n")


def main() :
    import re , pickle, random , datetime
    # import spacy
    # import calamancy
    # from nltk import word_tokenize

    from recognizer import AIMouth, AIEar
    file = f"new_data {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"
    file2 = f"new_data response {datetime.datetime.now().strftime('%m-%d-%Y')}.csv"

    ear = AIEar()
    mouth = AIMouth()

    # Load All The Information of Locations
    with open('wise_data/rooms_informations.json' , 'r') as jf:
        room_info = json.load(jf)
    with open('wise_data/instructor_information.json' , 'r') as jf:
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
    with open('wise_data/instructors_patterns.json', 'r' ) as jf:
        persons_patterns = json.load(jf)
    with open('wise_data/rooms_pattern.json' , 'r') as jf:
        rooms_patterns = json.load(jf)

    # Load The Model
    tags = { 1 : "wheres" , 0 : "invalid"}
    with open("model.pkl" , "rb") as pf:
        model = pickle.load(pf)

    print("Start Main Activity".center(40, "-"))
    while True :  # Main Loop

        # Capture the voice
        text = ear.captureVoice(language='filipino')
        # text = ear.captureVoiceContinues()

        # Check if the text is not error
        if not text or text == "<unk>" :
            continue

        # Check if  '<unk>' in the text and remove it
        if "<unk>" in text :
            text = text.replace("<unk>", "")

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
                    speech = random.choice(teachers_locations).format(name =random.choice(teacher_info[location]))
                    mouth.talk(speech)
                    mouth.talk("Do you want to know what is this building? say yes")
                    asked = ear.captureVoice(3)
                    if asked:
                        choice = "no"
                        if "yes" in asked :
                            mouth.talk(room_info['office'][1])
                            choice = "yes"
                        saveText(file2, choice, asked, header=('choice', 'response'))

            if room_found :
                for location in room_found:
                    mouth.talk(room_info[location][0])
                    mouth.talk("Do you want to know what is this building? say yes")
                    asked = ear.captureVoice(3)
                    if asked:
                        choice = "no"
                        if "yes" in asked:
                            mouth.talk(room_info[location][1])
                            choice = "yes"
                        saveText(file2, choice, asked, header=('choice', 'response'))


            if not room_found and not person_found:
                mouth.talk(
                "You are talking about the location in the building or a instructor but I cant understand clearly please repeat it")

            intent = "wheres"

        else :
            mouth.talk("My functions only guiding the location in this bulding, I cant cope what are you talking")
            intent = "invalid"

        saveText(file, intent , text)



if __name__ == "__main__" :
    main()
    # dataMaker('idontknow.txt')
    # learningMethod()
    # txtToCsv()



