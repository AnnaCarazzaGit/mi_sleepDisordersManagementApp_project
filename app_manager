import customtkinter as ctk
import random
import time
import threading

MANAGER_CODE = "admin"

class ManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Manager Dashboard")
        self.geometry("1000x700")
        self.configure(fg_color="#f2f4f7")

        self.sidebar = self.create_sidebar()
        self.sidebar.pack_forget()  # Hidden until after "Manager Panel"

        self.main_area = ctk.CTkFrame(self, fg_color="#ffffff")
        self.main_area.pack(side="right", expand=True, fill="both")

        self.login_frame = self.create_login_frame()
        self.login_frame.pack(in_=self.main_area, expand=True, fill="both")

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        ctk.CTkLabel(sidebar, text="MENU", font=("Arial", 20, "bold")).pack(pady=20)

        self.btn_user = ctk.CTkButton(sidebar, text="👥 User Management", command=self.show_user_management, width=180)
        self.btn_status = ctk.CTkButton(sidebar, text="⚙ System Check", command=self.show_status, width=180)
        self.btn_sensors = ctk.CTkButton(sidebar, text="📡 Sensors", command=self.show_sensors, width=180)

        self.btn_user.pack(pady=5)
        self.btn_status.pack(pady=5)
        self.btn_sensors.pack(pady=5)

        return sidebar

    def create_login_frame(self):
        frame = ctk.CTkFrame(self.main_area)
        ctk.CTkLabel(frame, text="Manager Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        self.code_entry = ctk.CTkEntry(frame, placeholder_text="Enter Manager Code")
        self.code_entry.pack(pady=10)
        ctk.CTkButton(frame, text="Login", command=self.authenticate).pack(pady=10)
        return frame

    def authenticate(self):
        if self.code_entry.get().strip() == MANAGER_CODE:
            self.login_frame.destroy()
            self.show_manager_panel()
        else:
            ctk.CTkLabel(self.login_frame, text="Invalid code", text_color="red").pack()

    def show_manager_panel(self):
        self.clear_main_area()
        panel = ctk.CTkFrame(self.main_area)
        panel.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(panel, text="Manager Panel", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)

        # Mostra i 3 pulsanti come prima
        ctk.CTkButton(panel, text="👥 User Management", width=250, command=lambda: self.open_dashboard("user")).pack(pady=10)
        ctk.CTkButton(panel, text="⚙ System Check", width=250, command=lambda: self.open_dashboard("status")).pack(pady=10)
        ctk.CTkButton(panel, text="📡 Sensors", width=250, command=lambda: self.open_dashboard("sensors")).pack(pady=10)

    def open_dashboard(self, section):
        # Sidebar visibile
        self.sidebar.pack(side="left", fill="y")
        # Carica la sezione selezionata
        if section == "user":
            self.show_user_management()
        elif section == "status":
            self.show_status()
        elif section == "sensors":
            self.show_sensors()

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_back_button(self, parent, callback):
        ctk.CTkButton(parent, text="⬅ Back", command=callback).pack(pady=10)

    # ----------------------------- USER MANAGEMENT -----------------------------
    def show_user_management(self):
        self.clear_main_area()
        self.content_frame = ctk.CTkFrame(self.main_area)
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(self.content_frame, text="Select User Type", font=("Arial", 20, "bold")).pack(pady=30)
        ctk.CTkButton(self.content_frame, text="Specialist", width=200, command=self.show_specialist_list).pack(pady=10)
        ctk.CTkButton(self.content_frame, text="Patient", width=200, command=self.show_patient_list).pack(pady=10)

    def show_specialist_list(self):
        self.clear_main_area()
        self.content_frame = ctk.CTkFrame(self.main_area)
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        names = [f"Dr. {n}" for n in random.sample(["Bianchi", "Rossi", "Verdi", "Neri", "Costa", "Fontana", "Gallo"], 5)]
        self.create_user_list_ui("Specialist List", names, self.show_user_management)

    def show_patient_list(self):
        self.clear_main_area()
        self.content_frame = ctk.CTkFrame(self.main_area)
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        names = [f"{n} {c}" for n, c in zip(random.sample(["Giulia", "Marco", "Luca", "Anna", "Simone"], 5),
                                            random.sample(["Rossi", "Bianchi", "Neri", "Gialli", "Blu"], 5))]

        self.create_user_list_ui("Patient List", names, self.show_user_management)

    def create_user_list_ui(self, title, names, back_callback):
        ctk.CTkLabel(self.content_frame, text=title, font=("Arial", 20, "bold")).pack(pady=20)
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(pady=10)
        for name in names:
            ctk.CTkLabel(list_frame, text=name).pack(pady=2)

        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="➕ Add New User", width=160).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="🗑 Delete User", width=160, fg_color="red").pack(side="left", padx=10)
        self.show_back_button(self.content_frame, back_callback)

    # ----------------------------- SENSORS -----------------------------
    def show_sensors(self):
        self.clear_main_area()
        self.content_frame = ctk.CTkFrame(self.main_area)
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(self.content_frame, text="Sensor List", font=("Arial", 20, "bold")).pack(pady=20)

        self.sensor_ids = [random.randint(1000, 9999) for _ in range(8)]
        self.sensor_labels = []

        self.sensor_list_frame = ctk.CTkFrame(self.content_frame)
        self.sensor_list_frame.pack(pady=10)

        for sensor_id in self.sensor_ids:
            label = ctk.CTkLabel(self.sensor_list_frame, text=f"Sensor ID: {sensor_id}")
            label.pack(pady=2)
            self.sensor_labels.append(label)

        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="➕ Add Sensor", width=160, command=self.add_sensor).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="🗑 Delete Sensor", width=160, fg_color="red", command=self.delete_sensor).pack(side="left", padx=10)

    def add_sensor(self):
        new_id = random.randint(1000, 9999)
        self.sensor_ids.append(new_id)
        label = ctk.CTkLabel(self.sensor_list_frame, text=f"Sensor ID: {new_id}")
        label.pack(pady=2)
        self.sensor_labels.append(label)

    def delete_sensor(self):
        if self.sensor_ids:
            self.sensor_ids.pop()
            label = self.sensor_labels.pop()
            label.destroy()

    # ----------------------------- SYSTEM STATUS CHECK -----------------------------
    def show_status(self):
        self.clear_main_area()
        self.content_frame = ctk.CTkFrame(self.main_area)
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(self.content_frame, text="System Status Check", font=("Arial", 20), text_color="#204080").pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.content_frame, width=400)
        self.progress_bar.pack(pady=30)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.content_frame, text="Initializing...", font=("Arial", 14))
        self.status_label.pack(pady=10)

        ctk.CTkButton(self.content_frame, text="🔄 Update the System", command=self.restart_system_check).pack(pady=10)
        self.show_back_button(self.content_frame, self.back_to_main_menu)

        threading.Thread(target=self.simulate_status_check, daemon=True).start()

    def simulate_status_check(self):
        for i in range(101):
            time.sleep(0.03)
            self.progress_bar.set(i / 100)
            self.status_label.configure(text=f"System Check: {i}%")
        self.status_label.configure(text="System is fully operational ✅", text_color="green")

    def restart_system_check(self):
        threading.Thread(target=self.simulate_status_check, daemon=True).start()

    def back_to_main_menu(self):
        self.content_frame.destroy()
        self.show_main_menu()

# ----------------------------- RUN -----------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ManagerApp()
    app.mainloop()