from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as chex

from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty, DictProperty, NumericProperty
from datetime import datetime, time

Clock.max_iteration = 60


# ------------------------ Faculty Screens ----------------------
class FacultyDropDownButton(MDFillRoundFlatButton) :
    command: callable = ObjectProperty(None)

    def on_release(self) :
        self.command(self.text)


class FacultyWarningActionsModalView(ModalView) :
    isUsedToDisplay: bool = BooleanProperty(False)  # Used to check if the modal is used for displaying only or not

    text_displayer: Label = ObjectProperty(None)

    cancelText: str = StringProperty("CANCEL")

    command: callable = ObjectProperty(None)

    def displayError(self, text_error: str) :
        # TODO: Display the text_error
        self.text_displayer.text = text_error
        self.text_displayer.halign = "center"
        self.isUsedToDisplay = True
        self.cancelText = "CLOSE"
        self.open()

    def displayAddingSchedule(self, start_time: str, end_time: str, room: str, command: object) :
        self.isUsedToDisplay = False
        self.text_displayer.text = f"Do You Want to add this schedule? \nTime : {start_time} \nTime : {end_time} \nRoom : {room}"
        self.text_displayer.halign = "left"
        self.command = command
        self.open()


class FacultySelectionLocationDropdownContent(MDBoxLayout) :
    pass


class AddFacultyScheduleModalViewTimeSelections(Widget) :
    holder: BoxLayout = ObjectProperty(None)

    time_start: time = ObjectProperty(None)
    time_end: time = ObjectProperty(None)

    def __init__(self, **kwargs) :
        super(AddFacultyScheduleModalViewTimeSelections, self).__init__(**kwargs)
        self.start_time_picker = MDTimePicker(
            primary_color="brown",
            accent_color="white",
            text_button_color="white", )
        self.end_time_picker = MDTimePicker(
            primary_color="brown",
            accent_color="white",
            text_button_color="white", )

        # Customize the input
        self.start_time_picker.bind(on_save=self.get_start_time)
        self.end_time_picker.bind(on_save=self.get_end_time)

    def get_start_time(self, timer: MDTimePicker, selected_time: time) :
        self.holder.start_time = f"{int(timer.hour):02d}:{int(timer.minute):02d} {str(timer.am_pm).upper()}"
        self.time_start = selected_time

    def get_end_time(self, timer: MDTimePicker, selected_time: time) :
        self.holder.end_time = f"{int(timer.hour):02d}:{int(timer.minute):02d} {str(timer.am_pm).upper()}"
        self.time_end = selected_time

    def checkingIfCorrectSelectionOfTime(self) -> tuple[bool, str] :
        print(f"{self.time_start} >= {self.time_end}")
        if not self.time_end or not self.time_start :
            return False, "Please fill up or select the requested time"

        if self.time_start >= self.time_end :
            return False, "The starting time is greater than end time"

        return True, ""


