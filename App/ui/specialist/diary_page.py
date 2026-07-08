import customtkinter as ctk
from datetime import date, timedelta
from ui.style_ctk import *
import sqlite3

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

class DiaryPage(ctk.CTkFrame):
    def __init__(self, master, main_window, patient_id=None):
        super().__init__(master, fg_color=COLORS["background"])
            
        self.main_window = main_window
        self.patient_id = patient_id
        self.week_offset = 0
        self.selected_date = date.today()
        self.conn = sqlite3.connect("diary_responses.db")
        self.conn.row_factory = sqlite3.Row


        # Header and navigation
        create_label(self, "Daily Diary", size=FONT_SIZES["large"]).pack(pady=10)

        self.date_label = create_label(self, "", size=20)
        self.date_label.pack(pady=(0, 10))

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=5)

        create_primary_button(nav_frame, "← Previous Week", command=self.prev_week).pack(side="left", padx=10)
        create_primary_button(nav_frame, "Next Week →", command=self.next_week).pack(side="left", padx=10)

        
        # Calendar and score display
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.pack(pady=20)

        self.score_label = create_label(self, "", size=26)
        self.score_label.pack(pady=5)

        self.status_label = create_label(self, "", size=FONT_SIZES["medium"])
        self.status_label.pack(pady=5)

        self.report_button = create_primary_button(self, "Alert Patient", command=self.report_to_patient)
        self.report_button.pack(pady=5)
        self.report_button.pack_forget()

        create_secondary_button(self, "Back", command=lambda: self.main_window.show_page("patients")).pack(pady=10)

        self.update_calendar()

    
    # Load diary score
    def fetch_score(self, target_date):
        cursor = self.conn.cursor()
        query = "SELECT value FROM DIARY WHERE patient_id = ? AND date = ?"
        cursor.execute(query, (self.patient_id, target_date.strftime("%Y-%m-%d")))
        row = cursor.fetchone()
        return row["value"] if row else None

    
    # Update calendar week view
    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        today = date.today()
        monday = today + timedelta(days=-today.weekday(), weeks=self.week_offset)
        self.dates = [monday + timedelta(days=i) for i in range(7)]

        start = self.dates[0].strftime("%d %B %Y")
        end = self.dates[-1].strftime("%d %B %Y")
        self.date_label.configure(text=f"Week: {start} → {end}")

        row = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        row.pack()

        for idx, d in enumerate(self.dates):
            btn = ctk.CTkButton(
                row,
                text=f"{DAYS[idx]}\n{d.strftime('%d/%m')}",
                width=100,
                height=60,
                fg_color="#ffffff",
                text_color="black",
                hover_color="#d2ecff",
                command=lambda date=d: self.select_date(date)
            )
            btn.pack(side="left", padx=5)

        self.select_date(self.selected_date)

    
    # Select and display daily score
    def select_date(self, selected_date):
        self.selected_date = selected_date
        score = self.fetch_score(selected_date)

        if score is None:
            self.score_label.configure(text="No data available")
            self.status_label.configure(text="Status: N/A", text_color="gray")
            self.report_button.pack_forget()
            return

        self.score_label.configure(text=f"Score: {score}")

        if score <= 7:
            status, color = "OK", "green"
            self.report_button.pack_forget()
        elif score <= 14:
            status, color = "Moderate", "orange"
            self.report_button.pack_forget()
        elif score <= 21:
            status, color = "Severe", "#D97706"
            self.report_button.pack()
        else:
            status, color = "Very Severe", "red"
            self.report_button.pack()

        self.status_label.configure(text=f"Status: {status}", text_color=color)

    
    # Navigate weeks
    def prev_week(self):
        self.week_offset -= 1
        self.update_calendar()

    def next_week(self):
        self.week_offset += 1
        self.update_calendar()

    
    # Alert patient action
    def report_to_patient(self):
        show_custom_warning(self, title="Alert Sent", message="Situation reported to the patient.")

