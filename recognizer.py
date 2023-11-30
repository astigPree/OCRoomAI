import os
import threading
import typing as tp
import json


class NewDataSaver :
    """
        This class use to save data to 'New Datas' folder and the file is named '[name of category] new datas.txt'
        The file created are container of all new data saved to use for future training
    """

    def __init__(self) :
        self.folder = "New Datas"
        self.datas = {}

        os.makedirs(self.folder, exist_ok=True)

    @staticmethod
    def write(filename: str, act: str, value: str) :
        with open(filename, act) as f :
            f.write(value + '\n')

    def add_new_data(self, key: str, value: str) :
        filename = os.path.join(self.folder, f"{key} new datas.txt")

        def save_with_thread() :
            if os.path.exists(filename) :
                self.write(filename, 'a', value)
            else :
                self.write(filename, 'w', value)

        threading.Thread(target=save_with_thread).start()


class MessageAnalyzer :
    """
        This class hold the keywords of all words to make easier handling and text manipulations
    """
    __keywords = {}
    filename = 'keywords.json'

    def __init__(self) :
        from nltk import word_tokenize, stem
        from fuzzywuzzy import process, fuzz

        self.stemmer = stem.PorterStemmer()
        self.process = process
        self.scorer = fuzz.partial_ratio
        self.word_tokenizer = word_tokenize

        # with open(self.filename, 'r') as jf :
        #     self.__keywords = json.load(jf)

    def getKeywords(self, key: str) :
        return self.__keywords[key]

    def getRateOfText(self, key: str, words: str) :
        """Get the highest and closest keywords"""
        return self.process.extractOne(words, self.__keywords[key], scorer=self.scorer)

    def stemTheWords(self, words: list[str, ...]) -> list[str, ...] :
        """Return a list of root form of each word in list; Ex: jumps -> jump """
        return [self.stemmer.stem(word) for word in words]

    def splitTextToListOfWord(self, text: str) -> list[str, ...] :
        """Split the Text to list of word"""
        return self.word_tokenizer(text)

    def removeSpecificWord(self, word: str, sentence: str, rate=70, stemmed=True) -> str :
        """Remove a word in the sentence and reconstruct it again """
        if stemmed :
            new_sentence = self.stemTheWords(self.word_tokenizer(sentence))
        else :
            new_sentence = self.word_tokenizer(sentence)
        return " ".join([accepted_word for accepted_word in new_sentence if self.scorer(word, accepted_word) < rate])

    @staticmethod
    def listOfWordToText(words: list[str, ...], sep=" ") -> str :
        return sep.join(words)


class AIMouth :
    """ This where the A.I. Speak """

    import pyttsx3
    __speaker = pyttsx3.init()
    male_voice = None
    female_voice = None

    def __init__(self, rate=None, volume=1.0, gender='male') :
        self.male_voice = self.__speaker.getProperty('voices')[0].id
        self.female_voice = self.__speaker.getProperty('voices')[1].id

        if rate :
            self.__speaker.setProperty('rate', rate)
        self.__speaker.setProperty('volume', volume)
        if gender == 'male' :
            self.__speaker.setProperty('voice', self.male_voice)
        else :
            self.__speaker.setProperty('voice', self.female_voice)

    # -----> Speaker Activities
    def talk(self, sentence: str) :
        print(f'Speaking : {sentence}')
        self.__speaker.say(sentence)
        self.__speaker.runAndWait()

    # -----> Configure Speaker
    def changeVoiceToFemale(self) :
        self.__speaker.setProperty('voice', self.female_voice)

    def changeVoiceToMale(self) :
        self.__speaker.setProperty('voice', self.male_voice)

    def changeTalkingSpeed(self, rate: int) :
        self.__speaker.setProperty('rate', rate)

    def changeVolume(self, volume: float) :
        self.__speaker.setProperty('volume', volume)