class AddFacultyScheduleModalView(ModalView) :
    location_dropdown: MDFillRoundFlatButton = ObjectProperty()
    dropdown_list = DropDown()

    day_selection : MDFillRoundFlatButton = ObjectProperty()
    days_dropdown_list = DropDown()

    time_selections: AddFacultyScheduleModalViewTimeSelections = ObjectProperty(None)
    start_time: str = StringProperty("SELECT TIME")
    end_time: str = StringProperty("SELECT TIME")

    isUsedAlready: bool = BooleanProperty(False)

    holder: Screen = ObjectProperty(None)

    def changeLocation(self, location: str) :
        self.location_dropdown.text = location
        self.dropdown_list.dismiss()

    def changeDay(self, day : str):
        self.day_selection.text = day
        self.days_dropdown_list.dismiss()

    def updatingNewSchedule(self) :
        isCorrect, result = self.time_selections.checkingIfCorrectSelectionOfTime()

        if not isCorrect :
            self.holder.warning.displayError(result)
        elif self.location_dropdown.text == "Select Location" :
            self.holder.warning.displayError("Please specify what room you want to stay-in for the time being")
        elif self.day_selection.text == "Select Day" :
            self.holder.warning.displayError("Please specify what day you want to stay-in for the time being")
        else :
            def command():
                self.holder.addSchedule( f"{self.time_selections.time_start}-{self.time_selections.time_end}", self.location_dropdown.text)
                print("Happen")
                # self.holder.warning.command = None

            self.holder.warning.displayAddingSchedule(self.start_time, self.end_time, self.location_dropdown.text,
                                                      command)

    def closeModal(self) :
        self.start_time = "SELECT TIME"
        self.end_time = "SELECT TIME"
        self.location_dropdown.text = "Select Location"
        self.day_selection.text = "Select Day"

        self.dismiss()

    def on_open(self) :
        if not self.isUsedAlready :
            # TODO: Get the locations in the parents and display it in the dropdown list
            rooms = self.holder.parent.parent.parent.getAllRooms()  # TeachersScreen > ScreenManager > BoxLayout > FacultyScreen
            content_box = FacultySelectionLocationDropdownContent()
            for room in rooms :
                dropButton = FacultyDropDownButton(text=room)
                dropButton.command = self.changeLocation

                content_box.add_widget(dropButton)

            self.dropdown_list.add_widget(content_box)

            content_box = FacultySelectionLocationDropdownContent()
            for day in ("MONDAY" , "TUESDAY" , "WENDSDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY" ):
                dropButton = FacultyDropDownButton(text = day)
                dropButton.command = self.changeDay

                content_box.add_widget(dropButton)
            self.days_dropdown_list.add_widget(content_box)

            self.isUsedAlready = True

            self.time_selections = AddFacultyScheduleModalViewTimeSelections()
            self.time_selections.holder = self


class ChangeFacultyInfoModalView(ModalView) :
    teacher_name: TextInput = ObjectProperty(None)
    teacher_info: TextInput = ObjectProperty(None)

    holder: object = ObjectProperty(None)

    updateInfo: callable = ObjectProperty(None)

    def on_pre_open(self) :
        self.teacher_name.text = self.holder.teacher_name.text
        self.teacher_info.text = self.holder.teacher_info.text

    def updateParentInfo(self) :
        self.updateInfo(self.teacher_name.text, self.teacher_info.text)
        self.dismiss()


class ScheduleContainer(BoxLayout) :
    parent_index: int = NumericProperty(0)
    room: str = StringProperty('')
    schedule: str = StringProperty('')

    deleteSchedule: callable = ObjectProperty(None)

    json_schedule = ""

    def updateOnCreate(self, index: int, room: str, schedule: str ) :
        self.parent_index = index
        self.room = room.upper()

        schedule_1, schedule_2 = schedule.split("-")
        schedule_1 = datetime.strptime(schedule_1, "%H:%M:%S")
        schedule_1 = schedule_1.strftime("%I:%M %p")
        schedule_2 = datetime.strptime(schedule_2, "%H:%M:%S")
        schedule_2 = schedule_2.strftime("%I:%M %p")

        self.schedule = f"{schedule_1} - {schedule_2}"
        self.json_schedule = schedule


