import customtkinter as ctk
from ui.style_ctk import *
from ui.database_controller import DatabaseController

from ui.specialist.home_page import HomePage
from ui.specialist.profile_page import ProfilePage
from ui.specialist.patient_page import PatientPage
from ui.specialist.prescription_page import PrescriptionPage
from ui.specialist.diary_page import DiaryPage
from ui.specialist.sensor_data_page import SensorDataPage
from ui.specialist.calendar_page import CalendarPage

from ui.psychologist.home_page import HomePagePsychologist
from ui.psychologist.profile_page import ProfilePagePsychologist
from ui.psychologist.patient_page import PatientPagePsychologist
from ui.psychologist.diary_page import DiaryPagePsychologist
from ui.psychologist.calendar_page import CalendarPagePsychologist
from ui.psychologist.note_page import PsychologistNotesPage

from ui.manager.appmanager import ManagerDashboardPage

class MainWindow:
    def __init__(self, root, user_info):
        self.root = root
        self.root.title("Advanced Sleep Evaluation")
        self.root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")


        # UI style and theme setup
        set_theme()
        apply_window_style(self.root)

        # Database and user info
        self.db = DatabaseController("insomnia_management.db")
        self.current_user = user_info

        # Page container
        self.container = ctk.CTkFrame(self.root)
        self.container.pack(fill="both", expand=True)

        # Preload shared pages
        self.pages = {
            "home": HomePage(self.container, main_window=self),
            "profile": ProfilePage(self.container, main_window=self, db=self.db),
            "patients": PatientPage(self.container, main_window=self),
            "calendar": CalendarPage(self.container, main_window=self),
            
            "home_psychologist": HomePagePsychologist(self.container, main_window=self),
            "profile_psychologist": ProfilePagePsychologist(self.container, main_window=self, db=self.db),
            "patient_psychologist": PatientPagePsychologist(self.container, main_window=self),
            "calendar_psychologist": CalendarPagePsychologist(self.container, main_window=self),
            "psychologist_notes": PsychologistNotesPage(self.container, main_window=self)
        }

        self.current_page = None

        # Decide which homepage to show
        self.handle_login_role(user_info)

    def handle_login_role(self, user_info):
        role = user_info["role"]

        if role == "doctor":
            self.pages["home"] = HomePage(self.container, main_window=self)
            self.pages["patients"] = PatientPage(self.container, main_window=self)
            self.show_page("home")
        elif role == "psychologist":
            self.pages["home_psychologist"] = HomePagePsychologist(self.container, main_window=self)
            self.pages["patient_psychologist"] = PatientPagePsychologist(self.container, main_window=self)
            self.show_page("home_psychologist")
        elif role == "manager":
            self.pages["manager_dashboard"] = ManagerDashboardPage(self.container, main_window=self)
            self.show_page("manager_dashboard")
        else:
            self.root.destroy()

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.pack_forget()
        if page_name in ["profile", "profile_psychologist"]:
            self.pages[page_name].load_user_data()
        elif page_name == "calendar":
            self.pages["calendar"].load_calendar()

        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)

    # Navigation to patient pages (specialist/psychologist)
    def open_prescription_page(self, patient_id):
        self.pages["prescription"] = PrescriptionPage(self.container, main_window=self)
        self.pages["prescription"].load_prescription(patient_id)
        self.show_page("prescription")

    def open_diary_page(self, patient_id):
        page = DiaryPage(self.container, main_window=self, patient_id=patient_id)
        self._switch_page(page)

    def open_sensor_data_page(self, patient_id):
        page = SensorDataPage(self.container, main_window=self, patient_id=patient_id)
        self._switch_page(page)
    
    def open_diary_psychologist(self, patient_id):
        page = DiaryPagePsychologist(self.container, main_window=self, patient_id=patient_id)
        self._switch_page(page)

    def open_note_page(self, patient_id):
        page = PsychologistNotesPage(self.container, main_window=self, patient_id=patient_id)
        self._switch_page(page)

    def _switch_page(self, new_page):
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = new_page
        self.current_page.pack(fill="both", expand=True)

    

        
