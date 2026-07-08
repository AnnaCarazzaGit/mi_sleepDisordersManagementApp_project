import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from ui.style_ctk import *
from ui.database_controller import DatabaseController

class ManagerLoginPage(ctk.CTkFrame):
    def __init__(self, root, on_success):
        super().__init__(root, fg_color=COLORS["background"])
        self.root = root
        self.on_success = on_success
        self.db = DatabaseController("insomnia_management.db")
        self.pack(fill="both", expand=True)

        logo_path = "logoASE.png" 
        logo_image = Image.open(logo_path)
        logo_ctk = CTkImage(light_image=logo_image, dark_image=logo_image, size=(350, 200)) 
        ctk.CTkLabel(self, image=logo_ctk, text="").pack(pady=20) 

        create_label(self, text="Please, enter your PIN:", size=30).pack(pady=40)

        self.pin_entry = create_entry(self, placeholder_text="Enter PIN", show="*")
        self.pin_entry.pack(pady=20)

        create_primary_button(self, text="Login", command=self.login_with_pin).pack(pady=10)

        self.error_label = create_label(self, text="", color="red")
        self.error_label.pack(pady=5)
        self.error_label.pack_forget()

        create_secondary_button(self, text="Back", command=self.logout_selector).pack(pady=10)

    def login_with_pin(self):
        pin = self.pin_entry.get().strip()
        if not pin:
            self.show_error("Please enter a PIN.")
            return

        manager_info = self.db.get_manager_by_pin(pin)
        if manager_info:
            self.destroy()
            self.on_success(manager_info)
        else:
            self.show_error("Invalid PIN. Access denied.")

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.error_label.pack()

    def logout_selector(self):
        self.pack_forget()
        self.destroy()
        from ui.login_selector import LoginSelector  
        LoginSelector(self.master).pack(fill="both", expand=True)