class TeachersScreen(Screen) :
    teacher_schedule: MDGridLayout = ObjectProperty(None)
    teacher_image: Image = ObjectProperty(None)
    teacher_name: Label = ObjectProperty(None)
    teacher_info: Label = ObjectProperty(None)

    teacher_data: dict = ObjectProperty(None)
    teacher_key: str = StringProperty("")

    def __init__(self, **kwargs) :
        super(TeachersScreen, self).__init__(**kwargs)
        self.change_faculty_info = ChangeFacultyInfoModalView()
        self.add_schedule = AddFacultyScheduleModalView()
        self.warning = FacultyWarningActionsModalView()

        self.change_faculty_info.holder = self
        self.change_faculty_info.updateInfo = self.updateNameAndInfo
        self.add_schedule.holder = self
        self.warning.holder = self

    def updateDisplay(self, data: dict) :
        # Update the display contain in schedule of each teacher
        self.teacher_info.text = data['information']
        self.teacher_image.source = data['picture']
        self.teacher_name.text = data['person']

        index = 0  # Used to identify the index in parent children
        self.teacher_schedule.clear_widgets()  # Clear the display widgets
        for room in data['locations'] :
            for schedule_time in data['locations'][room] :
                container = ScheduleContainer()
                container.updateOnCreate(index, room, schedule_time)
                container.deleteSchedule = self.removeSchedule
                self.teacher_schedule.add_widget(container)
                index += 1

        # TODO: Update the schedule screen

        self.teacher_data = data

    def removeSchedule(self, index: int) :
        for child in self.teacher_schedule.children:
            if child.parent_index == index:
                print(f"Schedule {child} , index : {index}")
                print(self.parent.parent.parent)
                self.teacher_data['locations'][''].remove(child.json_schedule)
                self.teacher_schedule.remove_widget(widget=child)

    def updateNameAndInfo(self, name: str, info: str) :
        self.teacher_info.text = info if len(info) else self.teacher_info.text
        self.teacher_name.text = name if len(name) else self.teacher_name.text

    def resetSchedule(self) :
        self.teacher_data['locations'] = {}
        self.teacher_schedule.clear_widgets()

    def addSchedule(self, schedule: str, room: str) :
        container = ScheduleContainer()
        container.updateOnCreate(len(self.teacher_schedule.children), self.parent.parent.parent.getKeyByRoomName(room), schedule)
        container.deleteSchedule = self.removeSchedule
        self.teacher_schedule.add_widget(container)
        self.add_schedule.closeModal()
        self.warning.dismiss()


class NavigationButton(Button) :
    activity: callable = ObjectProperty(None)
    activity_colors = {
        "selected" : (chex("ddacae"), "black"),
        "unselected" : (chex("620609"), "white")
    }

    isSelected: bool = BooleanProperty(False)
    name: str = StringProperty("")

    def command(self) :
        if self.activity :
            self.activity(self.name)


