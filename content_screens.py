from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput

from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as chex

Clock.max_iteration = 60

from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty, DictProperty, NumericProperty

from datetime import datetime, time


# ------------------------ Faculty Screens ----------------------
class FacultyWarningActionsModalView(ModalView):
    pass


class FacultySelectionLocationDropdownContent(MDBoxLayout):
    pass


class AddFacultyScheduleModalViewTimeSelections(BoxLayout):

    start_time : time = ObjectProperty(None)
    end_time : time = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(AddFacultyScheduleModalViewTimeSelections , self).__init__(**kwargs)
        self.start_time_picker = MDTimePicker()
        self.end_time_picker = MDTimePicker()

        # Customize the input
        self.start_time_picker.bind(time=self.get_start_time)
        self.end_time_picker.bind(time=self.get_end_time)

    def get_start_time(self, _ , selected_time):
        self.start_time = selected_time

    def get_end_time(self, _ , selected_time):
        self.end_time = selected_time


class AddFacultyScheduleModalView(ModalView):
    location_dropdown : MDFillRoundFlatButton = ObjectProperty()
    dropdown_list = DropDown()

    time_selections : AddFacultyScheduleModalViewTimeSelections = ObjectProperty(None)

    time_start : str = StringProperty("Select Time")
    time_end : str = StringProperty("Select Time")
    isUsedAlready : bool = BooleanProperty(False)

    def changeLocation(self , location : str):
        self.location_dropdown.text = location
        print(location)
        self.dropdown_list.dismiss()

    def on_open(self):
        if not self.isUsedAlready:
            # TODO: Get the locations in the parents and display it in the dropdown list
            content_box = FacultySelectionLocationDropdownContent()
            for index in range(20) :
                btn = MDFillRoundFlatButton(
                    text=f"Value {index}", size_hint=(1, None),
                    height=44 , md_bg_color =  chex("620609") ,
                    font_name = "ai_font" , font_size = min(self.size) * 0.03
                )
                # btn.bind(on_release = lambda x : self.changeLocation(f"Value {index}"))
                content_box.add_widget(btn)

            self.dropdown_list.add_widget(content_box)
            # self.dropdown_list.bind(on_select=lambda instance, x : setattr(self.location_dropdown, 'text', x))

            self.isUsedAlready = True

            self.time_selections = AddFacultyScheduleModalViewTimeSelections()


class ChangeFacultyInfoModalView(ModalView):

    teacher_name : TextInput = ObjectProperty(None)
    teacher_info : TextInput = ObjectProperty(None)

    holder : object = ObjectProperty(None)

    updateInfo : callable = ObjectProperty(None)

    def on_pre_open(self):
        self.teacher_name.text = self.holder.teacher_name.text
        self.teacher_info.text = self.holder.teacher_info.text

    def updateParentInfo(self):
        self.updateInfo(self.teacher_name.text, self.teacher_info.text)
        self.dismiss()

class ScheduleContainer(BoxLayout):
    parent_index : int = NumericProperty(0)
    room : str = StringProperty('')
    schedule : str = StringProperty('')

    deleteSchedule : callable = ObjectProperty(None)

    def updateOnCreate(self , index : int , room : str ,schedule : str):
        self.parent_index = index
        self.room = room.upper()
        self.schedule = schedule


class TeachersScreen(Screen) :

    teacher_schedule: MDGridLayout = ObjectProperty(None)
    teacher_image: Image = ObjectProperty(None)
    teacher_name: Label = ObjectProperty(None)
    teacher_info: Label = ObjectProperty(None)

    teacher_data : dict = ObjectProperty(None)
    teacher_key : str = StringProperty("")

    def __init__(self, **kwargs):
        super(TeachersScreen, self).__init__(**kwargs)
        self.change_faculty_info = ChangeFacultyInfoModalView()
        self.add_schedule = AddFacultyScheduleModalView()
        self.warning = FacultyWarningActionsModalView()

        self.change_faculty_info.holder = self
        self.change_faculty_info.updateInfo = self.updateNameAndInfo
        self.add_schedule.holder = self
        self.warning.holder = self

    def updateDisplay(self, data : dict):
        # Update the display contain in schedule of each teacher
        self.teacher_info.text = data['information']
        self.teacher_image.source = data['picture']
        self.teacher_name.text = data['person']

        index = 0 # Used to identify the index in parent children
        self.teacher_schedule.clear_widgets() # Clear the display widgets
        for room in data['locations']:
            for schedule_time in data['locations'][room]:
                container = ScheduleContainer()
                container.updateOnCreate(index , room ,schedule_time)
                container.deleteSchedule = self.removeSchedule
                self.teacher_schedule.add_widget(container)
                index += 1

        # TODO: Update the schedule screen

        self.teacher_data = data

    def removeSchedule(self, index : int):
        schedule = self.teacher_schedule.children[index]
        self.teacher_data['locations'][schedule.room.lower()].remove(schedule.schedule)
        self.teacher_schedule.remove_widget(schedule)

    def updateNameAndInfo(self, name : str , info : str):
        self.teacher_info.text = info if len(info) else self.teacher_info.text
        self.teacher_name.text = name if len(name) else self.teacher_name.text

    def resetSchedule(self):
        self.teacher_data['locations'] = {}
        self.teacher_schedule.clear_widgets()


