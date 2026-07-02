import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import json
import os
import re

# ----------------------------- UTENTE -----------------------------
users_db = {
    "emma": {
        "password": "emma",
        "face_id": True,
        "attempts": 0,
    }
}

patient_data = {
    "name": "Giulia Rossi",
    "fiscal_code": "ABC123DEF",
    "birthdate": "1996-08-01",
    "gender": "Female",
    "residency": "Torino",
    "domicile": "Via Po, 12",
    "nationality": "Italian",
    "family_doctor": "Dr. Bianchi",
    "psychologist": "Dr.ssa Neri",
    "phone": "+39 331 1234567",
    "email": "giulia@example.com",
    "privacy_consent": "Yes",
    "password": "emma",
}

available_slots = {
    "Dr. Bianchi": [f"2025-05-{d:02d} 10:00" for d in range(10, 15)],
    "Dr.ssa Neri": [f"2025-05-{d:02d} 15:00" for d in range(16, 21)],
}
booked_visits = []

def generate_visit_code():
    return f"VIS{1000 + len(booked_visits)}"

def authenticate(id_code, password=None):
    user = users_db.get(id_code)
    if not user:
        return "ID not found"
    if password == user["password"]:
        user["attempts"] = 0
        return "success"
    user["attempts"] += 1
    if user["attempts"] >= 3:
        return "reset"
    return "wrong_password"