class FacultyScreen(Screen) :
    navigation_buttons: MDGridLayout = ObjectProperty(None)
    navigation_screens: ScreenManager = ObjectProperty(None)

    room_data: dict = ObjectProperty()
    instructor_data: dict = ObjectProperty()

    current_screen: str = StringProperty("")
    list_of_screens: dict[str, TeachersScreen] = DictProperty({})

    exit_command : callable = ObjectProperty() # Use to exit the screen

    def on_pre_enter(self, *args) :
        if self.parent :

            self.exit_command = self.parent.switchScreenByName

            if not self.parent.parent.hasData() :  # Check if MainWindow hold the data already
                self.parent.parent.loadScreenData()

            self.room_data = self.parent.parent.getRoomData()
            self.instructor_data = self.parent.parent.getInstructorData()

            self.navigation_buttons.clear_widgets()
            for key, values in self.instructor_data.items() :

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

                # Checking if it has screen used
                if not self.current_screen :
                    self.changeScreen(key)

            self.update()

    def getKeyByRoomName(self , room : str ) -> str :
        for key in self.room_data:
            if self.room_data[key]['name'] == room:
                return key

    def getAllRooms(self) -> tuple[str, ...] :
        return tuple(self.room_data[room]['name'] for room in self.room_data)

    def update(self , *args) :
        for child in self.navigation_buttons.children :
            if child.name == self.current_screen :
                child.isSelected = True
            else :
                if child.isSelected :
                    child.isSelected = False

    def changeScreen(self, name: str) :
        self.current_screen = name
        self.update()
        self.list_of_screens[name].updateDisplay(self.instructor_data[name])
        self.navigation_screens.switch_to(self.list_of_screens[name])
        self.update_navigation_content()

    def update_navigation_content(self) :
        for nav_button in self.navigation_buttons.children :
            nav_button.text = self.instructor_data[nav_button.name]['person']

    def update_instructor_data(self, instructor: str, name=None, information=None, locations=None) :
        """
        :param instructor: the key string for data structure
        :param name: new name of the instructor
        :param information: new information of the instructor
        :param locations: new data for new locations; structure = { room : [ start time - end time, ... ] }
        :return: None
        """

        instructor_data = self.instructor_data.get(instructor, None)

        if not instructor_data :
            print(f"[!] Instructor does not exist ; {instructor_data}")
            return

        if name :
            instructor_data['person'] = name
        if information :
            instructor_data['information'] = information
        if locations :
            instructor_data['locations'] = locations

        self.instructor_data[instructor] = instructor_data
        filename, folder = self.parent.parent.instructor_filename()
        self.parent.parent.saveNewData(filename=filename, data=self.instructor_data, folder=folder)

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
    teacher_time: list[[str, datetime, datetime], ...] = ListProperty([])

    # Data Structure teacher_time : [ (room, time_start , time_end ) , ]

    def on_kv_post(self, base_widget) :
        self.information.title.text = "INFORMATION"
        self.information.info.text = "    This room is an inventory room for all the un used supply"

    def on_enter(self, *args) :
        self.enter_animate.start(self)
        self.updateOnlyTeacherScreen()

    def on_leave(self, *args) :
        self.leave_animate.start(self)

    def getScreenInformation(self) -> dict :
        # Data Structure = { directions : ( text , int ) }
        if self.isRoom :
            return {"directions" : self.__data["directions"]}
        else :
            return {"directions" : ["I can't find the location of the instructor", 1]}

    def updateOnlyTeacherScreen(self) :
        # TODO: Update the screen if it TEACHER Screen
        try:
            current_time = datetime.now()
            if self.parent and self.screen_id and not self.isRoom :
                for name, time_start, time_end in self.teacher_time :
                    if time_start.hour <= current_time.hour <= time_end.hour :  # Check if the current hour in the hour range
                        if time_start.minute <= current_time.minute :  # Check if the current minute in the minute range
                            # TODO: Set new location screen for teacher
                            room_data = self.parent.parent.parent.parent.getSpecificRoom(name)
                            self.image2.locationImage.source = room_data["building picture"]
                            self.image2.locationName.text = room_data["name"]
                            self.directions.info.text = room_data["directions"][0]
                            break
                else :
                    # TODO: Set new location screen for teacher if no specified room
                    room_data = self.parent.parent.parent.parent.getSpecificRoom(self.ifNoTimeSpecifiedUseThisKey)
                    self.image2.locationImage.source = room_data["building picture"]
                    self.image2.locationName.text = room_data["name"]
                    self.directions.info.text = room_data["directions"][0]

        except AttributeError: # I put this to handle error when changing screen
            pass

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

    index_of_screen : int = NumericProperty(0)
    main_event : Clock = None
    changing_screen_event : Clock = None

    def update_activity(self, interval: float) :
        if self.parent :
            if self.parent.parent.location_selected :
                self.changeScreen(self.parent.parent.location_selected)
                self.parent.parent.location_selected = ""

    def changeScreen(self, name: str) :
        if name not in self.screens_names :
            raise Exception(f"Can't change screen, {name} screen does not exist")
        self.__okey_to_animate = False
        self.screens_handler.current = name

    def okeyToChangeScreen(self) :
        self.__okey_to_animate = True

    def on_enter(self, *args) :

        self.main_event = Clock.schedule_interval(self.update_activity, 1 / 30)

        try:
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

        except AttributeError :  # I put this to handle error when changing screen
            pass

    def animate(self , *args):
        self.index_of_screen = self.index_of_screen + 1 if (self.index_of_screen + 1) < len(self.screens_names) else 0
        self.screens_handler.current = self.screens_names[self.index_of_screen]
        self.changing_screen_event =Clock.schedule_once(self.animateChangingScreens , self.__changing_speed)

    def animateChangingScreens(self , *args) :
        if self.__okey_to_animate :
            self.changing_screen_event = Clock.schedule_once(self.animate, self.__changing_speed)
        else :
            self.changing_screen_event = Clock.schedule_once(self.animateChangingScreens , 1 / 30)

    def controlVariables(self, okey_to_animate=None, changing_speed=None) :
        if okey_to_animate is not None :
            self.__okey_to_animate = okey_to_animate
        if changing_speed is not None :
            self.__changing_speed = changing_speed

    def on_leave(self, *args):
        self.__okey_to_animate = False
        Clock.unschedule(self.main_event)
        Clock.unschedule(self.changing_screen_event)


# ------------------------ Developer Screens ----------------------

class DeveloperScreen(Screen) :
    pass
