import customtkinter as ctk
from ui.style_ctk import *
import sqlite3
import random
import string
import datetime

class ManagerDashboardPage(ctk.CTkFrame):
    def __init__(self, master, manager_info):
        super().__init__(master)
        self.master = master
        self.configure(fg_color=COLORS["background"])
        apply_window_style(self)

        self.db = sqlite3.connect("insomnia_management.db")
        self.helpdesk_db = sqlite3.connect("helpdesk.db")

        self.cursor = self.db.cursor()
        self.helpdesk_cursor = self.helpdesk_db.cursor()

        self.current_section = None
        self.create_main_menu()

    def create_main_menu(self):
        self.center_container = ctk.CTkFrame(self)
        self.center_container.pack(pady=20, expand=True)

        self.menu_frame = create_frame(self.center_container, width=400, height=600)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.menu_frame.pack_propagate(False)

        create_label(self.menu_frame, text="Manager Panel", size=FONT_SIZES["large"]).pack(pady=(10, 30))

        create_primary_button(self.menu_frame, "User Management", self.show_user_selection).pack(pady=10)
        create_primary_button(self.menu_frame, "Help Desk", self.show_helpdesk).pack(pady=10)
        create_primary_button(self.menu_frame, "Sensors", self.show_sensor_section).pack(pady=10)
        create_primary_button(self.menu_frame, "System Check", self.system_check).pack(pady=10)
        create_primary_button(self.menu_frame, "Logout", self.logout).pack(pady=(50, 0))

        self.content_frame = create_frame(self.center_container, width=650, height=600)
        self.content_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.content_frame.pack_propagate(False)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_scrollable_section(self):
        container = ctk.CTkFrame(self.content_frame)
        canvas = ctk.CTkCanvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame
    
    def show_user_selection(self):
        self.clear_content()
        create_label(self.content_frame, "Select User Type to Manage", size=FONT_SIZES["large"]).pack(pady=20)

        btn_frame = create_frame(self.content_frame)
        btn_frame.pack(pady=10)

        create_primary_button(btn_frame, "Patients", self.show_patient_management).pack(side="left", padx=20)
        create_primary_button(btn_frame, "Specialists", self.show_specialist_management).pack(side="right", padx=20)

    def show_specialist_management(self):
        self.clear_content()
        create_label(self.content_frame, "Choose Specialist Type", size=FONT_SIZES["large"]).pack(pady=20)

        frame = create_frame(self.content_frame)
        frame.pack(pady=10)

        create_primary_button(frame, "Family Doctor", lambda: self.show_specific_specialist_form("doctor")).pack(pady=5)
        create_primary_button(frame, "Psychologist", lambda: self.show_specific_specialist_form("psychologist")).pack(pady=5)

    def show_patient_management(self):
        self.clear_content()
        create_label(self.content_frame, "Patient Management", size=FONT_SIZES["large"]).pack(pady=10)
        frame = self.create_scrollable_section()

        # Add form
        create_label(frame, "Add New Patient", size=FONT_SIZES["medium"]).pack(pady=10)
        fields = ["Name", "Surname", "Fiscal Code", "Phone Number", "Email", "Gender", "Birthdate (YYYY-MM-DD)",
                  "Residency", "Domicile", "Nationality", "Family Doctor ID", "Psychologist ID"]
        entries = {}
        form = create_frame(frame)
        form.pack()
        for i, field in enumerate(fields):
            create_label(form, field + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entries[field] = create_entry(form, width=300)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        pin = ''.join(random.choices(string.digits, k=6))
        create_label(form, "Generated PIN:").grid(row=len(fields), column=0, sticky="e", padx=5, pady=5)
        pin_entry = create_readonly_entry(form, pin)
        pin_entry.grid(row=len(fields), column=1, padx=5, pady=5)

        def save_patient():
            try:
                user_id = entries["Fiscal Code"].get()
                self.cursor.execute("""
                    INSERT INTO Personal_Info (User_Id, Name, Surname, Phone_Number, Email, Gender, Birthdate, Residency, Domicile, Nationality, Privacy_Consent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, entries["Name"].get(), entries["Surname"].get(), entries["Phone Number"].get(), entries["Email"].get(),
                    entries["Gender"].get(), entries["Birthdate (YYYY-MM-DD)"].get(), entries["Residency"].get(), entries["Domicile"].get(),
                    entries["Nationality"].get(), "1"))

                self.cursor.execute("""
                    INSERT INTO USER (Id, Password, Privacy_Consent, role)
                    VALUES (?, ?, ?, ?)""",
                    (user_id, pin, 1, "patient"))

                self.cursor.execute("INSERT INTO PATIENT (Patient_Id) VALUES (?)", (user_id))

                self.db.commit()
                show_custom_warning(self, "Saved", "Patient successfully saved.")
                self.show_patient_management()
            except Exception as e:
                show_custom_error(self, "Error", str(e))

        create_primary_button(frame, "Save Patient", save_patient).pack(pady=10)

        # Delete
        create_label(frame, "Delete Patient by ID:", size=FONT_SIZES["medium"]).pack(pady=(20, 5))
        delete_entry = create_entry(frame)
        delete_entry.pack()
        create_secondary_button(frame, "Delete", lambda: self.delete_user_and_refresh(delete_entry.get())).pack(pady=5)

        # List
        self.patient_list_frame = create_frame(frame)
        self.patient_list_frame.pack(pady=(10, 20), fill="x")
        self.update_patient_list()

    def update_patient_list(self):
        for widget in self.patient_list_frame.winfo_children():
            widget.destroy()
        self.cursor.execute("SELECT Id FROM USER WHERE role='patient'")
        for uid, in self.cursor.fetchall():
            create_label(self.patient_list_frame, uid, FONT_SIZES["small"]).pack(anchor="w", padx=10)

    def delete_user_and_refresh(self, user_id):
        self.delete_user(user_id)
        self.update_patient_list()

    def show_specific_specialist_form(self, table):
        self.clear_content()
        role_title = "Family Doctor" if table == "doctor" else "Psychologist"
        create_label(self.content_frame, f"{role_title} Management", size=FONT_SIZES["large"]).pack(pady=20)

        frame = self.create_scrollable_section()
        
        # Form
        create_label(frame, f"Add New {role_title}", size=FONT_SIZES["medium"]).pack(pady=10)
        fields = ["Name", "Surname", "Phone Number", "Email", "Gender", "Birthdate (YYYY-MM-DD)",
              "Residency", "Domicile", "Nationality", "Visiting Hours", "Clinic Address"]
        entries = {}
        form = create_frame(frame)
        form.pack()
        for i, field in enumerate(fields):
            create_label(form, field + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entries[field] = create_entry(form, width=300)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        user_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#", k=10))

        create_label(form, "Generated ID:").grid(row=len(fields), column=0, sticky="e", padx=5, pady=5)
        id_entry = create_readonly_entry(form, user_id)
        id_entry.grid(row=len(fields), column=1, padx=5, pady=5)

        create_label(form, "Generated Password:").grid(row=len(fields)+1, column=0, sticky="e", padx=5, pady=5)
        pw_entry = create_readonly_entry(form, password)
        pw_entry.grid(row=len(fields)+1, column=1, padx=5, pady=5)

        def save_specialist():
            try:
                self.cursor.execute("""
                    INSERT INTO Personal_Info (User_Id, Name, Surname, Phone_Number, Email, Gender, Birthdate, Residency, Domicile, Nationality, Privacy_Consent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, entries["Name"].get(), entries["Surname"].get(), entries["Phone Number"].get(), entries["Email"].get(),
                    entries["Gender"].get(), entries["Birthdate (YYYY-MM-DD)"].get(), entries["Residency"].get(), entries["Domicile"].get(),
                    entries["Nationality"].get(), "1"))

                self.cursor.execute("""
                    INSERT INTO USER (Id, Password, Privacy_Consent, role)
                    VALUES (?, ?, ?, ?)""",
                    (user_id, password, 1, table))

                if table == "doctor":
                    self.cursor.execute("""
                        INSERT INTO FAMILY_DOCTOR (Family_Doctor_Id, Visiting_Hours, Clinic_Address, Specialization)
                        VALUES (?, ?, ?, ?)""",
                        (user_id, entries["Visiting Hours"].get(), entries["Clinic Address"].get(), "General Medicine"))
                else:
                    self.cursor.execute("""
                        INSERT INTO PSYCHOLOGIST (Psychologist_Id, Visiting_Hours, Clinic_Address)
                        VALUES (?, ?, ?)""",
                        (user_id, entries["Visiting Hours"].get(), entries["Clinic Address"].get()))

                self.db.commit()
                show_custom_warning(self, "Saved", f"{role_title} saved.")
                self.update_specialist_list(table)
            except Exception as e:
                show_custom_error(self, "Error", str(e))

        create_primary_button(frame, "Save Specialist", save_specialist).pack(pady=10)

        # Delete
        create_label(frame, f"Delete {role_title} by ID:", size=FONT_SIZES["medium"]).pack(pady=(20, 5))
        delete_entry = create_entry(frame, width=300)
        delete_entry.pack()
        create_secondary_button(frame, "Delete", lambda: self.delete_specialist_and_refresh(delete_entry.get(), table)).pack(pady=5)

        # List
        self.specialist_list_frame = create_frame(frame)
        self.specialist_list_frame.pack(pady=(10, 20), fill="x")
        self.update_specialist_list(table)

    def update_specialist_list(self, table):
        for widget in self.specialist_list_frame.winfo_children():
            widget.destroy()
        self.cursor.execute("SELECT Id FROM USER WHERE role=?", (table,))
        for uid, in self.cursor.fetchall():
            create_label(self.specialist_list_frame, uid, size=FONT_SIZES["small"]).pack(anchor="w", padx=10)

    def delete_specialist_and_refresh(self, specialist_id, table):
        self.delete_specialist(specialist_id)
        self.update_specialist_list(table)

    def show_helpdesk(self):
        self.clear_content()

        container = ctk.CTkFrame(self.content_frame)
        container.pack(fill="both", expand=True)

        canvas = ctk.CTkCanvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        create_label(scrollable_frame, "Help Desk", size=FONT_SIZES["large"]).pack(pady=10)

        self.helpdesk_cursor.execute("SELECT message_id, patient_id, text FROM MESSAGE")
        messages = self.helpdesk_cursor.fetchall()

        if not messages:
            create_label(scrollable_frame, "No help desk messages.", size=FONT_SIZES["large"]).pack(pady=20)
            return

        for message_id, patient_id, text in messages:
            msg_frame = create_frame(scrollable_frame)
            msg_frame.pack(pady=10, fill="x", padx=20)

            label = create_label(msg_frame, f"From {patient_id}: {text[:50]}...", size=FONT_SIZES["small"])
            label.pack(anchor="w")
            label.bind("<Button-1>", lambda e, mid=message_id: self.show_helpdesk_detail(mid))

    def show_helpdesk_detail(self, message_id):
        self.clear_content()

        self.helpdesk_cursor.execute("SELECT patient_id, text FROM MESSAGE WHERE message_id=?", (message_id,))
        row = self.helpdesk_cursor.fetchone()
        if not row:
            show_custom_error(self, "Error", "Message not found.")
            return

        patient_id, text = row

        create_label(self.content_frame, f"Help Request from {patient_id}", size=FONT_SIZES["large"]).pack(pady=10)
        create_label(self.content_frame, f"Message:", size=24).pack(anchor="w", padx=20)
        create_label(self.content_frame, text, size=FONT_SIZES["medium"], wraplength=600).pack(padx=20, pady=10, anchor="w")

        create_label(self.content_frame, "Your Response:", size=24).pack(anchor="w", padx=20, pady=(20, 5))
        response_entry = create_entry(self.content_frame, placeholder_text="Write your response here...")
        response_entry.pack(fill="x", padx=20, pady=(0, 10))

        button_frame = create_frame(self.content_frame)
        button_frame.pack(pady=10)

        create_primary_button(button_frame, "Send Response",
            lambda: self.respond_helpdesk(message_id, response_entry.get())
        ).pack(side="left", padx=10)

        create_secondary_button(button_frame, "Back to List", command=self.show_helpdesk).pack(side="left", padx=10)

    def show_sensor_section(self):
        self.clear_content()
        create_label(self.content_frame, "Sensor Management", size=FONT_SIZES["large"]).pack(pady=10)

        frame = self.create_scrollable_section()

        form = create_frame(frame)
        form.pack(pady=10)

        fields = ["Serial Number", "Creation Date (YYYY-MM-DD)", "Association Date (YYYY-MM-DD)", "Patient Fiscal Code"]
        entries = {}
        for i, field in enumerate(fields):
            create_label(form, field + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entries[field] = create_entry(form)
            entries[field].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                serial = entries["Serial Number"].get()
                creation = entries["Creation Date (YYYY-MM-DD)"].get()
                association = entries["Association Date (YYYY-MM-DD)"].get()
                patient = entries["Patient Fiscal Code"].get()
                self.cursor.execute("INSERT INTO SENSOR (Serial_Num, Creation_Date) VALUES (?, ?)", (serial, creation))
                self.cursor.execute("INSERT INTO ASSOCIATION (Patient_Id, Sensor_Serial_Num, Start_Date, App_Manager_Access_Code) VALUES (?, ?, ?, ?)",
                    (patient, serial, association, "manager"))
                self.db.commit()
                show_custom_warning(self, "Saved", "Sensor successfully paired.")
                self.show_sensor_section()
            except Exception as e:
                show_custom_error(self, "Error", str(e))

        create_primary_button(frame, "Save Sensor", save).pack(pady=15)

        create_label(frame, "Delete Sensor by Serial Number:", size=FONT_SIZES["medium"]).pack(pady=(20, 5))
        serial_entry = create_entry(frame)
        serial_entry.pack()
        create_secondary_button(frame, "Delete Sensor", lambda: self.delete_sensor(serial_entry.get())).pack(pady=5)

        create_label(frame, "All Sensors:", size=24).pack(pady=(20, 10))
        self.cursor.execute("SELECT Serial_Num, Creation_Date FROM SENSOR")
        for serial, date in self.cursor.fetchall():
            create_label(frame, f"{serial} ({date})", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)

    def delete_sensor(self, serial):
        try:
            self.cursor.execute("DELETE FROM ASSOCIATION WHERE Sensor_Serial_Num=?", (serial,))
            self.cursor.execute("DELETE FROM SENSOR WHERE Serial_Num=?", (serial,))
            self.db.commit()
            show_custom_warning(self, "Deleted", f"Sensor {serial} deleted.")
            self.show_sensor_section()
        except Exception as e:
            show_custom_error(self, "Error", str(e))

    def delete_user(self, user_id):
            try:
                self.cursor.execute("DELETE FROM PATIENT WHERE Patient_Id = ?", (user_id,))
                self.cursor.execute("DELETE FROM USER WHERE Id = ?", (user_id,))
                self.cursor.execute("DELETE FROM Personal_Info WHERE User_Id = ?", (user_id,))
                self.db.commit()
                show_custom_warning(self, "Deleted", f"User '{user_id}' successfully deleted.")
            except Exception as e:
                show_custom_error(self, "Error", str(e))

    def delete_specialist(self, specialist_id):
        try:
            self.cursor.execute("SELECT role FROM USER WHERE Id = ?", (specialist_id,))
            result = self.cursor.fetchone()

            if result is None:
                show_custom_error(self, "Error", f"No user found with ID '{specialist_id}'.")
                return

            role = result[0]

            if role == "doctor":
                self.cursor.execute("DELETE FROM FAMILY_DOCTOR WHERE Family_Doctor_Id = ?", (specialist_id,))
            elif role == "psychologist":
                self.cursor.execute("DELETE FROM PSYCHOLOGIST WHERE Psychologist_Id = ?", (specialist_id,))
            else:
                show_custom_error(self, "Error", f"The user with ID '{specialist_id}' is not a specialist.")
                return

            self.cursor.execute("DELETE FROM USER WHERE Id = ?", (specialist_id,))
            self.cursor.execute("DELETE FROM Personal_Info WHERE User_Id = ?", (specialist_id,))
            self.db.commit()

            show_custom_warning(self, "Deleted", f"Specialist '{specialist_id}' successfully deleted.")
        
        except Exception as e:
            show_custom_error(self, "Error", str(e))

    def respond_helpdesk(self, message_id, response_text):
        try:
            if not response_text.strip():
                show_custom_error(self, "Error", "Response cannot be empty.")
                return

            self.helpdesk_cursor.execute("DELETE FROM MESSAGE WHERE message_id=?", (message_id,))
            self.helpdesk_db.commit()

            show_custom_warning(self, "Response Sent", "The patient has been answered.")
            self.show_helpdesk()
        except Exception as e:
            show_custom_error(self, "Error", str(e))

    def system_check(self):
        self.clear_content()
        create_label(self.content_frame, "System Status Check", size=FONT_SIZES["large"]).pack(pady=20)

        progress_label = create_label(self.content_frame, "Checking system...", size=24)
        progress_label.pack(pady=10)

        progress_bar = ctk.CTkProgressBar(self.content_frame, width=400)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        last_update_label = create_label(self.content_frame, "", size=16, color="#555555")
        last_update_label.pack(pady=(5, 20))

        def update_bar(value=0):
            if value <= 1:
                progress_bar.set(value)
                self.after(50, lambda: update_bar(value + 0.01))
            else:
                progress_label.configure(text="✔ System is active and running smoothly.", text_color="green")
                last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_update_label.configure(text=f"Last checked: {last_update}")

        update_bar()
        create_primary_button(self.content_frame, "Run Check Again", self.system_check).pack(pady=10)


    def logout(self):
        self.pack_forget()
        self.destroy()

        from ui.login_selector import LoginSelector
        LoginSelector(self.master).pack(fill="both", expand=True)
