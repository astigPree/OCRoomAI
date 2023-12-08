from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.animation import Animation
from kivy.clock import Clock

from kivy.properties import ObjectProperty, ListProperty

# ------------------------ Guest Screens ----------------------
class LocationImageContainer(BoxLayout):
    locationName : Label = ObjectProperty()
    locationImage : Image = ObjectProperty()


class LocationInformationContainer(BoxLayout):
    title : Label = ObjectProperty()
    info : Label = ObjectProperty()


class LocationScreenInformation(Screen) :
    enter_animate = Animation(opacity=1, duration=0.5)
    leave_animate = Animation(opacity=0, duration=0.5)

    image1 : LocationImageContainer = ObjectProperty()
    image2 : LocationImageContainer = ObjectProperty()
    directions : LocationInformationContainer = ObjectProperty()
    information : LocationInformationContainer = ObjectProperty()

    def on_kv_post(self, base_widget):
        self.image1.locationName.text = "Audio-Visual Room"
        self.information.title.text = "INFORMATION"
        self.information.info.text = "    This room is an inventory room for all the un used supply"

    def on_enter(self, *args) :
        self.enter_animate.start(self)

    def on_leave(self, *args) :
        self.leave_animate.start(self)


class GuestScreen(Screen) :
    screens_handler: ScreenManager = ObjectProperty(None)
    screens_names: list = ListProperty(['ROOM 501', 'ROOM 502', 'AVR', 'OFFICE'])

    __okey_to_animate = True
    __changing_speed = 5

    def on_kv_post(self, base_widget) :
        for name in self.screens_names :
            location = LocationScreenInformation(name=name)
            self.screens_handler.add_widget(location)

        self.animateChangingScreens()

    def animateChangingScreens(self) :
        def animate(pos: int) :
            if self.__okey_to_animate:
                self.screens_handler.current = self.screens_names[pos]
                Clock.schedule_once(lambda x : animate(pos + 1 if pos + 1 < len(self.screens_names) else 0) , self.__changing_speed)
            else:
                Clock.schedule_once(lambda x : animate(pos) , 1 / 30)

        Clock.schedule_once(lambda x : animate(0) , self.__changing_speed)

    def controlVariables(self , okey_to_animate = None, changing_speed = None):
        if okey_to_animate is not None :
            self.__okey_to_animate = okey_to_animate
        if changing_speed is not None:
            self.__changing_speed = changing_speed


# ------------------------ Faculty Screens ----------------------

class FacultyScreen(Screen) :
    pass


# ------------------------ Developer Screens ----------------------

class DeveloperScreen(Screen) :
    pass
