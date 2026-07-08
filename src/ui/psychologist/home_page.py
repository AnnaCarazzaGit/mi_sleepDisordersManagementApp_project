import customtkinter as ctk
from ui.style_ctk import *

class HomePagePsychologist(ctk.CTkFrame):
    def __init__(self, master, main_window):
        super().__init__(master, fg_color=COLORS["background"])
        self.main_window = main_window

        welcome_text = "Welcome, Psychologist!"

        # Title label
        create_label(self, welcome_text, size=FONT_SIZES["large"]).pack(pady=(40, 30))

        # Navigation buttons
        self.add_nav_button("Profile", "profile_psychologist")
        self.add_nav_button("Patients", "patient_psychologist")
        self.add_nav_button("Calendar", "calendar_psychologist")

        # Spacer
        ctk.CTkLabel(self, text="").pack(pady=30)

        # Logout button
        logout_btn = create_secondary_button(self, "Logout", command=self.logout)
        logout_btn.pack(pady=10)

    def add_nav_button(self, text, page_name):
        btn = create_primary_button(self, text, command=lambda: self.main_window.show_page(page_name))
        btn.pack(pady=10)

    def logout(self):
        for widget in self.main_window.root.winfo_children():
            widget.destroy()
            from ui.login_selector import LoginSelector
            LoginSelector(self.main_window.root)