class AIEar :
    """ This where the A.I. Listen """

    KHZT = 16_000  # 16_000 'If increasing the buffer size doesn't resolve the issue, you can try reducing the sample rate (sampling frequency) when opening the audio stream. Lowering the sample rate decreases the amount of data captured per second, which can help prevent input overflow.'
    frames_per_buffer = 8_192  # 8192 'One way to mitigate input overflow issues is to increase the size of the input buffer (frames_per_buffer) when opening the audio stream. A larger buffer can handle more audio data and reduce the chances of overflow. For example, you can set frames_per_buffer to a larger value, such as 8192 or 16384.'
    stream_read = int(frames_per_buffer / 2)
    channel = 1

    isListening = False
    isTalking = False
    maximumRecordLoop = 50

    def __init__(self) :
        from vosk import Model, KaldiRecognizer
        from pyaudio import paInt16, PyAudio

        self.english_model = Model(model_name="vosk-model-small-en-us-0.15")
        self.fil_model = Model(model_name="vosk-model-tl-ph-generic-0.6")
        # self.english_model = Model(r"C:\Users\63948\Desktop\PyProg\OC Room AI\EarModel\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")
        # self.fil_model = Model(r"C:\Users\63948\Desktop\PyProg\OC Room AI\EarModel\vosk-model-tl-ph-generic-0.6\vosk-model-tl-ph-generic-0.6")

        self.english_recognizer = KaldiRecognizer(self.english_model, self.KHZT)
        self.fil_recognizer = KaldiRecognizer(self.fil_model, self.KHZT)

        self.mic = PyAudio()
        self.stream = self.mic.open(format=paInt16, rate=16000, channels=self.channel, input=True,
                                    frames_per_buffer=self.frames_per_buffer)

    def closeMicrophone(self) :
        if self.stream and self.mic :
            self.stream.close()
            self.mic.terminate()

    def updateKHZT(self, value: int) :
        self.KHZT = int

    def updateFrameBuffer(self, frames_per_buffer) :
        self.frames_per_buffer = frames_per_buffer
        self.stream_read = int(self.frames_per_buffer / 2)

    def updateChannel(self, value: int) :
        self.channel = value

    def captureVoice(self, language='english', waiting_time=None) -> tp.Union[str, None] :
        """This functions might return empty string and to not get stuck it has a maximum loop to read stream"""
        self.isListening = True
        self.stream.start_stream()
        text = ""

        for _ in range(self.maximumRecordLoop if not waiting_time else waiting_time) :
            data = self.stream.read(num_frames=self.stream_read, exception_on_overflow=False)
            if language == "english" :
                if self.english_recognizer.AcceptWaveform(data) :
                    text = self.english_recognizer.Result()[14 :-3]
                    print(f"English Text : {text}")
                    if len(text) : break
            else :
                if self.fil_recognizer.AcceptWaveform(data) :
                    text = self.fil_recognizer.Result()[14 :-3]
                    print(f"Filipino Text : {text}")
                    if len(text) : break

        if len(text) :
            self.stream.stop_stream()
            self.isListening = False
            return text
        else :
            print("[!] OSError: [Errno -9981] Input overflowed")
            self.stream.stop_stream()
            self.isListening = False
            return None

    def captureVoiceContinues(self, language="filipino", key="@#$") -> tuple[str, bool] :
        # A function that has loop of recording until there is no sound
        # Return sentences and boolean if key is in the sentences
        self.isListening = True
        self.stream.start_stream()

        past_text = ""
        keep_recording = True

        if language == "english" :
            while keep_recording :
                data = self.stream.read(num_frames=self.stream_read, exception_on_overflow=False)
                if self.english_recognizer.AcceptWaveform(data) :
                    current_text = self.english_recognizer.Result()[14 :-3]

                    if not past_text :  # Check if past_text is empty then set a current_text
                        past_text = current_text

                    if past_text in current_text :
                        past_text = current_text
                    else :
                        keep_recording = False

        else :
            while keep_recording :
                data = self.stream.read(num_frames=self.stream_read, exception_on_overflow=False)
                if self.fil_recognizer.AcceptWaveform(data) :
                    current_text = self.fil_recognizer.Result()[14 :-3]
                    print(f"Present Text : {current_text}")

                    if not past_text :  # Check if past_text is empty then set a current_text
                        past_text = current_text

                    if past_text in current_text :  # Check if past_text in current_text
                        past_text = current_text
                    else :
                        keep_recording = False

                    print(f"Past Text : {past_text}")

        self.stream.stop_stream()
        self.isListening = False

        return (past_text, True) if key in past_text else (past_text, bool)


class AIBrain :
    """ This is where the classification of text occur """

    __decision = None
    folder = "AI Model"
    model = ""

    def create_brain(self, model: str, file_json: str, functions: dict) :
        from neuralintents import GenericAssistant
        self.model = model
        # if you want to have return value in decide method , put empty dictionary in functions parameter
        model_name = os.path.join(self.folder, self.model)  # Directory , Model
        self.__decision = GenericAssistant(file_json, intent_methods=functions, model_name=model_name)
        if os.path.exists(f"{model_name}.h5") :
            self.__decision.load_model(model_name)
        else :
            self.__decision.train_model()
            self.__decision.save_model(model_name)

    def decide(self, message: str) -> str :
        return self.__decision.request(message)


if __name__ == "__main__" :
    # pass
    rec = AIEar()
    mouth = AIMouth()
    print("starting ............ ")
    text = rec.captureVoice(language='filipino')
    print(f"Result :{text}")
    mouth.talk(text)
    rec.closeMicrophone()
    text = "gwapo mo talaga pre ways"
    #
    # mes = MessageAnalyzer()
    # me2 = MessageAnalyzer()
    # # with open("wise_data/command_keywords.json", 'r') as jf:
    # #     data = json.load(jf)
    #
    # a = mes.removeSpecificWord("wise", text, stemmed=False)
    # print(a)

    # mes = MessageAnalyzer()
    # words = [
    #     "Switch screens",
    #     "Replace the screen",
    #     "Change the display",
    #     "Swap the screen",
    #     "Alternate screens",
    #     "palit screen",
    # ]
    # for word in words:
    #     tok = mes.splitTextToListOfWord(word)
    #     stem = mes.stemTheWords(tok)
    #     print(f"\"{' '.join(stem)}\",")
    #     # print(f"Tokenized : {tok}")
    #     # print(f"Stemmed : {stem}")
