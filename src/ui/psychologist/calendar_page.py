import customtkinter as ctk
from datetime import date, timedelta, time, datetime
from ui.style_ctk import *


# Configuration: time slots and days
def generate_time_slots(start_hour=14, end_hour=18, interval_minutes=15):
    """Generate time slots every `interval_minutes` between start_hour and end_hour."""
    start = datetime.combine(date.today(), time(hour=start_hour))
    end = datetime.combine(date.today(), time(hour=end_hour))
    slots = []
    while start < end:
        slots.append(start.strftime("%H:%M"))
        start += timedelta(minutes=interval_minutes)
    return slots

TIME_SLOTS = generate_time_slots()
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# Main calendar page class
class CalendarPagePsychologist(ctk.CTkFrame):
    def __init__(self, master, main_window):
        super().__init__(master, fg_color=COLORS["background"])
        self.main_window = main_window
        self.week_offset = 0
        self.dates = []
        self.cells = {}

        # Header title
        create_label(self, "Appointment Calendar", size=FONT_SIZES["large"]).pack(pady=(10, 10))

        # Week range label
        self.date_label = create_label(self, "", size=20)
        self.date_label.pack(pady=(0, 10))

        # Navigation buttons
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=5)
        create_primary_button(nav_frame, "← Previous Week", command=self.prev_week).pack(side="left", padx=10)
        create_primary_button(nav_frame, "Next Week →", command=self.next_week).pack(side="left", padx=10)

        # Calendar grid
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(pady=20)
        self.build_table()

        # Home button
        create_secondary_button(self, "Back to Home", command=lambda: self.main_window.show_page("home_psychologist")).pack(padx=10)

 
    # Build calendar table layout
    def build_table(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        header_row = ctk.CTkFrame(self.calendar_frame)
        header_row.pack(fill="x")
        ctk.CTkLabel(header_row, text="", width=110).pack(side="left")

        for day in DAYS:
            ctk.CTkLabel(header_row, text=day, width=130).pack(side="left", padx=1)

        self.cells = {}

        for time_slot in TIME_SLOTS:
            row = ctk.CTkFrame(self.calendar_frame)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=time_slot, width=80).pack(side="left")

            for col in range(7):
                cell = ctk.CTkButton(
                    row, text="", width=130, height=25,
                    fg_color="white", text_color="black", hover_color="#e6f3ff",
                    command=lambda t=time_slot, c=col: self.add_appointment_popup(t, c)
                )
                cell.pack(side="left", padx=4)
                self.cells[(time_slot, col)] = cell

    
    # Calendar data loading
    def load_calendar(self):
        self.update_calendar()

    def update_calendar(self):
        today = date.today()
        monday = today + timedelta(days=-today.weekday(), weeks=self.week_offset)
        self.dates = [monday + timedelta(days=i) for i in range(7)]
        iso_dates = [d.isoformat() for d in self.dates]

        start = self.dates[0].strftime("%d %B %Y")
        end = self.dates[-1].strftime("%d %B %Y")
        self.date_label.configure(text=f"Week: {start} → {end}")

        for cell in self.cells.values():
            cell.configure(text="", fg_color="white")

        doctor_id = self.main_window.current_user["id"]
        visits = self.main_window.db.get_consults_for_week(doctor_id, iso_dates[0], iso_dates[-1])

        for visit in visits:
            date_str, time_str, patient_name = visit["Date"], visit["Hour"], visit["patient_name"]
            if date_str in iso_dates:
                col = iso_dates.index(date_str)
                row = time_str
                cell = self.cells.get((row, col))
                if cell:
                    cell.configure(text=patient_name, fg_color="#7ecbff", text_color="black")


    # Week navigation
    def prev_week(self):
        self.week_offset -= 1
        self.update_calendar()

    def next_week(self):
        self.week_offset += 1
        self.update_calendar()


    # Appointment creation dialog
    def add_appointment_popup(self, time_str, column):
        selected_date = self.dates[column]

        popup = ctk.CTkToplevel(self)
        popup.title("New Appointment")
        popup.geometry("400x300")

        create_label(popup, f"Date: {selected_date.strftime('%d/%m/%Y')} - {time_str}").pack(pady=15)
        entry = ctk.CTkEntry(popup, placeholder_text="Patient Full Name")
        entry.pack(pady=10)

        def save():
            patient_name = entry.get().strip()
            if not patient_name:
                show_custom_warning(self, title="Warning", message="Please enter a valid name.")
                return

            try:
                self.main_window.db.add_appointment_psychologist(
                    doctor_id=self.main_window.current_user["id"],
                    date_str=selected_date.isoformat(),
                    time_str=time_str,
                    patient_name=patient_name
                )
                popup.destroy()
                self.update_calendar()
            except ValueError as ve:
                show_custom_error(self, title="Error", message=str(ve))
            except Exception as e:
                show_custom_error(self, title="Error", message=f"Error saving appointment: {e}")

        create_primary_button(popup, "Save", command=save).pack(pady=5)
        create_secondary_button(popup, "Cancel", command=popup.destroy).pack(pady=5)


