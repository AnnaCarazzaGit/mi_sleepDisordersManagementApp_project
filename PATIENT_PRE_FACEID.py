import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# ----------------------------- Dati utente simulati -----------------------------
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

from datetime import datetime, timedelta
# Genera una struttura iniziale
def generate_slots_for_doctor(doctor_name, num_days=365):
    today = datetime.today()
    slots = []
    for day in range(num_days):
        date = (today + timedelta(days=day)).strftime("%Y-%m-%d")
        for hour in range(9, 19):  # 09:00 to 18:00
            time_str = f"{hour:02d}:00"
            slots.append(f"{date} {time_str}")
    return slots

# Genera una struttura iniziale
available_slots = {
    "Dr. Bianchi (Family Doctor)": generate_slots_for_doctor("Dr. Bianchi"),
    "Dr.ssa Neri (Psychologist)": generate_slots_for_doctor("Dr.ssa Neri")
}




booked_visits = []

def generate_visit_code():
    return f"VIS{1000 + len(booked_visits)}"

# ----------------------------- Funzioni frame sezioni -----------------------------
import pandas as pd
import numpy as np

def generate_night_data(date):
    """
    Genera dati simulati minuto per minuto per una notte intera.
    """
    minutes = pd.date_range(f"{date} 22:00", periods=480, freq="T")
    return pd.DataFrame({
        "Time": minutes,
        "Heart Rate (bpm)": np.random.normal(60, 5, 480).round(1),
        "Respiratory Rate (breaths/min)": np.random.normal(16, 1.2, 480).round(1),
        "SpO₂ (%)": np.random.normal(97, 0.5, 480).round(1),
        "Skin Temperature (°C)": np.random.normal(36.5, 0.3, 480).round(1),
        "Date": pd.to_datetime(date).date()
    })

def generate_last_7_nights_data():
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.Timedelta(days=6)
    dates = pd.date_range(start=start_date, periods=7, freq="D")
    return pd.concat([generate_night_data(date) for date in dates], ignore_index=True)

def generate_last_month_data():
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.Timedelta(days=29)
    dates = pd.date_range(start=start_date, periods=30, freq="D")
    return pd.concat([generate_night_data(date) for date in dates], ignore_index=True)

def generate_last_6_months_data():
    today = pd.Timestamp.today().normalize()
    start_date = today - pd.Timedelta(days=179)
    dates = pd.date_range(start=start_date, periods=180, freq="D")
    return pd.concat([generate_night_data(date) for date in dates], ignore_index=True)

def compute_daily_averages(df):
    return df.groupby("Date")[[
        "Heart Rate (bpm)",
        "Respiratory Rate (breaths/min)",
        "SpO₂ (%)",
        "Skin Temperature (°C)"
    ]].mean().reset_index()



