import customtkinter as ctk
from datetime import datetime, date, timedelta
from tkcalendar import Calendar
import os
import json
import re
from ui.style_ctk import *
from ui.specialist.sensor_data_page import SensorDataPage
import sqlite3


def load_users_from_db():
    conn = sqlite3.connect("insomnia_management.db")
    cursor = conn.cursor()

    users_db = {}

    cursor.execute("""
        SELECT U.Id, U.Password, P.Face_Id, PI.Privacy_Consent
        FROM USER U
        JOIN PATIENT P ON U.Id = P.Patient_Id
        JOIN Personal_Info PI ON U.Id = PI.User_Id
    """)
    for row in cursor.fetchall():
        user_id, password, face_id_value, privacy_consent = row
        users_db[user_id] = {
            "password": password,
            "face_id": face_id_value, 
            "consent": str(privacy_consent).strip().lower() == "yes", 
            "attempts": 0
        }

    conn.close()
    return users_db

users_db = load_users_from_db()


def get_patient_info(patient_id):
    conn = sqlite3.connect("insomnia_management.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            PI.Name, PI.Surname, PI.User_Id, PI.Birthdate, PI.Gender, PI.Residency, PI.Domicile, PI.Nationality,
            PI.Phone_Number, PI.Email, PI.Privacy_Consent
        FROM PATIENT P
        LEFT JOIN Personal_Info PI ON P.Patient_Id = PI.User_Id
        WHERE P.Patient_Id = ?
    """, (patient_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    patient_info = {
        "name": row[0],
        "surname": row[1],
        "fiscal_code": row[2],
        "birthdate": row[3],
        "gender": row[4],
        "residency": row[5],
        "domicile": row[6],
        "nationality": row[7],
        "phone": row[8],
        "email": row[9],
        "privacy_consent": row[10],
    }
    return patient_info


# VISIT

WEEKDAY_MAP = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6,
}


def parse_visiting_hours(visiting_hours_str):
    """
    Parsing semplice di stringhe come 'Mon-Fri 09:00-12:00'
    Ritorna tuple (days_list, start_hour, end_hour)
    """
    days_part, hours_part = visiting_hours_str.split()
    if "-" in days_part:
        start_day, end_day = days_part.split("-")
        start_idx = WEEKDAY_MAP[start_day]
        end_idx = WEEKDAY_MAP[end_day]
        if end_idx >= start_idx:
            days = list(range(start_idx, end_idx + 1))
        else:
            
            days = list(range(start_idx, 7)) + list(range(0, end_idx + 1))
    else:
        
        days = [WEEKDAY_MAP[days_part]]

    start_hour_str, end_hour_str = hours_part.split("-")
    start_hour = int(start_hour_str.split(":")[0])
    end_hour = int(end_hour_str.split(":")[0])

    return days, start_hour, end_hour


def generate_slots(visiting_hours_str, num_days=30):
    """
    Generate time slots from today onward for num_days based on visiting_hours_str. 
    One slot per hour from start_hour to end_hour - 1.
    """
    days, start_hour, end_hour = parse_visiting_hours(visiting_hours_str)
    today = datetime.today()
    slots = []

    for day_offset in range(num_days):
        current_date = today + timedelta(days=day_offset)
        if current_date.weekday() in days:
            date_str = current_date.strftime("%Y-%m-%d")
            for hour in range(start_hour, end_hour):
                for minute in [0, 15, 30, 45]:
                    slot = f"{date_str} {hour:02d}:{minute:02d}"
                    slots.append(slot)

    return slots


def load_doctors_and_slots_from_db(conn, num_days=30):
    cursor = conn.cursor()
    available_slots = {}

    cursor.execute("""
        SELECT FD.Family_Doctor_Id, PI.Name, PI.Surname, FD.Visiting_Hours
        FROM FAMILY_DOCTOR FD
        JOIN Personal_Info PI ON FD.Family_Doctor_Id = PI.User_Id
    """)
    for doc_id, name, surname, visiting_hours in cursor.fetchall():
        full_name = f"Dr. {name} {surname} (Family Doctor)"
        slots = generate_slots(visiting_hours, num_days=num_days)
        available_slots[full_name] = slots

        slots = generate_slots(visiting_hours, num_days=num_days)
        available_slots[name] = slots

    cursor.execute("""
        SELECT PS.Psychologist_Id, PI.Name, PI.Surname, PS.Visiting_Hours
        FROM PSYCHOLOGIST PS
        JOIN Personal_Info PI ON PS.Psychologist_Id = PI.User_Id
    """)
    for doc_id, name, surname, visiting_hours in cursor.fetchall():
        full_name = f"Dr. {name} {surname} (Psychologist)"
        slots = generate_slots(visiting_hours, num_days=num_days)
        available_slots[full_name] = slots

    return available_slots

conn = sqlite3.connect('insomnia_management.db')
available_slots = load_doctors_and_slots_from_db(conn, num_days=60) 

booked_visits = []
booked_consults = []


def load_booked_visits_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Code, Patient_Id, Family_Doctor_Id, Date, Hour FROM VISIT")
    visits = cursor.fetchall()
    return visits


def load_booked_consults_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Code, Patient_Id, Psychologist_Id, Date, Hour FROM CONSULT")
    consults = cursor.fetchall()
    return consults
    

def build_doctor_id_name_maps(conn):
    cursor = conn.cursor()
    doctor_id_to_name = {}
    doctor_name_to_id = {}

    cursor.execute("""
        SELECT FD.Family_Doctor_Id, PI.Name, PI.Surname 
        FROM FAMILY_DOCTOR FD 
        JOIN Personal_Info PI ON FD.Family_Doctor_Id = PI.User_Id
    """)
    for doc_id, name, surname in cursor.fetchall():
        display_name = f"Dr. {name} {surname} (Family Doctor)"

        doctor_id_to_name[doc_id] = name
        doctor_name_to_id[name] = doc_id

    cursor.execute("""
        SELECT PS.Psychologist_Id, PI.Name, PI.Surname 
        FROM PSYCHOLOGIST PS 
        JOIN Personal_Info PI ON PS.Psychologist_Id = PI.User_Id
    """)
    for doc_id, name, surname in cursor.fetchall():
        display_name = f"Dr. {name} {surname} (Psychologist)"

        doctor_id_to_name[doc_id] = display_name
        doctor_name_to_id[display_name] = doc_id


    return doctor_id_to_name, doctor_name_to_id

doctor_id_to_name, doctor_name_to_id = build_doctor_id_name_maps(conn)
booked_visits_db = load_booked_visits_from_db(conn)

for code, patient_id, doctor_id, date, time_ in booked_visits_db:
    doctor_name = doctor_id_to_name.get(doctor_id)
    if doctor_name and f"{date} {time_}" in available_slots.get(doctor_name, []):
        available_slots[doctor_name].remove(f"{date} {time_}")
    booked_visits.append({
        "code": code,
        "patient_id": patient_id,
        "doctor": doctor_name,
        "date": f"{date} {time_}"
    })

booked_consults_db = load_booked_consults_from_db(conn)

for code, patient_id, doctor_id, date, time_ in booked_consults_db:
    doctor_name = doctor_id_to_name.get(doctor_id)
    if doctor_name and f"{date} {time_}" in available_slots.get(doctor_name, []):
        available_slots[doctor_name].remove(f"{date} {time_}")
    booked_consults.append({
        "code": code,
        "patient_id": patient_id,
        "doctor": doctor_name,
        "date": f"{date} {time_}"
    })


def generate_visit_code(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Code FROM VISIT")
    existing_codes = {row[0] for row in cursor.fetchall()}

    base = 1000
    while True:
        code = f"VIS{base}"
        if code not in existing_codes:
            return code
        base += 1


def generate_consult_code(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Code FROM CONSULT")
    existing_codes = {row[0] for row in cursor.fetchall()}

    base = 1000
    while True:
        code = f"CON{base}"
        if code not in existing_codes:
            return code
        base += 1


def get_doctors_for_patient(patient_id):
    conn = sqlite3.connect("insomnia_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Doctor_Id, Psychologist_Id
        FROM Patient_Doctor_Psychologist
        WHERE Patient_Id = ?
    """, (patient_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return []

    doctor_id, psychologist_id = row
    associated = []

    for doc_id, role in [(doctor_id, "Family Doctor"), (psychologist_id, "Psychologist")]:
        if doc_id:
            cursor.execute("""
                SELECT Name, Surname FROM Personal_Info WHERE User_Id = ?
            """, (doc_id,))
            info = cursor.fetchone()
            if info:
                full_name = f"Dr. {info[0]} {info[1]} ({role})"
                associated.append(full_name)
                
                doctor_name_to_id[full_name] = doc_id
                doctor_id_to_name[doc_id] = full_name

    conn.close()
    return associated


def insert_consult_to_db(conn, code, patient_id, psychologist_id, date, time_):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO CONSULT (Code, Patient_Id, Psychologist_Id, Date, Hour) VALUES (?, ?, ?, ?, ?)",
                   (code, patient_id, psychologist_id, date, time_))
    conn.commit()

    
# UPDATE DATE 

def update_all_patient_data(user_id, phone=None, residency=None, domicile=None, email=None, password=None):
    
    if password:
        conn = sqlite3.connect("insomnia_management.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE USER SET Password = ? WHERE Id = ?", (password, user_id))
        conn.commit()
        conn.close()
        users_db[user_id]["password"] = password  

    updates = {}
    if phone is not None:
        updates["Phone_Number"] = phone
    if residency is not None:
        updates["Residency"] = residency
    if domicile is not None:
        updates["Domicile"] = domicile
    if email is not None:
        updates["Email"] = email

    if updates:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(user_id)

        conn = sqlite3.connect("insomnia_management.db")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Personal_Info SET {set_clause} WHERE User_Id = ?", values)
        conn.commit()
        conn.close()

def get_profile_frame(parent_frame, patient_data, user_id):
    frame = create_frame(parent_frame, width=950, height=600)
    create_label(frame, text="Profile", size=FONT_SIZES["large"]).pack(pady=20)

    table = create_frame(frame, width=700)
    table.pack(pady=10, padx=20)

    phone_var = ctk.StringVar(value=patient_data["phone"])
    residency_var = ctk.StringVar(value=patient_data["residency"])
    domicile_var = ctk.StringVar(value=patient_data["domicile"])
    email_var = ctk.StringVar(value=patient_data["email"])
    password_var = ctk.StringVar(value=users_db[user_id]["password"])

    table.grid_columnconfigure(0, weight=0, minsize=200)
    table.grid_columnconfigure(1, weight=1, minsize=400)

    static_fields = {
        "Name": patient_data["name"],
        "Surname": patient_data["surname"],
        "Fiscal Code": patient_data["fiscal_code"],
        "Birthdate": patient_data["birthdate"],
        "Gender": patient_data["gender"],
        "Nationality": patient_data["nationality"],
        "Privacy Consent": patient_data["privacy_consent"]
    }

    row = 0
    for label, value in static_fields.items():
        create_label(table, text=f"{label}:", size=FONT_SIZES["medium"], width=20).grid(
            row=row, column=0, sticky="w", padx=4, pady=4)
        create_label(table, text=value, size=FONT_SIZES["medium"], width=40).grid(
            row=row, column=1, sticky="w", padx=4, pady=4)
        row += 1

    editable_vars = {
        "Residency": residency_var,
        "Domicile": domicile_var,
        "Phone Number": phone_var,
        "E-mail": email_var,
        "New Password": password_var
    }

    label_refs = {}
    entry_refs = {}

    for label, var in editable_vars.items():
        create_label(table, text=f"{label}:", size=FONT_SIZES["medium"], width=20).grid(
            row=row, column=0, sticky="w", padx=4, pady=4)

        displayed_value = "**********" if label == "New Password" else var.get()
        lbl = create_label(table, text=displayed_value, size=FONT_SIZES["medium"], width=40)
        lbl.grid(row=row, column=1, sticky="w", padx=4, pady=4)
        label_refs[label] = lbl
        row += 1

    def save_changes():
        new_pw = password_var.get().strip()
        old_pw = users_db[user_id]["password"]

        if new_pw and new_pw != old_pw:
            errors = check_password_constraints(new_pw, old_pw)
            if errors:
                show_custom_error(frame, title="Invalid Password", message="\n".join(errors))
                return
        elif new_pw == old_pw:
            new_pw = None
       
        def confirm_save():
            if new_pw:
                patient_data["password"] = new_pw

            update_all_patient_data(
                user_id,
                phone=phone_var.get(),
                residency=residency_var.get(),
                domicile=domicile_var.get(),
                email=email_var.get(),
                password=new_pw if new_pw else None
            )

            if new_pw:
                users_db[user_id]["password"] = new_pw

            patient_data["phone"] = phone_var.get()
            patient_data["residency"] = residency_var.get()
            patient_data["domicile"] = domicile_var.get()
            patient_data["email"] = email_var.get()

            for i, (label, var) in enumerate(editable_vars.items()):
                entry_refs[label].destroy()
                updated_value = "******" if label == "New Password" else var.get()
                lbl = create_label(table, text=updated_value, size=FONT_SIZES["medium"], width=40)
                lbl.grid(row=len(static_fields) + i, column=1, sticky="w", padx=4, pady=4)
                label_refs[label] = lbl

            entry_refs.clear()
            edit_btn.pack(pady=(20, 10))
            save_btn.pack_forget()

            create_label(frame, text="✔ Profile updated!", size=FONT_SIZES["medium"], color="green").pack(pady=10)

        show_custom_confirm(
            master=frame,
            title="Confirm Changes",
            message="Are you sure you want to save these changes?",
            on_yes=confirm_save
        )

    save_btn = create_secondary_button(frame, text="Save Changes", command=save_changes)
    save_btn.pack(pady=(0, 20))
    save_btn.pack_forget()

    def enable_editing():
            for i, (label, var) in enumerate(editable_vars.items()):
                label_refs[label].destroy()
                entry = create_entry(
                    table,
                    placeholder_text=label,
                    show="*" if label == "New Password" else None,
                    width=350
                )
                entry.configure(textvariable=var)
                entry.grid(row=len(static_fields) + i, column=1, sticky="w", padx=4, pady=4)
                entry_refs[label] = entry
            edit_btn.pack_forget()
            save_btn.pack(pady=(0, 20))
        
    edit_btn = create_primary_button(frame, text="Edit Info", command=enable_editing)
    edit_btn.pack(pady=(20, 10))

    return frame

def show_custom_confirm(master, title, message, on_yes, on_no=None):
    win = ctk.CTkToplevel(master)
    win.title(title)
    win.geometry("500x180")
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


# HELPDESK

def get_helpdesk_frame(parent_frame, user_id):
    conn = sqlite3.connect("helpdesk.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MESSAGE (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            text TEXT NOT NULL
        )
    """)
    conn.commit()

    frame = create_frame(parent_frame, width=800, height=600)

    create_label(frame, "Help Desk", size=FONT_SIZES["large"]).pack(pady=20)

    scroll_frame = create_frame(frame)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    canvas = ctk.CTkCanvas(scroll_frame, borderwidth=0, highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(scroll_frame, orientation="vertical", command=canvas.yview)
    messages_container = ctk.CTkFrame(canvas)

    messages_container.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=messages_container, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    cursor.execute("SELECT text FROM MESSAGE WHERE patient_id=? ORDER BY message_id", (user_id,))
    previous_messages = cursor.fetchall()

    if previous_messages:
        for (msg,) in previous_messages:
            msg_box = ctk.CTkFrame(messages_container, fg_color=COLORS["card"], corner_radius=10)
            msg_box.pack(fill="x", padx=5, pady=5)
            create_label(msg_box, text=f"You: {msg}", size=FONT_SIZES["medium"]).pack(anchor="w", padx=10, pady=5)
            create_label(msg_box, text="Operator: Thank you. We will reply soon on your email address.", size=FONT_SIZES["small"]).pack(anchor="w", padx=10, pady=(0, 5))
    else:
        create_label(messages_container, text="No messages yet. Start by sending one below.", size=FONT_SIZES["medium"]).pack(pady=10)

    input_frame = create_frame(frame, bg_color="transparent")
    input_frame.pack(fill="x", padx=20, pady=10)

    user_input = create_entry(input_frame, placeholder_text="Write your message...", width=500)
    user_input.pack(side="left", padx=5, pady=5)

    def send_message():
        msg = user_input.get().strip()
        if msg:
            cursor.execute("INSERT INTO MESSAGE (patient_id, text) VALUES (?, ?)", (user_id, msg))
            conn.commit()

            msg_box = ctk.CTkFrame(messages_container, fg_color=COLORS["card"], corner_radius=10)
            msg_box.pack(fill="x", padx=5, pady=5)
            create_label(msg_box, text=f"You: {msg}", size=FONT_SIZES["medium"]).pack(anchor="w", padx=10, pady=5)
            create_label(msg_box, text="Operator: Thank you. We will reply soon on your email address.", size=FONT_SIZES["small"]).pack(anchor="w", padx=10, pady=(0, 5))

            user_input.delete(0, "end")

    create_primary_button(input_frame, text="Send", command=send_message).pack(side="right", padx=5)

    return frame


# CHECK PASSWORD

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


# DIARY

from datetime import datetime, date, timedelta
def get_diary_frame(parent_frame, current_user_id):
    frame = create_frame(parent_frame, width=800, height=600)
    today_str = date.today().strftime("%Y-%m-%d")
    diary_file = "diary_answers.json"

    create_label(frame, text=f"Today Diary – {today_str}", size=FONT_SIZES["large"]).pack(pady=20)

    questions = [
        "① Difficulty falling asleep (0 = Very satisfied, 4 = Very dissatisfied)",
        "② Difficulty staying asleep (0 = Very satisfied, 4 = Very dissatisfied)",
        "③ Problem waking up too early (0 = Very satisfied, 4 = Very dissatisfied)",
        "④ Satisfaction with sleep pattern (0 = Very satisfied, 4 = Very dissatisfied)",
        "⑤ Interference with daily functioning (0 = Not at all, 4 = Very much)",
        "⑥ Noticeability to others (0 = Not at all, 4 = Very much)",
        "⑦ Worry about sleep (0 = Not at all, 4 = Very much)"
    ]

    saved_data = {}
    if os.path.exists(diary_file):
        with open(diary_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

    already_filled = today_str in saved_data
    FORCE_EDIT_TODAY = True
    previous_answers = saved_data.get(today_str, {})
    already_saved = already_filled

    sliders = {}
    value_labels = {}
    containers = []
    pages = [[], []]
    current_page = [0]

    content_frame = create_frame(frame)
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    confirmation_label = create_label(frame, text="", size=FONT_SIZES["medium"], color="green")
    confirmation_label.pack(pady=(5, 5))

    for i, question in enumerate(questions):
        qid = f"q{i+1}"
        container = create_frame(content_frame, bg_color="white")
        pages[i // 4].append(container)
        containers.append((qid, container))

        create_label(container, text=question, size=FONT_SIZES["medium"]).pack(anchor="w", padx=10, pady=(10, 5))

        row_frame = create_frame(container, bg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=(0, 10))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=0)

        slider = ctk.CTkSlider(row_frame, from_=0, to=4, number_of_steps=4)
        slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        value_label = create_label(row_frame, text="N/A", size=FONT_SIZES["medium"])
        value_label.grid(row=0, column=1)

        sliders[qid] = slider
        value_labels[qid] = value_label

        def make_update_label(qid=qid, slider=slider, label=value_label, container=container):
            def update_label(val):
                val_str = str(round(float(val)))
                label.configure(text=val_str)
                container.configure(border_color=COLORS["border"])
            return update_label

        slider.configure(command=make_update_label())

        if qid in previous_answers:
            slider.set(previous_answers[qid])
            value_label.configure(text=str(previous_answers[qid]))
            if not FORCE_EDIT_TODAY:
                slider.configure(state="disabled")

    button_frame = create_frame(frame, bg_color="transparent")
    button_frame.pack(fill="x", pady=10, padx=10)

    def show_page(index):
        for container in pages[0] + pages[1]:
            container.pack_forget()
        for widget in pages[index]:
            widget.pack(pady=10, padx=20, fill="x")
        current_page[0] = index
        arrow_button.configure(text="→" if index == 0 else "←", command=next_page if index == 0 else prev_page)

    def next_page():
        show_page(1)

    def prev_page():
        show_page(0)

    def save_answers():
        nonlocal already_saved
        if already_saved and not FORCE_EDIT_TODAY:
            confirmation_label.configure(text="You have already saved your responses today.")
            return

        missing = []
        responses = {}

        for qid, slider in sliders.items():
            value_text = value_labels[qid].cget("text")
            if value_text == "N/A":
                missing.append(qid)
            else:
                responses[qid] = int(value_text)

        if missing:
            confirmation_label.configure(text="Required field not answered", color="red")
            for qid, container in containers:
                if qid in missing:
                    container.configure(border_color="red", border_width=2)
                else:
                    container.configure(border_color=COLORS["border"], border_width=1)
            return

        saved_data[today_str] = responses
        with open(diary_file, "w", encoding="utf-8") as f:
            json.dump(saved_data, f, indent=2, ensure_ascii=False)

        somma_risposte = sum(responses.values())
        save_to_db(current_user_id, today_str, somma_risposte)

        for slider in sliders.values():
            slider.configure(state="disabled")

        def show_popup():
            popup = ctk.CTkToplevel(frame)
            popup.title("Diary Saved")
            popup.geometry("500x250")
            popup.grab_set()
            popup.lift()
            popup.focus_force()

            create_label(popup, text="Your responses have been saved successfully!", size=FONT_SIZES["medium"], color="green").pack(pady=(20, 10))
            create_label(popup, text=f"Total Score: {somma_risposte}", size=FONT_SIZES["medium"]).pack(pady=5)

            if somma_risposte > 15:
                msg = "Your total score is high.\nPlease try to improve your sleep, or consider contacting a specialist."
                color = "red"
            else:
                msg = "Your sleep pattern seems okay today."
                color = "green"

            create_label(popup, text=msg, size=FONT_SIZES["medium"], color=color, justify="center", wraplength=360).pack(pady=10)
            create_primary_button(popup, text="OK", command=popup.destroy).pack(pady=(10, 15))

        show_popup()
        already_saved = True
        confirmation_label.configure(text="You have already saved your responses today.", color="green")

    save_button = create_primary_button(button_frame, text="Save Answers", command=save_answers)
    save_button.pack(side="left", padx=10)

    arrow_button = create_secondary_button(button_frame, text="→", command=next_page, width=60)
    arrow_button.pack(side="right", padx=10)

    if already_filled and not FORCE_EDIT_TODAY:
        confirmation_label.configure(text="You have already saved your responses today.", color="green")

    show_page(0)
    return frame


# VSIT

def get_visits_frame(parent_frame, current_user_id):
    conn = sqlite3.connect("insomnia_management.db")
    frame = create_frame(parent_frame)
    create_label(frame, text="My visits", size=FONT_SIZES["large"]).pack(pady=10)

    booked_visits_db = load_booked_visits_from_db(conn)
    booked_consults_db = load_booked_consults_from_db(conn)
    doctor_id_to_name, _ = build_doctor_id_name_maps(conn)

    booked_visits = [{
        "code": code,
        "patient_id": patient_id,
        "doctor": doctor_id_to_name.get(doctor_id),
        "date": f"{date} {time_}"
    } for code, patient_id, doctor_id, date, time_ in booked_visits_db]

    booked_consults = [{
        "code": code,
        "patient_id": patient_id,
        "doctor": doctor_id_to_name.get(doctor_id),
        "date": f"{date} {time_}"
    } for code, patient_id, doctor_id, date, time_ in booked_consults_db]

    # Scrollable section full-width
    scroll_container = create_frame(frame)
    scroll_container.pack(fill="both", expand=True)

    scroll_frame = create_frame(scroll_container, width=700)
    scroll_frame.pack(anchor="center", pady=10)

    canvas = ctk.CTkCanvas(scroll_frame, height=500, width=700)
    scrollbar = ctk.CTkScrollbar(scroll_frame, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    container = ctk.CTkFrame(canvas, width=700)
    container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=container, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def refresh_visits_list():
        for widget in container.winfo_children():
            widget.destroy()

        filtered_visits = [v for v in booked_visits if v["patient_id"] == current_user_id]
        filtered_consults = [c for c in booked_consults if c["patient_id"] == current_user_id]

        all_visits = sorted(filtered_visits + filtered_consults, key=lambda x: x["date"])

        if not all_visits:
            create_label(container, text="No visits booked yet.", size=FONT_SIZES["medium"]).pack(pady=5)
            return

        for visit in all_visits:
            visit_box = create_frame(container, bg_color=COLORS["card"], width=600, height=100)
            visit_box.pack(padx=10, pady=10, fill="x")

            dt = datetime.strptime(visit["date"], "%Y-%m-%d %H:%M")
            create_label(visit_box, text=dt.strftime("%A, %d %B %Y"), size=FONT_SIZES["medium"]).pack(anchor="w", padx=15, pady=(5, 0))
            create_label(visit_box, text=dt.strftime("%H:%M"), size=18).pack(anchor="w", padx=15)
            create_label(visit_box, text=f"{visit['doctor']} – Code: {visit['code']}", size=15).pack(anchor="w", padx=15, pady=(0, 5))

            if dt > datetime.now():
                btns = create_frame(visit_box, bg_color="transparent")
                btns.pack(anchor="e", padx=10)
                create_secondary_button(btns, text="Modify", command=lambda v=visit: modify_visit(v), width=80).pack(side="left", padx=5)
                create_primary_button(btns, text="Delete", command=lambda v=visit: delete_visit(v), width=80).pack(side="left", padx=5)

    def modify_visit(visit):
        popup = ctk.CTkToplevel()
        apply_window_style(popup)
        popup.title("Modify Visit")
        popup.geometry("600x600")

        create_label(popup, text="Select New Date", size=FONT_SIZES["medium"]).pack(pady=10)
        selected_doctor = visit["doctor"]
        slots = available_slots.get(selected_doctor, [])

        calendar_frame = create_frame(popup)
        calendar_frame.pack(pady=10)
        calendar = Calendar(calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd',
                            showweeknumbers=False, font='Helvetica 14', foreground='black')
        calendar.pack(padx=10, pady=10)

        time_var = ctk.StringVar()

        def proceed_to_time_selection():
            selected_date = calendar.get_date()
            times = [s.split()[1] for s in slots if s.startswith(selected_date)]
            if not times:
                show_custom_warning(popup, message="No slots available.")
                return

            time_popup = ctk.CTkToplevel()
            apply_window_style(time_popup)
            time_popup.geometry("400x250")
            time_var.set(times[0])

            create_label(time_popup, text="Select New Time").pack(pady=10)
            time_dropdown, _ = create_dropdown(time_popup, times, width=180, command=lambda val: time_var.set(val))
            time_dropdown.pack(pady=10)

            def confirm():
                new_slot = f"{selected_date} {time_var.get()}"
                if new_slot not in available_slots[selected_doctor]:
                    show_custom_error(time_popup, message="Slot already booked.")
                    return

                available_slots[selected_doctor].append(visit["date"])
                available_slots[selected_doctor].remove(new_slot)
                visit["date"] = new_slot
                update_visit_in_db(conn, visit["code"], *new_slot.split())

                popup.destroy()
                time_popup.destroy()
                refresh_visits_list()
                show_custom_warning(frame, title="Updated", message="Visit updated successfully.")

            create_primary_button(time_popup, text="Update Visit", command=confirm).pack(pady=20)

        create_primary_button(popup, text="Next", command=proceed_to_time_selection).pack(pady=20)

    def delete_visit(visit):
        code = visit["code"]
        delete_visit_from_db(conn, code)
        for lst in (booked_visits, booked_consults):
            lst[:] = [v for v in lst if v["code"] != code]
        refresh_visits_list()
        show_custom_warning(frame, title="Deleted", message="Visit deleted successfully.")

    def book_new_visit():
        popup = ctk.CTkToplevel()
        apply_window_style(popup)
        popup.title("Book New Visit")
        popup.geometry("600x600")

        doctors = get_doctors_for_patient(current_user_id)
        if not doctors:
            show_custom_warning(popup, title="No doctors", message="No doctors assigned.")
            popup.destroy()
            return

        create_label(popup, text="Select Practitioner", size=FONT_SIZES["medium"]).pack(pady=10)
        doc_dropdown, doc_var = create_dropdown(popup, doctors)
        doc_dropdown.pack(pady=5)

        calendar_frame = create_frame(popup)
        calendar_frame.pack(pady=10)
        calendar = Calendar(calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd',
                            showweeknumbers=False, font='Helvetica 14', foreground='black')
        calendar.pack(padx=10, pady=10)

        time_var = ctk.StringVar()

        def select_time():
            date_sel = calendar.get_date()
            doctor = doc_var.get()
            slots = available_slots.get(doctor, [])
            times = [s.split()[1] for s in slots if s.startswith(date_sel)]
            if not times:
                show_custom_warning(popup, message="No available slots.")
                return

            time_popup = ctk.CTkToplevel()
            apply_window_style(time_popup)
            time_popup.geometry("400x250")
            time_var.set(times[0])

            create_label(time_popup, text="Select Time Slot").pack(pady=10)
            dropdown, _ = create_dropdown(time_popup, times, width=180, command=lambda v: time_var.set(v))
            dropdown.pack(pady=10)

            def confirm():
                slot = f"{date_sel} {time_var.get()}"
                if slot not in available_slots[doctor]:
                    show_custom_error(time_popup, message="Slot already taken.")
                    return
                available_slots[doctor].remove(slot)
                doctor_id = doctor_name_to_id[doctor]
                code = generate_visit_code(conn) if "(Family Doctor)" in doctor else generate_consult_code(conn)
                date_only, time_only = slot.split()
                entry = {
                    "doctor": doctor,
                    "date": slot,
                    "code": code,
                    "patient_id": current_user_id
                }
                if "(Family Doctor)" in doctor:
                    insert_visit_to_db(conn, code, current_user_id, doctor_id, date_only, time_only)
                    booked_visits.append(entry)
                else:
                    insert_consult_to_db(conn, code, current_user_id, doctor_id, date_only, time_only)
                    booked_consults.append(entry)

                time_popup.destroy()
                popup.destroy()
                refresh_visits_list()
                show_custom_warning(frame, title="Booked", message="Visit booked successfully.")

            create_primary_button(time_popup, text="Book", command=confirm).pack(pady=20)

        create_primary_button(popup, text="Next", command=select_time).pack(pady=20)

    create_primary_button(frame, text="Book a New Visit", command=book_new_visit).pack(pady=15)

    refresh_visits_list()
    return frame

# UPDATE DATABASE

def update_password_in_db(user_id, new_password):
    conn = sqlite3.connect("insomnia_management.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE USER SET Password = ? WHERE Id = ?", (new_password, user_id))
    conn.commit()
    conn.close()

def update_patient_info_in_db(user_id, updates):
    """
    Update the fields of Personal_Info for the user with user_id.
    updates: dict with keys among
    'Residency', 'Domicile', 'Phone Number', 'E-mail', 'New Password'
    """
    field_map = {
        "Residency": "Residency",
        "Domicile": "Domicile",
        "Phone Number": "Phone_Number",
        "E-mail": "Email",
        "New Password": "Password"
    }

    set_clauses = []
    values = []

    for key, val in updates.items():
        if val is not None and key in field_map:
            set_clauses.append(f"{field_map[key]} = ?")
            values.append(val)

    if not set_clauses:
        return 

    sql = f"UPDATE Personal_Info SET {', '.join(set_clauses)} WHERE User_Id = ?"
    values.append(user_id)

    conn = sqlite3.connect("insomnia_management.db")
    cursor = conn.cursor()

    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def insert_visit_to_db(conn, code, patient_id, doctor_id, date, time_):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO VISIT (Code, Patient_Id, Family_Doctor_Id, Date, Hour) VALUES (?, ?, ?, ?, ?)",
                (code, patient_id, doctor_id, date, time_))
    conn.commit()

def update_visit_in_db(conn, code, date, time_):
    cursor = conn.cursor()
    cursor.execute("UPDATE VISIT SET Date=?, Hour=? WHERE Code=?",
                    (date, time_, code))
    conn.commit()

def delete_visit_from_db(conn, code):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM VISIT WHERE Code=?", (code,))
    conn.commit()

def save_to_db(id_paziente, data_risposte, somma):
    conn = sqlite3.connect("diary_responses.db")
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS DIARY (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Patient_Id TEXT NOT NULL,
                date TEXT NOT NULL,
                value INTEGER NOT NULL,
                UNIQUE(Patient_Id, Date)
            )
        ''')
    try:
        c.execute('''
                INSERT OR REPLACE INTO DIARY (Patient_Id, Date, Value)
                VALUES (?, ?, ?)
            ''', (id_paziente, data_risposte, somma))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Errore DB: {e}")
    conn.close()



class PatientPage(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        apply_window_style(self)
        self.master = master
        self.current_user_id = user_id
        self.sleep_data_path = "sleep_data.db"

        self.patient_info = get_patient_info(user_id) or {}

        self.menu_frame = create_frame(self)
        self.menu_frame.pack(expand=True)

        create_label(self.menu_frame, text="Welcome, Patient!", size=FONT_SIZES["large"], color="#003366").pack(pady=20)

        create_primary_button(self.menu_frame, text="Profile", command=self.activate_profile).pack(pady=10)
        create_primary_button(self.menu_frame, text="Visits", command=self.activate_visits).pack(pady=10)
        create_primary_button(self.menu_frame, text="Statistics and Diagrams", command=self.activate_stats).pack(pady=10)
        create_primary_button(self.menu_frame, text="My Diary", command=self.activate_diary).pack(pady=10)

        self.setup_sidebar()
        
    def logout(self):
        self.destroy()
        from ui.login_selector import LoginSelector
        LoginSelector(self.master)

    def clear_app(self):
        for widget in self.winfo_children():
            widget.destroy()

    def on_logout(self):
        print("Logged out")
        self.clear_app()
        self.__init__(self.master, self.current_user_id)

    def setup_sidebar(self):
        self.menu_frame.destroy()

        self.sidebar = create_frame(self, width=250, height=450, bg_color=COLORS["card"])
        self.sidebar.pack(side="left", anchor="n", padx=10, pady=10)

        self.main_content = create_frame(self)
        self.main_content.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        self.profile_btn = create_primary_button(self.sidebar, text="Profile", command=self.show_profile, width=180)
        self.visits_btn = create_primary_button(self.sidebar, text="Visits", command=self.show_visits, width=180)
        self.diary_btn = create_primary_button(self.sidebar, text="My Diary", command=self.show_diary, width=180)
        self.stats_btn = create_primary_button(self.sidebar, text="Statistics and Diagram", command=self.activate_stats, width=180)

        self.help_btn = ctk.CTkButton(
            self.sidebar,
            text="Help Desk",
            command=self.show_helpdesk,
            width=180,
            height=40,
            font=(FONT_FAMILY, FONT_SIZES["medium"]),
            fg_color="#003366",
            hover_color="#005599",
            text_color="white",
            corner_radius=12
        )

        self.logout_btn = create_secondary_button(
            self.sidebar,
            text="Logout",
            command=self.logout,
            width=180
        )

        for btn in [self.profile_btn, self.visits_btn, self.diary_btn, self.stats_btn, self.help_btn, self.logout_btn]:
            btn.pack(pady=10, padx=10)

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

    def activate_diary(self):
            self.setup_sidebar()
            self.show_diary()

    def show_profile(self):
            self.clear_main_content()
            user_id = self.patient_info.get("fiscal_code", "")
            frame = get_profile_frame(self.main_content, self.patient_info, user_id)
            frame.pack(fill="both", expand=True)

    def show_visits(self):
            self.clear_main_content()
            frame = get_visits_frame(self.main_content, self.current_user_id)
            frame.pack(fill="both", expand=True)

    def show_diary(self):
            self.clear_main_content()
            frame = get_diary_frame(self.main_content, self.current_user_id)
            frame.pack(fill="both", expand=True)

    def show_helpdesk(self):
            self.clear_main_content()
            frame = get_helpdesk_frame(self.main_content, self.current_user_id)
            frame.pack(fill="both", expand=True)

    def activate_stats(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        stats_page = SensorDataPage(self.main_content, self.current_user_id)
        stats_page.pack(fill="both", expand=True)

