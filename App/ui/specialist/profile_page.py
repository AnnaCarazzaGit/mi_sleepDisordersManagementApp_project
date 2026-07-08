import re
import customtkinter as ctk
from ui.style_ctk import *

class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, main_window, db):
        super().__init__(master, fg_color=COLORS["background"])
        self.main_window = main_window
        self.db = db
        self.original_data = {}

   
    # Load and display user data
    def load_user_data(self):
        user_id = self.main_window.current_user["id"] if self.main_window.current_user else None
        if user_id is None:
            show_custom_error(self, title="Error", message="User not logged in.")
            return

        user_data = self.db.get_user_by_id(user_id)
        if user_data is None:
            show_custom_error(self, title="Error", message="User data not found.")
            return

        self.original_data = {
            "name": user_data[1],
            "surname": user_data[2],
            "phone": user_data[3],
            "email": user_data[4],
            "gender": user_data[5],
            "birthdate": user_data[6],
            "privacy": user_data[10],
            "hours": user_data[12],
            "clinic_address": user_data[13],
            "specialization": user_data[14],
        }

        self.init_view_mode()

    
    # View Mode: read-only profile info
    def init_view_mode(self):
        for widget in self.winfo_children():
            widget.destroy()

        create_label(self, "Profile Information", size=FONT_SIZES["large"]).pack(pady=20)

        container = ctk.CTkFrame(self, fg_color="#A9D8F4")
        container.pack(padx=30, pady=10)

        field = [
            "name", "surname", "birthdate", "gender", "specialization",
            "phone", "clinic_address", "email", "hours"
        ]

        for i, field in enumerate(field):
            value = self.original_data.get(field, "N/A")
            label_text = field.replace("_", " ").capitalize()

            field_label = ctk.CTkLabel(
                container,
                text=f"{label_text}:",
                font=ctk.CTkFont(size=20, weight="bold"),
                anchor="w"
            )
            field_label.grid(row=i, column=0, sticky="w", padx=(0, 10), pady=5)

            value_label = ctk.CTkLabel(
                container,
                text=value,
                font=ctk.CTkFont(size=20),
                anchor="w"
            )
            value_label.grid(row=i, column=1, sticky="w", pady=5)

        ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18)).pack(pady=10)

        create_primary_button(self, "Edit Profile", command=self.init_edit_mode).pack(pady=10)
        create_secondary_button(self, "Back to Home", command=lambda: self.main_window.show_page("home")).pack(pady=10)


    # Edit Mode: show editable fields
    def init_edit_mode(self):
        for widget in self.winfo_children():
            widget.destroy()

        create_label(self, "Edit Profile", size=20).pack(pady=20)

        self.input_password = create_entry(self, placeholder_text="New password", show="*")
        self.input_password.pack(pady=5)

        self.input_phone = create_entry(self)
        self.input_phone.insert(0, self.original_data.get("phone", ""))
        self.input_phone.pack(pady=5)

        self.input_address = create_entry(self)
        self.input_address.insert(0, self.original_data.get("clinic_address", ""))
        self.input_address.pack(pady=5)

        self.input_email = create_entry(self)
        self.input_email.insert(0, self.original_data.get("email", ""))
        self.input_email.pack(pady=5)

        create_primary_button(self, "Save Changes", command=self.save_data).pack(pady=10)
        create_secondary_button(self, "Cancel", command=self.init_view_mode).pack(pady=5)

   
    # Save and validate profile changes
    def save_data(self):
        password = self.input_password.get()
        phone = self.input_phone.get().strip()
        address = self.input_address.get().strip()
        email = self.input_email.get().strip()

        if not all([phone, address, email]):
            show_custom_error(self, title="Error", message="All fields are required.")
            return

        if "@" not in email or "." not in email:
            show_custom_warning(self, title="Error", message="Invalid email address.")
            return

        if not phone.isdigit() or len(phone) < 8:
            show_custom_warning(self, title="Error", message="Invalid phone number.")
            return

        if password and password != self.original_data.get("password", ""):
            errors = self.check_password_constraints(password, self.original_data.get("password", ""))
            if errors:
                show_custom_warning(self, title="Password Error", message="\n".join(errors))
                return
        else:
            password = self.original_data.get("password", "")

        show_custom_confirm(
            self,
            title="Confirm Changes",
            message="Do you want to save the changes?",
            on_yes=lambda: self.apply_profile_changes(phone, address, email, password) 
        )

    def apply_profile_changes(self, phone, address, email, password):
        user_id = self.main_window.current_user["id"]

        try:
            self.db.update_user_profile(
                user_id=user_id,
                phone=phone,
                address=address,
                email=email,
                password=password
            )
            self.load_user_data()
            show_custom_warning(self, title="Success", message="Profile updated successfully.")
            self.init_view_mode()
        except Exception as e:
            show_custom_error(self, title="Error", message=f"Failed to update profile: {e}")


    # Password validation rules
    def check_password_constraints(self, password, old_password=None):
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


def show_custom_confirm(master, title, message, on_yes, on_no=None):
    win = ctk.CTkToplevel(master)
    win.title(title)
    win.geometry("400x180")
    win.grab_set()

    create_label(win, message, size=FONT_SIZES["medium"]).pack(pady=30)

    button_frame = create_frame(win)
    button_frame.pack(pady=10)

    def yes_action():
        win.destroy()
        on_yes()

    def no_action():
        win.destroy()
        if on_no:
            on_no()

    create_primary_button(button_frame, "Yes", yes_action).pack(side="left", padx=20)
    create_secondary_button(button_frame, "No", no_action).pack(side="left", padx=20)
