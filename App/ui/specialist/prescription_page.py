import customtkinter as ctk
from ui.style_ctk import *
from datetime import datetime

class PrescriptionPage(ctk.CTkFrame):
    def __init__(self, master, main_window):
        super().__init__(master, fg_color=COLORS["background"])
            
        self.main_window = main_window
        self.db = main_window.db
        self.patient_id = None
        self.prescriptions = []
        self.editing_prescription_id = None

    
    # Load and display prescriptions
    def load_prescription(self, patient_id):
        self.patient_id = patient_id
        self.prescriptions = self.db.load_prescription(patient_id)
        self.clear_page()
        self.build_view_mode()

    def clear_page(self):
        for widget in self.winfo_children():
            widget.destroy()

    def build_view_mode(self):
        self.clear_page()
        create_label(self, "Active Prescriptions", size=FONT_SIZES["large"]).pack(pady=10)

        if self.prescriptions:
            for presc in self.prescriptions:
                group = create_frame(self)
                group.pack(fill="x", padx=20, pady=10)

                create_label(group, f"Medication: {presc['medication']}", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)
                create_label(group, f"Dosage: {presc['dosage']}", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)
                create_label(group, f"Frequency: {presc['frequency']}", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)
                create_label(group, f"Therapy: {presc['therapy']}", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)
                create_label(group, f"Notes: {presc['text']}", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)
                create_label(group, f"Date: {presc['visit_date']}", size=FONT_SIZES["small"]).pack(anchor="w", padx=10)

                btn_row = create_frame(group, bg_color="transparent")
                btn_row.pack(anchor="e", pady=5, padx=10)

                create_primary_button(
                    btn_row,
                    text="Edit",
                    command=lambda pid=presc["id"]: self.edit_prescription(pid)
                ).pack(side="left", padx=5)

                create_secondary_button(
                    btn_row,
                    text="Delete",
                    command=lambda pid=presc["id"]: self.delete_prescription(pid)
                ).pack(side="left", padx=5)
        else:
            create_label(self, "No prescriptions found.").pack(pady=20)

        # Navigation buttons
        button_row = create_frame(self, bg_color="transparent")
        button_row.pack(pady=15)

        create_secondary_button(
            button_row, "Back",
            command=lambda: self.main_window.show_page("patients")
        ).pack(side="left", padx=10)

        create_primary_button(button_row, "New Prescription", command=self.build_add_mode).pack(side="left", padx=10)


    # Add new prescription
    def build_add_mode(self):
        self.clear_page()
        create_label(self, "Add New Prescription", size=FONT_SIZES["large"]).pack(pady=10)

        self.med_input = create_entry(self, placeholder_text="Medication")
        self.med_input.pack(pady=5)

        self.dosage_input = create_entry(self, placeholder_text="Dosage")
        self.dosage_input.pack(pady=5)

        self.freq_input = create_entry(self, placeholder_text="Frequency")
        self.freq_input.pack(pady=5)

        self.text_input = create_entry(self, placeholder_text="Additional notes")
        self.text_input.pack(pady=5)

        self.therapy_input = create_entry(self, placeholder_text="Therapy")
        self.therapy_input.pack(pady=5)

        self.date_input = create_entry(self, placeholder_text="Date (YYYY-MM-DD)")
        self.date_input.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_input.pack(pady=5)

        create_primary_button(self, "Save Prescription", command=self.save_new_prescription).pack(pady=10)
        create_secondary_button(self, "Cancel", command=self.build_view_mode).pack(pady=5)

    def save_new_prescription(self):
        medication = self.med_input.get().strip()
        dosage = self.dosage_input.get().strip()
        frequency = self.freq_input.get().strip()
        text = self.text_input.get().strip()
        therapy = self.therapy_input.get().strip()
        date_prescribed = self.date_input.get().strip()
        doctor_id = self.main_window.current_user["id"]

        if not all([medication, dosage, date_prescribed]):
            show_custom_error(self, title="Error", message="Fields Medication, Dosage, and Date are required.")
            return

        try:
            datetime.strptime(date_prescribed, "%Y-%m-%d")
        except ValueError:
            show_custom_error(self, title="Error", message="Invalid date format. Use YYYY-MM-DD.")
            return

        self.db.create_new_prescription(
            patient_id=self.patient_id,
            doctor_id=doctor_id,
            medication=medication,
            dosage=dosage,
            frequency=frequency,
            text=text,
            therapy=therapy,
            date_prescribed=date_prescribed
        )

        show_custom_warning(self, title="Success", message="Prescription added successfully.")
        self.prescriptions = self.db.load_prescription(self.patient_id)
        self.build_view_mode()


    # Edit existing prescription
    def edit_prescription(self, prescription_id):
        self.editing_prescription_id = prescription_id
        presc = next((p for p in self.prescriptions if p["id"] == prescription_id), None)
        if not presc:
            show_custom_error(self, title="Error", message="Prescription not found.")
            return

        self.clear_page()
        create_label(self, "Edit Prescription", size=FONT_SIZES["large"]).pack(pady=10)

        self.med_input = create_entry(self)
        self.med_input.insert(0, presc["medication"])
        self.med_input.pack(pady=5)

        self.dosage_input = create_entry(self)
        self.dosage_input.insert(0, presc["dosage"])
        self.dosage_input.pack(pady=5)

        self.freq_input = create_entry(self)
        self.freq_input.insert(0, presc["frequency"])
        self.freq_input.pack(pady=5)

        self.text_input = create_entry(self)
        self.text_input.insert(0, presc["text"])
        self.text_input.pack(pady=5)

        self.therapy_input = create_entry(self)
        self.therapy_input.insert(0, presc["therapy"])
        self.therapy_input.pack(pady=5)

        create_primary_button(self, "Save Changes", command=self.save_edited_prescription).pack(pady=10)
        create_secondary_button(self, "Cancel", command=self.build_view_mode).pack(pady=5)

    def save_edited_prescription(self):
        medication = self.med_input.get().strip()
        dosage = self.dosage_input.get().strip()
        frequency = self.freq_input.get().strip()
        text = self.text_input.get().strip()
        therapy = self.therapy_input.get().strip()

        if not all([medication, dosage]):
            show_custom_error(self, title="Error", message="Fields Medication and Dosage are required.")
            return

        self.db.update_prescription(
            prescription_id=self.editing_prescription_id,
            medication=medication,
            dosage=dosage,
            frequency=frequency,
            text=text,
            therapy=therapy
        )

        show_custom_warning(self, title="Success", message="Prescription updated successfully.")
        self.load_prescription(self.patient_id)

    def delete_prescription(self, prescription_id):
        def confirm_deletion():
            self.db.delete_prescription(prescription_id)
            show_custom_warning(self, title="Deleted", message="Prescription deleted successfully.")
            self.load_prescription(self.patient_id)

        show_custom_confirm(
            self,
            title="Confirm Deletion",
            message="Are you sure you want to delete this prescription?",
            on_yes=confirm_deletion
            )
        
def show_custom_confirm(master, title, message, on_yes, on_no=None):
        win = ctk.CTkToplevel(master)
        win.title(title)
        win.geometry("500x180")
        win.grab_set()

        create_label(win, message, size=FONT_SIZES["medium"]).pack(pady=30)

        btn_frame = create_frame(win)
        btn_frame.pack(pady=10)

        def yes():
            win.destroy()
            on_yes()

        def no():
            win.destroy()
            if on_no:
                on_no()

        create_primary_button(btn_frame, "Yes", yes).pack(side="left", padx=10)
        create_secondary_button(btn_frame, "No", no).pack(side="left", padx=10)

        

