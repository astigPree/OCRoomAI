from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')

from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput

from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.lang.builder import Builder
from kivy.core.text import LabelBase
from kivy.clock import Clock

from threading import Thread
import os, pickle, json , typing

from content_screens import GuestScreen, FacultyScreen, DeveloperScreen


class LogInView(ModalView):
    duration = 10 # Duration of login

    username: TextInput = ObjectProperty()
    password: TextInput = ObjectProperty()
    timer : int = NumericProperty(duration)

    command : callable = ObjectProperty()
    main_event : Clock = None

    def startTimer(self , *args):
        if self.timer <= 0:
            self.dismiss()
            return

        self.timer -= 1
        self.main_event = Clock.schedule_once(self.startTimer , 1)

    def on_dismiss(self):
        self.timer = self.duration
        Clock.unschedule(self.main_event)

    def on_open(self):
        self.main_event = Clock.schedule_once(self.startTimer , 1)


class ContentWindow(ScreenManager) :
    listOfScreen = { 'guest' : GuestScreen , 'faculty' : FacultyScreen , 'dev' : DeveloperScreen}

    def on_parent(self, *args) :
        screen = self.listOfScreen['faculty']()
        self.switch_to(screen)

    def switchScreenByName(self, name : str):
        current_screen = self.current_screen
        self.switch_to(self.listOfScreen[name]())
        self.remove_widget(current_screen)


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
    __commands_metadata : dict = ObjectProperty(None)

    __current_command : str = StringProperty("") # Used to control the manage the whole system

    __room_filename= ( "locations_data.json", "locations_informations")
    __instructor_filename = ("instructors_data.json", "locations_informations")

    from backend.algo_recognation import recognizeAlgo , whatScreen

    def __init__(self , **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.login = LogInView()
        self.login.command = self.changeScreen

    @property
    def room_filename(self) -> tuple[str , str]:
        return self.__room_filename

    @property
    def instructor_filename(self) -> tuple[str, str]:
        return self.__instructor_filename

    @staticmethod
    def loadNeededData( filename: str, folder=None, isBytes=False) -> dict :
        filepath = os.path.join(os.path.dirname(__file__), folder, filename) if folder else os.path.join(
            os.path.dirname(__file__), filename)
        with open(filepath, 'rb' if isBytes else 'r') as file :
            return json.load(file) if not isBytes else pickle.load(file)

    @staticmethod
    def saveNewData( filename : str, data : dict, folder = None , isBytes = False):
        filepath = os.path.join(os.path.dirname(__file__), folder, filename) if folder else os.path.join(
            os.path.dirname(__file__), filename)
        with open(filepath, 'wb' if isBytes else 'w') as file :
            return json.dump(data, file) if not isBytes else pickle.dump(data, file)

    def loadScreenData(self) :
        # TODO: Load the teachers and rooms data
        self.__instructor_data = self.loadNeededData(filename=self.__instructor_filename[0], folder=self.__instructor_filename[1])
        self.__room_data = self.loadNeededData(filename=self.__room_filename[0], folder=self.__room_filename[1])
        self.__commands_pattern = self.loadNeededData(filename="command_keywords.json")
        self.__commands_metadata = self.loadNeededData(filename="commands_metadata.json")

    def on_kv_post(self, base_widget):
        print(f"The String does not value {not self.__current_command}")
        self.ids['picture'].ids['picture'].source = os.path.join(os.path.dirname(__file__), 'pictures', 'building.jpg')

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

    def changeScreen(self, username : str , password : str):
        """Use to change screen with login modal view """
        screen = self.whatScreen(username , password)

        if not screen:
            self.login.timer = 0
            return

        self.content.switchScreenByName(screen)
        self.login.dismiss()

    # ---------------------- WRITING DATA ------------------------------
    def updateNewCommand(self, command : str):
        self.__current_command = command

    def updateAIText(self, text : str):
        self.__ai_talking = text

    def doneTalking(self , for_guest : bool):
        if for_guest:
            self.content.get_screen("guest").okeyToChangeScreen()

    # ---------------------- READING DATA ------------------------------
    @property
    def COMMAND(self) -> str:
        return self.__current_command

    def hasData(self) -> bool:
        if self.__room_data and self.__instructor_data:
            return True
        return False

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

    def hasCommandInBackEnd(self , command) -> dict:
        return self.__commands_metadata.get(command , {'isBackend' : False})


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
    try :
        RoomAIApp().run()
    except Exception as e:
        print(f"Main Error : {e.with_traceback(Exception)}")