def get_stats_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="📊 Statistics and Diagrams", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # Parametri e intervalli temporali
    parameters = [
        "Total Sleep Time",
        "Time in bed vs time asleep",
        "Sleep Stages",
        "Heart Rate",
        "Respiratory Rate",
        "Oxygen Saturation (SpO₂)",
        "Snoring Alert",
        "Body Position",
        "Skin Temperature" 
    ]

    timeframes = [
        "One night",
        "Last 7 Days",
        "Last Month",
        "Last 6 Months"
    ]

    # Selezione parametro
    ctk.CTkLabel(frame, text="Select Parameter").pack(pady=(10, 5))
    param_var = ctk.StringVar(value=parameters[0])
    param_menu = ctk.CTkOptionMenu(frame, values=parameters, variable=param_var)
    param_menu.pack()

    # Selezione intervallo temporale
    ctk.CTkLabel(frame, text="Select Timeframe").pack(pady=(20, 5))
    time_var = ctk.StringVar(value=timeframes[0])
    time_menu = ctk.CTkOptionMenu(frame, values=timeframes, variable=time_var)
    time_menu.pack()

    import matplotlib.pyplot as plt

    def open_graph_window():
        selected_param = param_var.get()
        selected_time = time_var.get()

        #graph_window = ctk.CTkToplevel()
        #graph_window.title(f"{selected_param} - {selected_time}")
        #graph_window.geometry("800x500")

        #ctk.CTkLabel(graph_window, text=f"{selected_param} ({selected_time})",
                    #font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        if selected_time == "Last 7 Days":
            data = generate_last_7_nights_data()

            if selected_param == "Heart Rate":
                plt.plot(data["Time"], data["Heart Rate (bpm)"])
                plt.ylabel("bpm")

            elif selected_param == "Respiratory Rate":
                plt.plot(data["Time"], data["Respiratory Rate (breaths/min)"])
                plt.ylabel("breaths/min")

            elif selected_param == "SpO₂":
                plt.plot(data["Time"], data["SpO₂ (%)"])
                plt.ylabel("%")

            elif selected_param == "Skin Temperature":
                plt.plot(data["Time"], data["Skin Temperature (°C)"])
                plt.ylabel("°C")


            plt.xlabel("Data e ora")
            plt.title(f"{selected_param} - Last 7 Days")

        elif selected_time == "Last Month":
            data = compute_daily_averages(generate_last_month_data())

            if selected_param == "Heart Rate":
                plt.plot(data["Date"], data["Heart Rate (bpm)"])
                plt.ylabel("bpm")

            elif selected_param == "Respiratory Rate":
                plt.plot(data["Date"], data["Respiratory Rate (breaths/min)"])
                plt.ylabel("breaths/min")

            elif selected_param == "SpO₂":
                plt.plot(data["Date"], data["SpO₂ (%)"])
                plt.ylabel("%")

            elif selected_param == "Skin Temperature":
                plt.plot(data["Date"], data["Skin Temperature (°C)"])
                plt.ylabel("°C")

            else:
                ctk.CTkLabel(graph_window, text="⚠ Parametro non valido").pack()
                return

            plt.xlabel("Data")
            plt.title(f"{selected_param} - Last Month")

        elif selected_time == "Last 6 Months":
            data = compute_daily_averages(generate_last_6_months_data())

            if selected_param == "Heart Rate":
                plt.figure(figsize=(10, 4))
                plt.plot(data["Date"], data["Heart Rate (bpm)"])
                plt.ylabel("bpm")

            elif selected_param == "Respiratory Rate":
                plt.plot(data["Date"], data["Respiratory Rate (breaths/min)"])
                plt.ylabel("breaths/min")

            elif selected_param == "Oxigen Saturation (SpO₂)":
                plt.plot(data["Date"], data["SpO₂ (%)"])
                plt.ylabel("%")

            elif selected_param == "Skin Temperature":
                plt.plot(data["Date"], data["Skin Temperature (°C)"])
                plt.ylabel("°C")



        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    ctk.CTkButton(frame, text="Show Diagram", command=open_graph_window).pack(pady=30)

    return frame
import json
import os


import re
def update_patient_data(patient_data, phone=None, residency=None, domicile=None, email=None):
    if phone:
        patient_data["phone"] = phone
    if residency:
        patient_data["residency"] = residency
    if domicile:
        patient_data["domicile"] = domicile
    if email:
        patient_data["email"] = email

def get_profile_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="👤 Profile", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # Frame interno per la tabella
    table = ctk.CTkFrame(frame)
    table.pack(pady=10, padx=20)

    # Variabili modificabili
    phone_var = ctk.StringVar(value=patient_data["phone"])
    residency_var = ctk.StringVar(value=patient_data["residency"])
    domicile_var = ctk.StringVar(value=patient_data["domicile"])
    email_var = ctk.StringVar(value=patient_data["email"])

    # Dizionario dei campi statici
    static_fields = {
        "Name and Surname": patient_data["name"],
        "Fiscal Code": patient_data["fiscal_code"],
        "Birthdate": patient_data["birthdate"],
        "Gender": patient_data["gender"],
        "Nationality": patient_data["nationality"],
        "Family Doctor": patient_data["family_doctor"],
        "Psychologist": patient_data["psychologist"],
        "Privacy Consent": patient_data["privacy_consent"]
    }

    # Righe della tabella
    row = 0
    for label, value in static_fields.items():
        ctk.CTkLabel(table, text=label + ":", anchor="w", width=180).grid(row=row, column=0, sticky="w", padx=4, pady=4)
        ctk.CTkLabel(table, text=value, anchor="w").grid(row=row, column=1, sticky="w", padx=4, pady=4)
        row += 1

    # Campi modificabili inizialmente come etichette
    editable_vars = {
        "Residency": residency_var,
        "Domicile": domicile_var,
        "Phone Number": phone_var,
        "E-mail": email_var
    }

    label_refs = {}  # Per tenere traccia delle etichette da rimuovere
    entry_refs = {}  # Per gestire le entry attivabili

    for label, var in editable_vars.items():
        ctk.CTkLabel(table, text=label + ":", anchor="w", width=180).grid(row=row, column=0, sticky="w", padx=4, pady=4)
        lbl = ctk.CTkLabel(table, text=var.get(), anchor="w")
        lbl.grid(row=row, column=1, sticky="w", padx=4, pady=4)
        label_refs[label] = lbl  # Salva l'etichetta per poi sostituirla
        row += 1

    # Pulsante Edit Info → sostituisce le etichette con entry
    def enable_editing():
        for i, (label, var) in enumerate(editable_vars.items()):
            # Rimuove la label statica
            label_refs[label].destroy()
            # Inserisce la entry al suo posto
            entry = ctk.CTkEntry(table, textvariable=var, width=300)
            entry.grid(row=len(static_fields) + i, column=1, sticky="w", padx=4, pady=4)
            entry_refs[label] = entry
        edit_btn.configure(state="disabled")  # Disattiva il pulsante Edit

    # Salva le modifiche
    def save_changes():
        update_patient_data(
            patient_data,
            phone=phone_var.get(),
            residency=residency_var.get(),
            domicile=domicile_var.get(),
            email=email_var.get()
        )
        ctk.CTkLabel(frame, text="✅ Profile updated!", text_color="green").pack(pady=10)

    # Pulsanti
    edit_btn = ctk.CTkButton(frame, text="Edit Info", command=enable_editing)
    edit_btn.pack(pady=(20, 10))

    save_btn = ctk.CTkButton(frame, text="Save Changes", command=save_changes)
    save_btn.pack(pady=(0, 20))

    return frame




