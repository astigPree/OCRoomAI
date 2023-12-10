# from kivy.config import Config
# Config.set('graphics', 'fullscreen', 'auto')

from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label

from kivy.properties import ObjectProperty, StringProperty
from kivy.lang.builder import Builder
from kivy.core.text import LabelBase
from kivy.clock import Clock

from threading import Thread

from content_screens import GuestScreen, FacultyScreen, DeveloperScreen



class ContentWindow(ScreenManager) :
    listOfScreen = ('guest', 'faculty', 'developer')

    def on_kv_post(self, base_widget) :
        self.add_widget(GuestScreen(name=self.listOfScreen[0]))
        self.add_widget(FacultyScreen(name=self.listOfScreen[1]))
        self.add_widget(DeveloperScreen(name=self.listOfScreen[2]))


class MainWindow(FloatLayout) :
    display_talking: Label = ObjectProperty(None)
    content: ContentWindow = ObjectProperty(None)
    activity : Label = ObjectProperty(None)

    __ai_talking: str = StringProperty("This is a test of the UI Display asjdf sdfjo jsdf jsdafj sadjo joojds oj dsf")

    from backend.algo_recognation import recognizeAlgo

    def on_kv_post(self, base_widget):
        Thread(target=self.recognizeAlgo).start()

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
        self.__ai_talking = text
        Clock.schedule_once(lambda x : self.animateDisplayTalking(talking_speed))



class RoomAIApp(MDApp) :

    def build(self) :
        Builder.load_file("screens_content_design.kv")
        return Builder.load_file("design.kv")


if __name__ == "__main__" :
    LabelBase.register(name="ai_font", fn_regular="fonts/OpenSans-Semibold.ttf")
    LabelBase.register(name="title_font" , fn_regular="fonts/OpenSans-Bold.ttf")
    LabelBase.register(name="content_font" , fn_regular="fonts/OpenSans-Regular.ttf")
    RoomAIApp().run()