class NavigationButton(Button) :
    activity: callable = ObjectProperty(None)
    activity_colors = {
        "selected" : (chex("ddacae"), "black"),
        "unselected" : (chex("620609"), "white")
    }

    isSelected : bool = BooleanProperty(False)
    name : str = StringProperty("")

    def command(self) :
        if self.activity :
            self.activity(self.name)


class FacultyScreen(Screen) :

    navigation_buttons : MDGridLayout = ObjectProperty(None)
    navigation_screens : ScreenManager = ObjectProperty(None)

    room_data : dict = ObjectProperty()
    instructor_data : dict = ObjectProperty()

    current_screen : str = StringProperty("")
    list_of_screens : dict[str , TeachersScreen] = DictProperty({})

    def on_pre_enter(self, *args):
        if self.parent:

            if not self.parent.parent.hasData(): # Check if MainWindow hold the data already
                self.parent.parent.loadScreenData()

            self.room_data = self.parent.parent.getRoomData()
            self.instructor_data = self.parent.parent.getInstructorData()

            self.navigation_buttons.clear_widgets()
            for key , values in self.instructor_data.items():

                # Creating Navigation Button
                navBut = NavigationButton()
                navBut.text = values["person"]
                navBut.activity = self.changeScreen
                navBut.name = key
                self.navigation_buttons.add_widget(navBut)

                # Creating Navigation Screen
                screen = TeachersScreen()
                screen.updateDisplay(values)
                self.list_of_screens[key] = screen

                # Checking if has screen used
                if not self.current_screen:
                    self.changeScreen(key)

            Clock.schedule_interval(self.update , 1 /30)

    def update(self , interval : float ):
        for child in self.navigation_buttons.children:
            if child.name == self.current_screen:
                child.isSelected = True
            else:
                if child.isSelected:
                    child.isSelected = False

    def changeScreen(self, name : str):
        self.current_screen = name
        self.list_of_screens[name].updateDisplay(self.instructor_data[name])
        self.navigation_screens.switch_to(self.list_of_screens[name])
        self.update_navigation_content()

    def update_navigation_content(self):
        for nav_button in self.navigation_buttons.children:
            nav_button.text = self.instructor_data[nav_button.name]['person']

    def update_instructor_data(self, instructor : str, name = None , information = None , locations = None ):
        """
        :param instructor: the key string for data structure
        :param name: new name of the instructor
        :param information: new information of the instructor
        :param locations: new data for new locations; structure = { room : [ start time - end time, ... ] }
        :return: None
        """

        instructor_data = self.instructor_data.get(instructor , None)

        if not instructor_data:
            print(f"[!] Instructor does not exist ; {instructor_data}")
            return

        if name:
            instructor_data['person'] = name
        if information:
            instructor_data['information'] = information
        if locations:
            instructor_data['locations'] = locations

        self.instructor_data[instructor] = instructor_data
        filename , folder = self.parent.parent.instructor_filename()
        self.parent.parent.saveNewData(filename=filename , data= self.instructor_data , folder=folder)

        self.update_navigation_content()


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
        self.updateOnlyTeacherScreen()

    def on_leave(self, *args) :
        self.leave_animate.start(self)

    def getScreenInformation(self) -> dict:
        # Data Structure = { directions : ( text , int ) }
        if self.isRoom:
            return { "directions" : self.__data["directions"] }
        else :
            return {"directions" : [ "I can't find the location of the instructor" , 1]}

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


class GuestScreen(Screen) :
    screens_handler: ScreenManager = ObjectProperty(None)
    screens_names: list = ListProperty([])

    __okey_to_animate = True
    __changing_speed = 5

    def on_kv_post(self, base_widget) :
        Clock.schedule_interval(self.update_activity , 1 / 30)

    def update_activity(self, interval : float):
        if self.parent:
            if self.parent.parent.location_selected:
                self.changeScreen(self.parent.parent.location_selected)
                self.parent.parent.location_selected = ""

    def changeScreen(self, name : str):
        if name not in self.screens_names:
            raise Exception(f"Can't change screen, {name} screen does not exist")
        self.__okey_to_animate = False
        self.screens_handler.current = name

    def okeyToChangeScreen(self):
        self.__okey_to_animate = True

    def on_enter(self, *args) :
        if self.parent :
            self.parent.parent.loadScreenData()

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