# ----------------------------- GRAFICO -----------------------------
def embed_sleep_graph_in_frame(parent_frame):
    sleep_data = [
        ("01:26", "01:40", "Awake"),
        ("01:40", "01:55", "REM"),
        ("01:55", "02:20", "Deep"),
        ("02:20", "02:40", "Awake"),
        ("02:40", "03:05", "REM"),
        ("03:05", "03:30", "Deep"),
        ("03:30", "04:00", "Light"),
        ("04:00", "04:30", "Awake"),
        ("04:30", "05:00", "REM"),
        ("05:00", "05:30", "Light"),
        ("05:30", "06:00", "Deep"),
        ("06:00", "06:30", "Light"),
        ("06:30", "07:00", "REM"),
        ("07:00", "07:28", "Awake"),
    ]

    phase_levels = {"Awake": 3, "REM": 2, "Light": 1, "Deep": 0}

    x_vals = []
    y_vals = []

    for start, end, phase in sleep_data:
        start_dt = datetime.datetime.strptime(start, "%H:%M")
        end_dt = datetime.datetime.strptime(end, "%H:%M")
        x_vals.extend([start_dt, end_dt])
        y_vals.extend([phase_levels[phase], phase_levels[phase]])

    fig = Figure(figsize=(7, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x_vals, y_vals, drawstyle='steps-post', linewidth=2)
    ax.set_yticks(list(phase_levels.values()))
    ax.set_yticklabels(list(phase_levels.keys()))
    ax.set_xlabel("Time")
    ax.set_ylabel("Sleep Phase")
    ax.set_title("Sleep Phases Over Time")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ----------------------------- STATISTICHE -----------------------------
def get_stats_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="\ud83d\udcca Statistics and Diagrams", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    parameters = ["Total sleep time", "Time in bed vs time asleep", "Sleep stages"]
    timeframes = ["One night", "Last 7 days", "Last month"]

    ctk.CTkLabel(frame, text="Select Parameter").pack(pady=(10, 5))
    param_var = ctk.StringVar(value=parameters[0])
    ctk.CTkOptionMenu(frame, values=parameters, variable=param_var).pack()

    ctk.CTkLabel(frame, text="Select Timeframe").pack(pady=(20, 5))
    time_var = ctk.StringVar(value=timeframes[0])
    ctk.CTkOptionMenu(frame, values=timeframes, variable=time_var).pack()

    def open_graph():
        selected_param = param_var.get()
        selected_time = time_var.get()
        popup = ctk.CTkToplevel()
        popup.geometry("800x400")
        popup.title(f"{selected_param} - {selected_time}")
        if selected_param == "Sleep stages" and selected_time == "One night":
            embed_sleep_graph_in_frame(popup)
        else:
            ctk.CTkLabel(popup, text="\u26a0 No data available for selected combination").pack(pady=50)

    ctk.CTkButton(frame, text="Show Diagram", command=open_graph).pack(pady=30)
    return frame

# ----------------------------- LOGIN -----------------------------
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success

        ctk.CTkLabel(self, text="Patient Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        self.id_entry = ctk.CTkEntry(self, placeholder_text="ID Code")
        self.id_entry.pack(pady=10)
        self.pw_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.pw_entry.pack(pady=10)
        ctk.CTkButton(self, text="Login", command=self.login_with_credentials).pack(pady=5)

    def login_with_credentials(self):
        result = authenticate(self.id_entry.get(), password=self.pw_entry.get())
        self.handle_result(result)

    def handle_result(self, result):
        if result == "success":
            self.on_success()
        elif result == "wrong_password":
            messagebox.showerror("Login Failed", "Wrong ID or password.")
        elif result == "reset":
            messagebox.showwarning("Too Many Attempts", "Please reset your password.")
        elif result == "ID not found":
            messagebox.showerror("User Not Found", "No user found with that ID Code.")

# ----------------------------- APP PRINCIPALE -----------------------------
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sleep Health App")
        self.geometry("1000x600")
        self.configure(fg_color="#f2f4f7")
        self.login_frame = LoginFrame(self, self.after_login)
        self.login_frame.pack(expand=True, fill="both")

    def after_login(self):
        self.login_frame.destroy()
        self.show_welcome_menu()

    def show_welcome_menu(self):
        self.menu_frame = ctk.CTkFrame(self, fg_color="#ffffff")
        self.menu_frame.pack(expand=True)

        ctk.CTkLabel(
            self.menu_frame,
            text="Welcome to E³A²S",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#003366"
        ).pack(pady=30)

        ctk.CTkButton(self.menu_frame, text="Profile", width=200, command=self.activate_profile).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Visits", width=200, command=self.activate_visits).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Statistics and Diagrams", width=200, command=self.activate_stats).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="My Diary", width=200, command=self.activate_diary).pack(pady=10)

    def setup_sidebar(self):
        self.menu_frame.destroy()
        self.sidebar = ctk.CTkFrame(self, width=180)
        self.sidebar.pack(side="left", fill="y")
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", expand=True, fill="both")

        ctk.CTkButton(self.sidebar, text="Profile", command=self.show_profile).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Visits", command=self.show_visits).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Statistics", command=self.show_stats).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="My Diary", command=self.show_diary).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Help Desk", command=self.show_helpdesk).pack(pady=10, padx=10)

    def clear_main_content(self):
        if hasattr(self, "main_content"):
            for widget in self.main_content.winfo_children():
                widget.destroy()

    def activate_profile(self):
        self.setup_sidebar()
        self.show_profile()

    def activate_visits(self):
        self.setup_sidebar()
        self.show_visits()

    def activate_stats(self):
        self.setup_sidebar()
        self.show_stats()

    def activate_diary(self):
        self.setup_sidebar()
        self.show_diary()

    def show_profile(self):
        self.clear_main_content()
        ctk.CTkLabel(self.main_content, text="\U0001F464 Profile (Placeholder)").pack(pady=100)

    def show_visits(self):
        self.clear_main_content()
        ctk.CTkLabel(self.main_content, text="\U0001F4C5 Visits (Placeholder)").pack(pady=100)

    def show_stats(self):
        self.clear_main_content()
        get_stats_frame(self.main_content).pack(fill="both", expand=True)

    def show_diary(self):
        self.clear_main_content()
        ctk.CTkLabel(self.main_content, text="\U0001F4D2 Diary (Placeholder)").pack(pady=100)

    def show_helpdesk(self):
        self.clear_main_content()
        ctk.CTkLabel(self.main_content, text="🆘 Help Desk (Placeholder)").pack(pady=100)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MainApp()
    app.mainloop()
    

