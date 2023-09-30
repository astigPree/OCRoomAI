
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

    def write(self, filename: str, act: str, value: str) :
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
        from fuzzywuzzy import process

        self.stemmer = stem.PorterStemmer()
        self.process = process
        self.word_tokenizer = word_tokenize

        with open(self.filename, 'r') as jf :
            self.__keywords = json.load(jf)

    def getKeywords(self, key: str) :
        return self.__keywords[key]

    def getRateOfText(self, key: str, words: str) :
        """Get the highest and closest keywords"""
        return self.process.extractOne(words, self.__keywords[key])

    def stemTheWords(self, words: list[str, ...]) -> list[str, ...] :
        """Return a list of root form of each word in list; Ex: jumps -> jump """
        return [self.stemmer.stem(word) for word in words]

    def splitTextToListOfWord(self, text: str) -> list[str, ...] :
        """Split the Text to list of word"""
        return self.word_tokenizer(text)

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
    maximumRecordLoop = 30

    def __init__(self) :
        from vosk import Model, KaldiRecognizer
        from pyaudio import paInt16, PyAudio

        self.english_model = Model(model_name="vosk-model-small-en-us-0.15")
        self.fil_model = Model(model_name="vosk-model-tl-ph-generic-0.6")

        self.english_recognizer = KaldiRecognizer(self.english_model, self.KHZT)
        self.fil_recognizer = KaldiRecognizer(self.fil_model, self.KHZT)

        self.mic = PyAudio()
        self.stream = self.mic.open(format=paInt16, rate=self.KHZT, channels=self.channel, input=True,
                                    frames_per_buffer=self.frames_per_buffer)

    def captureVoice(self, language='english') -> tp.Union[str, None] :
        """This functions might return empty string and to not get stuck it has a maximum loop to read stream"""
        self.isListening = True
        self.stream.start_stream()

        if language == "english" :
            for _ in range(self.maximumRecordLoop) :
                data = self.stream.read(num_frames=self.stream_read, exception_on_overflow=False)
                if self.english_recognizer.AcceptWaveform(data) :
                    text = self.english_recognizer.Result()[14 :-3]
                    print(f"Text : {text}")
                    if len(text) :
                        self.stream.stop_stream()
                        self.isListening = False
                        return text
            print("[!] OSError: [Errno -9981] Input overflowed")
        else :
            for _ in range(self.maximumRecordLoop) :
                data = self.stream.read(num_frames=self.stream_read, exception_on_overflow=False)
                if self.fil_recognizer.AcceptWaveform(data) :
                    text = self.fil_recognizer.Result()[14 :-3]
                    if len(text) :
                        self.stream.stop_stream()
                        self.isListening = False
                        return text
            print("[!] OSError: [Errno -9981] Input overflowed")

        self.stream.stop_stream()
        self.isListening = False
        return None

    def closeMicrophone(self) :
        self.stream.close()
        self.mic.terminate()


class AIBrain :
    """ This is where the classification of text occur """

    __decision = None
    folder = "AI Model"
    model = ""

    def create_brain(self, file_json: str, functions: dict) :
        from neuralintents import GenericAssistant
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
    rec = AIEar()
    mouth = AIMouth()
    print("starting ............ ")
    text = rec.captureVoice(language='filipino')
    print(f"Result :{text}")
    mouth.talk(text)

    rec.closeMicrophone()
