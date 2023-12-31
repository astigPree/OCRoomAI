# from kivy.config import Config
# Config.set('graphics', 'fullscreen', 'auto')

from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.lang.builder import Builder
from kivy.core.text import LabelBase
from kivy.clock import Clock

from threading import Thread
import os, pickle, json , typing

from content_screens import GuestScreen, FacultyScreen, DeveloperScreen


class ContentWindow(ScreenManager) :
    listOfScreen = ('guest', 'faculty', 'developer')

    def on_kv_post(self, base_widget) :
        self.add_widget(GuestScreen(name=self.listOfScreen[0]))
        # self.add_widget(FacultyScreen(name=self.listOfScreen[1]))
        # self.add_widget(DeveloperScreen(name=self.listOfScreen[2]))


class MainWindow(FloatLayout) :
    display_talking_scroller : ScrollView = ObjectProperty(None)
    display_talking: Label = ObjectProperty(None)
    content: ContentWindow = ObjectProperty(None)
    activity : Label = ObjectProperty(None)

    size_effect = NumericProperty(5.0)
    stop_all_running = BooleanProperty(False)
    __ai_talking: str = StringProperty("This is a test of the UI Display asjdf sdfjo jsdf jsdafj sadjo joojds oj dsf")

    location_selected : str = StringProperty("") # Used to be connection to algo_recognation when changing screen

    __instructor_data : dict = ObjectProperty(None)
    __room_data : dict = ObjectProperty(None)
    __commands_pattern : dict = ObjectProperty(None)

    from backend.algo_recognation import recognizeAlgo

    @staticmethod
    def loadNeededData( filename: str, folder=None, isBytes=False) -> dict :
        filepath = os.path.join(os.path.dirname(__file__), folder, filename) if folder else os.path.join(
            os.path.dirname(__file__), filename)
        with open(filepath, 'rb' if isBytes else 'r') as file :
            return json.load(file) if not isBytes else pickle.load(file)

    def loadGuestScreenData(self) :
        # TODO: Load the teachers and rooms data
        self.__instructor_data = self.loadNeededData(filename="instructors_data.json", folder="locations_informations")
        self.__room_data = self.loadNeededData(filename="locations_data.json", folder="locations_informations")
        self.__commands_pattern = self.loadNeededData(filename="command_keywords.json")

    def on_kv_post(self, base_widget):
        self.ids['picture'].ids['picture'].source = os.path.join(os.path.dirname(__file__), 'pictures', 'building.jpg')
        print("Happen ------------------------------------------------")

        Clock.schedule_interval(self.updateScrolling , 1/30)

    def close(self):
        self.stop_all_running = True

    def updateScrolling(self, interval : int):
        if self.display_talking_scroller.children[0].height > self.display_talking_scroller.height:
            self.display_talking_scroller.scroll_y = 0
        else:
            self.display_talking_scroller.scroll_y = 1

    def animateDisplayTalking(self, talking_time: int) :
        def Animate(speed: float) :
            if not len(self.__ai_talking) :
                return None

            self.display_talking.text = self.display_talking.text + self.__ai_talking[0]
            self.__ai_talking = self.__ai_talking[1 :]

            Clock.schedule_once(lambda x : Animate(speed), speed)

        speed = talking_time / len(self.__ai_talking)
        Clock.schedule_once(lambda x : Animate(speed), speed)

    def updateAITalking(self, text : str , talking_speed : int):
        # TODO: before changing the ai_talking , check if the AI is done talking by checking if the ai_talking is empty string
        self.display_talking.text = ""
        self.__ai_talking = text
        Clock.schedule_once(lambda x : self.animateDisplayTalking(int(talking_speed)))

    # ---------------------- WRITING DATA ------------------------------
    def updateAIText(self, text : str):
        self.__ai_talking = text

    def doneTalking(self , for_guest : bool):
        if for_guest:
            self.content.get_screen("guest").okeyToChangeScreen()

    # ---------------------- READING DATA ------------------------------
    def getInstructorData(self) -> dict:
        return self.__instructor_data

    def getRoomData(self) -> dict :
        return self.__room_data

    def getCommandPattern(self) -> dict:
        return self.__commands_pattern

    def getSpecificRoom(self, key : str) -> typing.Union[dict , None]:
        for room in self.__room_data:
            if room == key:
                return self.__room_data[key]
        return None

    def getGuestScreenData(self, name : str):
        return self.content.current_screen.screens_handler.get_screen(name).getScreenInformation()


class RoomAIApp(MDApp) :

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('oc ai.profile')
        self.root.close()

    def on_start(self):
        import cProfile
        self.profile = cProfile.Profile()
        self.profile.enable()


        Thread(target=self.root.recognizeAlgo).start()

    def build(self) :
        Builder.load_file("screens_content_design.kv")
        return Builder.load_file("design.kv")


if __name__ == "__main__" :
    LabelBase.register(name="ai_font", fn_regular="fonts/OpenSans-Semibold.ttf")
    LabelBase.register(name="title_font" , fn_regular="fonts/OpenSans-Bold.ttf")
    LabelBase.register(name="content_font" , fn_regular="fonts/OpenSans-Regular.ttf")
    RoomAIApp().run()
