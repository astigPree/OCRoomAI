from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from recognizer import AIMouth, AIEar, AIBrain, MessageAnalyzer, NewDataSaver


class AIThoughts(Label) :  # NOQA
    pass


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


class MainWindow(MDFloatLayout) :
    mouth: AIMouth = ObjectProperty()  # Use to talk with text to speech
    ear: AIEar = ObjectProperty()  # Use to record the user speech
    brain: AIBrain = ObjectProperty()  # Use to identify the user request
    analyzer: MessageAnalyzer = ObjectProperty()  # Use to check the precision of request based on the text
    dataSaver: NewDataSaver = ObjectProperty()  # Use to save the transactions between computer and user for future activities

    ai_image: Image = ObjectProperty()
    ai_thoughts : AIThoughts = ObjectProperty()
    oc_logo: Image = ObjectProperty()
    comsie_logo: Image = ObjectProperty()  # NOQA
    room_selections : RoomSelections = ObjectProperty()
    room_locations : RoomsLocationsPicture = ObjectProperty()
    room_information : RoomInformation = ObjectProperty()

    def loadAllNecessary(self, interval: int) :
        self.mouth = AIMouth()
        self.brain = AIBrain()
        self.ear = AIEar()
        # self.analyzer = MessageAnalyzer()
        # self.dataSaver = NewDataSaver()


class RoomAIApp(MDApp) :

    def on_start(self) :
        Clock.schedule_once(self.root.loadAllNecessary)

    def build(self) :
        return Builder.load_file("design.kv")


RoomAIApp().run()
