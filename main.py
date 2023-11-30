from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock, mainthread

from threading import Thread

from activity_functions import Settings
from recognizer import AIMouth, AIEar, AIBrain, MessageAnalyzer, NewDataSaver


class RoomInformation(Label) :
    pass


class RoomsLocationsPicture(MDBoxLayout) :
    room_name: Label = ObjectProperty()
    room_picture: Image = ObjectProperty
    floor_name: Label = ObjectProperty()
    floor_picture: Image = ObjectProperty()


class Room(MDBoxLayout) :
    room_image: Image = ObjectProperty()
    room_name: Label = ObjectProperty()


class RoomSelections(ScrollView) :
    container: MDGridLayout = ObjectProperty()


# ------------------------- Screens ------------------- #
class FacultyScreen(Screen) :
    pass


class DeveloperScreen(Screen) :
    pass


class InformationScreen(Screen) :
    room_locations: RoomsLocationsPicture = ObjectProperty()


class UserScreen(Screen) :
    room_selections: RoomSelections = ObjectProperty()
    room_locations: RoomsLocationsPicture = ObjectProperty()
    room_information: RoomInformation = ObjectProperty()


# -------------------------- Main Window --------------- #

class AIEmotions(MDRelativeLayout): # NOQA
    image : Image = ObjectProperty()
    name_holder : Label = ObjectProperty()
    status : Label = ObjectProperty()

    emotions = {} # { status : [ image , image , image ] }
    emotion_index = NumericProperty(0)

    def changeEmotions(self, interval):
        if self.status.text == "":
            pass
        else:
            self.emotion_index += 1
            if self.emotion_index > 2:
                self.emotion_index = 0

            self.image.source = self.emotions[self.status.text][self.emotion_index]

    def startAnimatingEmotions(self):
        Clock.schedule_interval(self.changeEmotions , 1/5)


class AIThoughts( MDRelativeLayout) :  # NOQA
    image : Image = ObjectProperty()
    ai_input : Label = ObjectProperty()


class MainWindow(MDFloatLayout) :
    app_settings: Settings = ObjectProperty()

    mouth: AIMouth = ObjectProperty()  # Use to talk with text to speech
    ear: AIEar = ObjectProperty()  # Use to record the user speech
    brain: AIBrain = ObjectProperty()  # Use to identify the user request
    analyzer: MessageAnalyzer = ObjectProperty()  # Use to check the precision of request based on the text
    dataSaver: NewDataSaver = ObjectProperty()  # Use to save the transactions between computer and user for future activities

    manager: ScreenManager = ObjectProperty()
    screens_name = ( "user" , "info", "dev" , "faculty")

    image : AIEmotions = ObjectProperty()
    thoughts : AIThoughts = ObjectProperty()

    def on_kv_post(self, base_widget) :
        self.manager.add_widget(UserScreen(name= self.screens_name[0] ))
        self.manager.add_widget(InformationScreen(name=self.screens_name[1] ))
        self.manager.add_widget(DeveloperScreen(name = self.screens_name[2] ))
        self.manager.add_widget(FacultyScreen(name = self.screens_name[3] ))

    def loadAllNecessary(self) :
        self.app_settings = Settings()

        self.mouth = AIMouth()
        self.brain = AIBrain()
        self.ear = AIEar()
        # self.analyzer = MessageAnalyzer()
        # self.dataSaver = NewDataSaver()

    def mainActivityThread(self) :
        while True :
            pass
            # Check the current command ( screens, unactivated, activated, shutdown )
            # If command stop the continuation of the program, wait till owner permission
            # If none then continue to main activity
            # User, Faculty, Developer enter input by speech ( Microphone )
            user_input = self.ear.captureVoice(self.app_settings.getUsedLanguage())
            # Check if the input is in the built-in commands
            # If in the commands then execute it and disregard future activities

            # If not then proceed to identification if 'who' or 'where' using neural_intents models

            # If the input intent is 'where' identify the list of rooms in the input, if not provided ask again ( go back to 1 )

            # If the input intent is 'who' identify again using neural_intents models to identify the input 'who' intent
            # If the input is identified then show the information or the activity that the application identified

            # Wait for a minute before change back to main screen or wait till the User, Faculty, Developer input tru speech


class RoomAIApp(MDApp) :
    #
    # def on_start(self) :
    #     Thread(target=self.root.loadAllNecessary ).start()

    def build(self) :
        return Builder.load_file("design.kv")
    #
    # def on_stop(self):
    #     self.root.ear.closeMicrophone()


RoomAIApp().run()
