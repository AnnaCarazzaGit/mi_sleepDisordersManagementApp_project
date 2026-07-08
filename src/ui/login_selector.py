import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from ui.style_ctk import *
from ui.login_page import LoginPage  
from ui.login_patient import PatientLoginPage  
from ui.login_manager import ManagerLoginPage  
from ui.main_window import MainWindow 

class LoginSelector(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color=COLORS["background"])
        self.root = root
        # self.on_success = on_success  # <-- Add this
        self.pack(fill="both", expand=True)

        logo_path = "logoASE.png" 
        logo_image = Image.open(logo_path)
        logo_ctk = CTkImage(light_image=logo_image, dark_image=logo_image, size=(400, 250)) 
        ctk.CTkLabel(self, image=logo_ctk, text="").pack(pady=20)  

        create_label(self, text="Welcome!", size=32, color="#336699").pack(pady=40)

        create_primary_button(
            self, text="Patient Login", command=self.open_patient_login
        ).pack(pady=20)

        create_primary_button(
            self,
            text="Specialist Login",
            command=lambda: self.open_login("specialist")
        ).pack(pady=20)


        ctk.CTkLabel(self, text="").pack(expand=True)
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=20)
        ctk.CTkLabel(footer_frame, text="If you are a manager,", text_color="#4D4D4D", font=ctk.CTkFont(size=16)).pack()
        ctk.CTkButton(
            footer_frame, text="Click here", fg_color="transparent", text_color="#336699", hover_color="#eeeeee", font=ctk.CTkFont(size=18, weight="bold"),
            command=self.open_manager_login
        ).pack()

    def open_patient_login(self):
        self.pack_forget()
        PatientLoginPage(self.root, on_success=self.launch_patient_app)

    # If you want to use Face ID, remove the # from the code below (lines 49-50-51) and add # to lines 44–45–46
    
    # def open_patient_login(self):
        # self.pack_forget()
        # PatientLoginPage(self.root, on_success=self.on_success)  # <-- Pass the callback properly

    def open_login(self, role):
        self.pack_forget()
        LoginPage(self.root, role, on_success=self.launch_after_login)

    def open_manager_login(self):
        self.pack_forget()
        ManagerLoginPage(self.root, on_success=self.launch_manager_dashboard)

    def launch_patient_app(self, user_id):
        from ui.patient.patient import PatientPage
        self.destroy()
        PatientPage(self.root, user_id).pack(fill="both", expand=True)

    def launch_after_login(self, user_info):
        self.destroy()
        MainWindow(self.root, user_info)

    def launch_manager_dashboard(self, manager_info):
        from ui.manager.appmanager import ManagerDashboardPage
        self.destroy()
        ManagerDashboardPage(self.master, manager_info).pack(fill="both", expand=True)

    def back_to_selector(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        LoginSelector(self.root)
