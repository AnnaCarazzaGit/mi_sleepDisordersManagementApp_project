import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import re
from ui.style_ctk import *

from ui.database_controller import DatabaseController

class LoginPage(ctk.CTkFrame):
    def __init__(self, root, role, on_success):
        super().__init__(root, fg_color=COLORS["background"])
        self.root = root
        self.role = role
        self.on_success = on_success
        self.db = DatabaseController("insomnia_management.db")
        self.failed_attempts = 0
        self.pack(fill="both", expand=True)

        logo_path = "logoASE.png" 
        logo_image = Image.open(logo_path)
        logo_ctk = CTkImage(light_image=logo_image, dark_image=logo_image, size=(350, 200)) 
        ctk.CTkLabel(self, image=logo_ctk, text="").pack(pady=20)

        # UI - Title and form
        create_label(self, text="Please, enter your credentials:", size=30).pack(pady=50)

        create_label(self, text="Username:").pack(pady=(0, 5))
        self.username_entry = create_entry(self, placeholder_text="Enter username")
        self.username_entry.pack(pady=(0, 20))

        create_label(self, text="Password:").pack(pady=(0, 5))
        self.password_entry = create_entry(self, placeholder_text="Enter password", show="*")
        self.password_entry.pack(pady=(0, 20))

        self.login_button = create_primary_button(self, text="Login", command=self.login)
        self.login_button.pack(pady=(0, 20))

        self.error_label = create_label(self, text="", color="red")
        self.error_label.pack(pady=(0, 10))
        self.error_label.pack_forget()

        create_secondary_button(self, text="Back", command=self.logout_selector).pack(pady=10)


    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.show_error("Username and password cannot be empty.")
            return

        user_info = self.db.get_user(username, password)
        if user_info and user_info["role"] in self.valid_roles():
            self.failed_attempts = 0
            self.pack_forget()
            self.destroy()  
            self.on_success(user_info)  
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.force_password_reset(username)
            else:
                self.show_error("Invalid credentials or role.")

    def valid_roles(self):
        if self.role == "specialist":
            return ["doctor", "psychologist"]
        if self.role == "patient":
            return ["patient"]
        return []

    def force_password_reset(self, username):
        def validate_and_update():
            new_password = self.new_password_entry.get()
            old_password_data = self.db.get_user(username)
            old_password = old_password_data["Password"] if old_password_data else None

            errors = self.check_password_constraints(new_password, old_password)
            if errors:
                show_custom_error(self, title ="Password Error", message="\n".join(errors))
                return

            try:
                self.db.update_password(username, new_password)
                show_custom_warning(self, title="Success", message="Operation completed successfully.")
                reset_window.destroy()
                self.failed_attempts = 0
            except Exception as e:
                show_custom_error(self, title ="Error", message=f"Failed to update password: {e}")

        reset_window = ctk.CTkToplevel(self)
        reset_window.title("Reset Password")
        reset_window.geometry("400x200")

        create_label(reset_window, text="Reset Your Password", size=18).pack(pady=10)
        self.new_password_entry = create_entry(reset_window, placeholder_text="New password", show="*")
        self.new_password_entry.pack(pady=10)
        create_primary_button(reset_window, "Submit", command=validate_and_update).pack(pady=10)

    def check_password_constraints(password, old_password=None):
        valid = True

        if len(password) < 10:
            valid = False
        if not re.search(r"[A-Z]", password):
            valid = False
        if not re.search(r"[!@#$%^&*()_\-+=\[\]{}|\\:;\"'<>,.?/]", password):
            valid = False
        if not re.search(r"\d", password):
            valid = False
        if old_password and password == old_password:
            valid = False

        errors = []
        if not valid:
            errors.append("Password must be at least 10 characters long and contain at least 1 uppercase letter, "
                        "1 special character and 1 number. It must be different from the old password.")

        return errors
    
    def show_error(self, message):
        self.error_label.configure(text=message)
        self.error_label.pack()

    def reset_fields(self):
        self.username_entry.delete(0, ctk.END)
        self.password_entry.delete(0, ctk.END)
        self.error_label.pack_forget()

    def logout_selector(self):
        self.pack_forget()
        self.destroy()
        from ui.login_selector import LoginSelector  
        LoginSelector(self.master).pack(fill="both", expand=True)
