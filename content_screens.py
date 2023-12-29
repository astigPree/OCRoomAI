from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as chex

Clock.max_iteration = 30

from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty

from datetime import datetime


# ------------------------ Faculty Screens ----------------------
class AddFacultyScheduleModalViewTimeSelections(BoxLayout):
    pass


class AddFacultyScheduleModalView(ModalView):
    location_dropdown : Button = ObjectProperty()
    dropdown_list = DropDown()

    def on_kv_post(self, base_widget):
        for index in range(10) :

            btn = Button(text='Value %d' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn : self.dropdown_list.select(self.location_dropdown.text))

            # then add the button inside the dropdown
            self.dropdown_list.add_widget(btn)

        self.location_dropdown.bind(on_release=self.dropdown_list.open)
        self.dropdown_list.bind(on_select=lambda instance, x : setattr(self.location_dropdown, 'text', x))


class ChangeFacultyInfoModalView(ModalView):
    pass


class ScheduleContainer(BoxLayout):
    pass


class TeachersScreen(Screen) :
    pass


class NavigationButton(Button) :
    activity: callable = ObjectProperty(None)
    activity_colors = {"selected" : (chex("ddacae"), "black"), "unselected" : (chex("620609"), "white")}

    def command(self) :
        if self.activity :
            self.activity(self.text)


class FacultyScreen(Screen) :

    def on_kv_post(self, base_widget):
        self.view = AddFacultyScheduleModalView()

        Clock.schedule_once(lambda x : self.view.open() , 1)


# ------------------------ Guest Screens ----------------------
class LocationImageContainer(BoxLayout) :
    locationName: Label = ObjectProperty()
    locationImage: Image = ObjectProperty()


class LocationInformationContainer(BoxLayout) :
    title: Label = ObjectProperty()
    info: Label = ObjectProperty()


class LocationScreenInformation(Screen) :
    enter_animate = Animation(opacity=1, duration=0.5)
    leave_animate = Animation(opacity=0, duration=0.5)

    image1: LocationImageContainer = ObjectProperty()
    image2: LocationImageContainer = ObjectProperty()
    directions: LocationInformationContainer = ObjectProperty()
    information: LocationInformationContainer = ObjectProperty()

    __data: dict = ObjectProperty(None)
    isRoom: bool = BooleanProperty(True)
    screen_id: str = StringProperty("")

    ifNoTimeSpecifiedUseThisKey = "office"
    time_parser = datetime.strptime
    time_format = "%H:%M:%S"
    time_split_letter = "-"
    teacher_time: list[[str, datetime , datetime], ... ] = ListProperty([ ])
    # Data Structure teacher_time : [ (room, time_start , time_end ) , ]

    def on_kv_post(self, base_widget) :
        self.information.title.text = "INFORMATION"
        self.information.info.text = "    This room is an inventory room for all the un used supply"

    def on_enter(self, *args) :
        self.enter_animate.start(self)

    def on_pre_enter(self, *args) :
        self.updateOnlyTeacherScreen()

    def on_leave(self, *args) :
        self.leave_animate.start(self)

    def updateOnlyTeacherScreen(self) :
        # TODO: Update the screen if it TEACHER Screen
        current_time = datetime.now()
        if self.parent and self.screen_id and not self.isRoom :
            for name, time_start , time_end in self.teacher_time:
                if time_start.hour <= current_time.hour <= time_end.hour: # Check if the current hour in the hour range
                    if time_start.minute <= current_time.minute: # Check if the current minute in the minute range
                        # TODO: Set new location screen for teacher
                        room_data = self.parent.parent.parent.parent.getSpecificRoom(name)
                        self.image2.locationImage.source = room_data["building picture"]
                        self.image2.locationName.text = room_data["name"]
                        self.directions.info.text = room_data["directions"][0]
                        break
            else:
                # TODO: Set new location screen for teacher if no specified room
                room_data = self.parent.parent.parent.parent.getSpecificRoom(self.ifNoTimeSpecifiedUseThisKey)
                self.image2.locationImage.source = room_data["building picture"]
                self.image2.locationName.text = room_data["name"]
                self.directions.info.text = room_data["directions"][0]

    def updateScreen(self, data: dict, isRoom: bool, key: str) :
        self.__data = data
        self.isRoom = isRoom
        self.screen_id = key
        if isRoom :
            # TODO: Display the needed data for rooms
            self.image1.locationName.text = data["name"]
            self.image1.locationImage.source = data["building picture"]
            self.image2.locationName.text = data["floor"]
            self.image2.locationImage.source = data["floor picture"]
            self.information.info.text = data["brief information"][0]
            self.directions.info.text = data["directions"][0]
        else :
            # TODO: Display the needed data for teacher
            self.image1.locationName.text = data["person"]
            self.image1.locationImage.source = data["picture"]
            self.information.info.text = data["information"]
            for location, overall_time in data["locations"].items() :
                for time_in_room in overall_time :
                    time_start, time_end = time_in_room.split(self.time_split_letter)
                    time_start = self.time_parser(time_start, self.time_format)
                    time_end = self.time_parser(time_end, self.time_format)
                    self.teacher_time.append((location, time_start, time_end))
            self.updateOnlyTeacherScreen()


class GuestScreen(Screen) :
    screens_handler: ScreenManager = ObjectProperty(None)
    screens_names: list = ListProperty([])

    __okey_to_animate = True
    __changing_speed = 5

    def on_kv_post(self, base_widget) :
        pass

    def on_enter(self, *args) :
        if self.parent :
            self.parent.parent.loadGuestScreenData()

            instructor_data = self.parent.parent.getInstructorData()
            for name in instructor_data :
                self.screens_names.append(name)
                location = LocationScreenInformation(name=name)
                location.updateScreen(instructor_data[name], False, name)
                self.screens_handler.add_widget(location)

            room_data = self.parent.parent.getRoomData()
            for name in room_data :
                self.screens_names.append(name)
                location = LocationScreenInformation(name=name)
                location.updateScreen(room_data[name], True, name)
                self.screens_handler.add_widget(location)

        self.animateChangingScreens()

    def animateChangingScreens(self) :

        def animate(pos: int) :
            if self.__okey_to_animate :
                self.screens_handler.current = self.screens_names[pos]
                Clock.schedule_once(lambda x : animate(pos + 1 if pos + 1 < len(self.screens_names) else 0),
                                    self.__changing_speed)
            else :
                Clock.schedule_once(lambda x : animate(pos), 1 / 30)

        Clock.schedule_once(lambda x : animate(0), self.__changing_speed)

    def controlVariables(self, okey_to_animate=None, changing_speed=None) :
        if okey_to_animate is not None :
            self.__okey_to_animate = okey_to_animate
        if changing_speed is not None :
            self.__changing_speed = changing_speed


# ------------------------ Developer Screens ----------------------

class DeveloperScreen(Screen) :
    pass