def get_helpdesk_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="🆘 Help Desk", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # Area chat
    chat_display = ctk.CTkTextbox(frame, width=600, height=300, state="disabled")
    chat_display.pack(padx=10, pady=10)

    # Barra di inserimento e invio
    input_frame = ctk.CTkFrame(frame, fg_color="transparent")
    input_frame.pack(fill="x", padx=10, pady=10)

    user_input = ctk.CTkEntry(input_frame, placeholder_text="Chat with an operator...", width=400)
    user_input.pack(side="left", padx=5)

    def send_message():
        msg = user_input.get().strip()
        if msg:
            chat_display.configure(state="normal")
            chat_display.insert("end", f"You: {msg}\n")
            chat_display.insert("end", f"Operator:Thanks for contacting us. We will get back to you as soon as possible.\n\n")
            chat_display.configure(state="disabled")
            user_input.delete(0, "end")

    send_btn = ctk.CTkButton(input_frame, text="Send", command=send_message)
    send_btn.pack(side="right", padx=5)

    return frame


def check_password_constraints(password, old_password=None):
    errors = []

    if len(password) < 10:
        errors.append("La password deve contenere almeno 10 caratteri.")
    if not re.search(r"[A-Z]", password):
        errors.append("La password deve contenere almeno una lettera maiuscola.")
    if not re.search(r"[!@#$%^&*()_\-+=\[\]{}|\\:;\"'<>,.?/]", password):
        errors.append("La password deve contenere almeno un carattere speciale.")
    if not re.search(r"\d", password):
        errors.append("La password deve contenere almeno un numero.")
    if old_password and password == old_password:
        errors.append("La nuova password deve essere diversa dalla precedente.")

    return errors  # una lista di stringhe con gli errori (vuota se valida)



import os
import json
from datetime import date
import customtkinter as ctk

