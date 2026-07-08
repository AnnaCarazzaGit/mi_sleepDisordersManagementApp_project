import customtkinter as ctk
from ui.style_ctk import *

class PatientPage(ctk.CTkFrame):
    def __init__(self, master, main_window):
        super().__init__(master, fg_color=COLORS["background"])
        self.main_window = main_window
        self.db = main_window.db
        self.patient_id = None

        # Title
        create_label(self, "Patient Search", size=FONT_SIZES["large"]).pack(pady=(30, 10))

        # Input field for patient tax code (ID)
        self.input_id = create_entry(self, placeholder_text="Enter patient's tax code", width=300)
        self.input_id.pack(pady=10)

        # Search button
        create_primary_button(self, "Search Patient", command=self.search_patient).pack(pady=10)

        # Results frame (initially hidden)
        self.result_frame = create_frame(self)
        self.result_frame.pack(fill="x", padx=20, pady=20)
        self.result_frame.pack_forget()

        # Back to Home button
        create_secondary_button(self, "Back to Home", command=lambda: self.main_window.show_page("home")).pack(pady=10)

    def search_patient(self):
        self.patient_id = self.input_id.get().strip()
        if not self.patient_id:
            show_custom_warning(self, title="Warning", message="Please enter a tax code.")
            return

        # Search for the patient in the database
        patient_data = self.db.get_patient_by_cf(self.patient_id)
        if patient_data:
            self.display_patient_info(patient_data)
        else:
            show_custom_error(self, title="Error", message="Patient not found.")
            self.result_frame.pack_forget()

    def display_patient_info(self, data):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        create_label(self.result_frame, "Patient Information", size=FONT_SIZES["medium"]).pack(pady=(10, 15))

        self.add_info_row("Full Name", f"{data['Name']} {data['Surname']}")
        self.add_info_row("Birthdate", data["Birth_Date"])
        self.add_info_row("Gender", data["Gender"])
        self.add_info_row("Last Visit", data.get("Last_Visit", "N/A"))
        self.add_info_row("Next Visit", data.get("Next_Visit", "N/A"))

        # Action buttons
        create_primary_button(
            self.result_frame,
            "View Prescriptions",
            command=lambda: self.main_window.open_prescription_page(self.patient_id)
        ).pack(pady=5)

        create_primary_button(
            self.result_frame,
            "View Patient's Diary",
            command=lambda: self.main_window.open_diary_page(self.patient_id)
        ).pack(pady=5)

        create_primary_button(
            self.result_frame,
            "View Sensor Data",
            command=lambda: self.main_window.open_sensor_data_page(self.patient_id)
        ).pack(pady=5)

        self.result_frame.pack(fill="x", padx=20, pady=20)

    def add_info_row(self, label_text, value_text):
        row = ctk.CTkFrame(self.result_frame)
        row.pack(anchor="w", fill="x", pady=2, padx=10)
        create_label(row, f"{label_text}:", size=20).pack(side="left")
        create_label(row, value_text, size=20).pack(side="left", padx=5)