def get_diary_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    today_str = date.today().strftime("%Y-%m-%d")
    diary_file = "diary_answers.json"

    ctk.CTkLabel(frame, text=f"📔 Today Diary – {today_str}",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    questions = [
        "1️⃣ Difficulty falling asleep (0=very satisfied, 4=very dissatisfied)",
        "2️⃣ Difficulty staying asleep (0=very satisfied, 4=very dissatisfied)",
        "3️⃣ Problem waking up too early (0=very satisfied, 4=very dissatisfied)",
        "4️⃣ Satisfaction with sleep pattern (0=very satisfied, 4=very dissatisfied)",
        "5️⃣ Interference with daily functioning (0=not at all, 4=very much)",
        "6️⃣ Noticeability to others (0=not at all, 4=very much)",
        "7️⃣ Worry about sleep (0=not at all, 4=very much)"
    ]

    # Carica risposte salvate
    saved_data = {}
    if os.path.exists(diary_file):
        with open(diary_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

    already_filled = today_str in saved_data
    FORCE_EDIT_TODAY = True  # True per test, rimettere False in produzione
    previous_answers = saved_data.get(today_str, {})

    sliders = {}
    containers = []
    pages = [[], []]
    current_page = [0]

    content_frame = ctk.CTkFrame(frame)
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    confirmation_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14), text_color="green")
    confirmation_label.pack(pady=(5, 5))

    for i, question in enumerate(questions):
        qid = f"q{i+1}"

        container = ctk.CTkFrame(content_frame, fg_color="#1e1e1e", corner_radius=12)
        container.pack(pady=10, padx=40, fill="x")
        pages[i // 4].append(container)
        containers.append((qid, container))

        label = ctk.CTkLabel(container, text=question, anchor="w", justify="left", wraplength=1000)
        label.pack(fill="x", padx=20, pady=(10, 5))

        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x", padx=15, pady=(0, 10))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=0)

        slider = ctk.CTkSlider(row_frame, from_=0, to=4, number_of_steps=4)
        slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        value_label = ctk.CTkLabel(row_frame, text="Nan", width=25, anchor="e")
        value_label.grid(row=0, column=1)

        def update_label(slider=slider, label=value_label):
            label.configure(text=str(round(slider.get())))

        slider.configure(command=lambda val, s=slider, l=value_label: update_label(s, l))

        if qid in previous_answers and not FORCE_EDIT_TODAY:
            slider.set(previous_answers[qid])
            slider.configure(state="disabled")
            value_label.configure(text=str(previous_answers[qid]))

        sliders[qid] = slider

    def show_page(index):
        for container in pages[0] + pages[1]:
            container.pack_forget()
        for widget in pages[index]:
            widget.pack(pady=10, padx=40, fill="x")
        current_page[0] = index

        if index == 0:
            arrow_button.configure(text="⏩", command=next_page)
        else:
            arrow_button.configure(text="⏪", command=prev_page)

    def next_page():
        show_page(1)

    def prev_page():
        show_page(0)

    def save_answers():
        missing = []
        responses = {}

        for qid, slider in sliders.items():
            value = slider.get()
            if str(value) == "Nan":
                missing.append(qid)
            else:
                responses[qid] = round(value)

        if missing:
            confirmation_label.configure(text="⚠ Required field not answered", text_color="red")
            for qid, container in containers:
                if qid in missing:
                    container.configure(border_color="red", border_width=2)
                else:
                    container.configure(border_color="#1e1e1e", border_width=0)
            return

        # Salva risposte
        saved_data[today_str] = responses
        with open(diary_file, "w", encoding="utf-8") as f:
            json.dump(saved_data, f, indent=2, ensure_ascii=False)

        for slider in sliders.values():
            slider.configure(state="disabled")

        confirmation_label.configure(text="✅ Risposte salvate e bloccate!", text_color="green")
        save_button.configure(state="disabled")

    # --- Bottoni in fondo ---
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(fill="x", pady=10, padx=10)

    save_button = ctk.CTkButton(
        button_frame,
        text="💾 Save Answers",
        command=save_answers,
        fg_color="#003366",
        hover_color="#005599",
        text_color="white",
        width=140,
        height=36,
        font=ctk.CTkFont(weight="bold")
    )
    save_button.pack(side="left", padx=10)

    arrow_button = ctk.CTkButton(
        button_frame,
        text="⏩",
        command=next_page,
        width=60,
        height=36,
        fg_color="#e0e0e0",
        hover_color="#cccccc",
        text_color="#003366",
        font=ctk.CTkFont(weight="bold")
    )
    arrow_button.pack(side="right", padx=10)

    show_page(0)
    return frame





def get_visits_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="📅 Visits", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    def refresh_visits_list():
        for widget in visits_list_frame.winfo_children():
            widget.destroy()

        if not booked_visits:
            ctk.CTkLabel(visits_list_frame, text="No visits booked yet.").pack(pady=5)
            return

        for visit in booked_visits:
            text = f"{visit['date']} – {visit['doctor']} (Code: {visit['code']})"
            visit_frame = ctk.CTkFrame(visits_list_frame)
            visit_frame.pack(pady=5, fill="x", padx=10)

            ctk.CTkLabel(visit_frame, text=text).pack(side="left", padx=10)

            def modify_callback(v=visit):
                modify_visit(v)

            def delete_callback(v=visit):
                booked_visits.remove(v)
                refresh_visits_list()
                messagebox.showinfo("Deleted", "Visit deleted successfully.")

            ctk.CTkButton(visit_frame, text="Modify", command=modify_callback, width=80).pack(side="right", padx=5)
            ctk.CTkButton(visit_frame, text="Delete", command=delete_callback, width=80, fg_color="red").pack(side="right", padx=5)

    from tkcalendar import Calendar

    def book_new_visit():
        popup = ctk.CTkToplevel()
        popup.title("Book New Visit")
        popup.geometry("500x500")

        ctk.CTkLabel(popup, text="Select Practitioner").pack(pady=10)
        doctor_combo = ctk.CTkOptionMenu(popup, values=list(available_slots.keys()))
        doctor_combo.pack(pady=5)

        calendar_frame = ctk.CTkFrame(popup)
        calendar_frame.pack(pady=10)

        time_var = ctk.StringVar(value="")
        calendar_widget = None

        def update_calendar():
            nonlocal calendar_widget
            for widget in calendar_frame.winfo_children():
                widget.destroy()

            selected_doctor = doctor_combo.get()
            slots = available_slots.get(selected_doctor, [])

            valid_dates = {s.split()[0] for s in slots}

            #def custom_date_validation(date_str):
                #return date_str in valid_dates

            calendar_widget = Calendar(
                calendar_frame,
                selectmode='day',
                date_pattern='yyyy-mm-dd',
                showweeknumbers=False
            )
            calendar_widget.pack()

        def proceed_to_time_selection():
            if not calendar_widget:
                messagebox.showerror("Error", "Please select a practitioner and wait for the calendar.")
                return

            selected_date = calendar_widget.get_date()
            selected_doctor = doctor_combo.get()
            slots = available_slots[selected_doctor]

            day_slots = [s for s in slots if s.startswith(selected_date)]
            if not day_slots:
                messagebox.showinfo("No Slots", "No time slots available on this date.")
                return

            # Finestra selezione orario
            time_popup = ctk.CTkToplevel()
            time_popup.title("Select Time")
            time_popup.geometry("400x200")

            times = [s.split()[1] for s in day_slots]
            time_var.set(times[0])
            ctk.CTkLabel(time_popup, text="Select Time Slot").pack(pady=10)
            ctk.CTkOptionMenu(time_popup, values=times, variable=time_var).pack(pady=10)

            def confirm_booking():
                final_slot = f"{selected_date} {time_var.get()}"
                available_slots[selected_doctor].remove(final_slot)
                code = generate_visit_code()
                booked_visits.append({
                    "doctor": selected_doctor,
                    "date": final_slot,
                    "code": code
                })
                time_popup.destroy()
                popup.destroy()
                refresh_visits_list()
                messagebox.showinfo("Booked", f"Visit booked.\nCode: {code}")

            ctk.CTkButton(time_popup, text="Book", command=confirm_booking).pack(pady=20)

        doctor_combo.configure(command=lambda _: update_calendar())
        ctk.CTkButton(popup, text="Next", command=proceed_to_time_selection).pack(pady=20)


    def modify_visit(visit):
        slots = available_slots.get(visit["doctor"], [])
        if not slots:
            messagebox.showinfo("No Availability", "No slots available.")
            return

        popup = ctk.CTkToplevel()
        popup.title("Modify Visit")
        popup.geometry("400x200")

        slot_var = ctk.StringVar(value=slots[0])
        ctk.CTkLabel(popup, text="Select new slot").pack(pady=10)
        ctk.CTkOptionMenu(popup, values=slots, variable=slot_var).pack()

        def confirm_modification():
            new_slot = slot_var.get()
            old_slot = visit["date"]
            available_slots[visit["doctor"]].append(old_slot)
            available_slots[visit["doctor"]].remove(new_slot)
            visit["date"] = new_slot
            popup.destroy()
            refresh_visits_list()
            messagebox.showinfo("Updated", "Visit updated successfully.")

        ctk.CTkButton(popup, text="Update", command=confirm_modification).pack(pady=20)

    ctk.CTkLabel(frame, text="My Visits", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
    visits_list_frame = ctk.CTkFrame(frame)
    visits_list_frame.pack(pady=5, fill="x")
    refresh_visits_list()

    ctk.CTkButton(frame, text="Book a New Visit", command=book_new_visit).pack(pady=20)
    return frame

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

import customtkinter as ctk

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
        ctk.CTkButton(self, text="Reset Password", command=self.check_password_constraints, fg_color="gray").pack(pady=10)



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

    def check_password_constraints(self):
        id_code = self.id_entry.get().strip()
        user = users_db.get(id_code)

        if not user:
            messagebox.showerror("Errore", "Inserisci prima un ID Code valido.")
            return

        # Finestra popup per nuova password
        popup = ctk.CTkToplevel(self)
        popup.title("Reset Password")
        popup.geometry("400x250")

        ctk.CTkLabel(popup, text="Nuova Password", font=ctk.CTkFont(size=16)).pack(pady=10)
        new_pw_entry = ctk.CTkEntry(popup, placeholder_text="Nuova Password", show="*")
        new_pw_entry.pack(pady=5)

        def validate_and_save():
            new_password = new_pw_entry.get().strip()
            old_password = user["password"]

            errors = check_password_constraints(new_password, old_password)

            if errors:
                messagebox.showerror("Errore password", "\n".join(errors))
            else:
                user["password"] = new_password
                user["attempts"] = 0
                messagebox.showinfo("Successo", "Password aggiornata con successo!")
                popup.destroy()

        ctk.CTkButton(popup, text="Conferma", command=validate_and_save).pack(pady=15)

import customtkinter as ctk

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Patient App")
        self.geometry("1000x700")
        self.configure(fg_color="#f2f4f7")

        # Mostra solo il login all'avvio
        self.login_frame = LoginFrame(self, self.after_login)
        self.login_frame.pack(expand=True, fill="both")

    def after_login(self):
        self.login_frame.destroy()

        # Mostra solo un frame centrale con i 4 pulsanti
        self.menu_frame = ctk.CTkFrame(self, fg_color="#ffffff")
        self.menu_frame.pack(expand=True)

        ctk.CTkLabel(
          self.menu_frame,
          text="Welcome to E\u00b3A\u00b2S",  # E³A²S in Unicode
          font=ctk.CTkFont(size=24, weight="bold"),
          text_color="#003366"  # blu scuro elegante (puoi cambiare colore)
        ).pack(pady=20)
 

        ctk.CTkButton(self.menu_frame, text="Profile", width=200, command=self.activate_profile).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Visits", width=200, command=self.activate_visits).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="Statistics and Diagrams", width=200, command=self.activate_stats).pack(pady=10)
        ctk.CTkButton(self.menu_frame, text="My Diary", width=200, command=self.activate_diary).pack(pady=10)

    def setup_sidebar(self):
        # Costruisci sidebar e main_content solo al primo click
        self.menu_frame.destroy()

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#ffffff")
        self.sidebar.pack(side="left", fill="y")

        self.main_content = ctk.CTkFrame(self, corner_radius=10, fg_color="#fdfdfd")
        self.main_content.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        self.profile_btn = ctk.CTkButton(self.sidebar, text="Profile", command=self.show_profile)
        self.visits_btn = ctk.CTkButton(self.sidebar, text="Visits", command=self.show_visits)
        self.diary_btn = ctk.CTkButton(self.sidebar, text="My Diary", command=self.show_diary)
        self.stats_btn = ctk.CTkButton(self.sidebar, text="Statistics and Diagram", command=self.show_stats)
        self.help_btn = ctk.CTkButton(
          self.sidebar,
          text="Help Desk",
          command=self.show_helpdesk,
          fg_color="#003366",          # sfondo blu
          hover_color="#005599",       # colore al passaggio del mouse
          text_color="white"           # testo chiaro
        )


        for btn in [self.profile_btn, self.visits_btn, self.diary_btn, self.stats_btn, self.help_btn]:
            btn.pack(pady=20, padx=10)

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
        frame = get_profile_frame(self.main_content)
        frame.pack(fill="both", expand=True)

    def show_stats(self):
        self.clear_main_content()
        frame = get_stats_frame(self.main_content)
        frame.pack(fill="both", expand=True)

    def show_visits(self):
        self.clear_main_content()
        frame = get_visits_frame(self.main_content)
        frame.pack(fill="both", expand=True)

    def show_diary(self):
        self.clear_main_content()
        frame = get_diary_frame(self.main_content)
        frame.pack(fill="both", expand=True)

    def show_helpdesk(self):
        self.clear_main_content()
        frame = get_helpdesk_frame(self.main_content)
        frame.pack(fill="both", expand=True)
    


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MainApp()
    app.mainloop()