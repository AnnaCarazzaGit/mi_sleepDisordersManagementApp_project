import cv2
import face_recognition
import os
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# Create directory for face images
FACE_DIR = "captured_faces"
os.makedirs(FACE_DIR, exist_ok=True)

# In-memory user database
users_db = {
    "emma": {
        "password": "emma",
        "face_id": False,
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

# ----------------------------- Funzioni frame sezioni -----------------------------
def get_stats_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="📊 Statistics and Diagrams", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # Parametri e intervalli temporali
    parameters = [
        "Total sleep time",
        "Time in bed vs time asleep",
        "Sleep stages",
        "Heart rate",
        "Respiratory rate",
        "Oxygen saturation (SpO₂)",
        "Snoring intensity/frequency",
        "Body position",
        "Body Temperature",
        "Room Temperature"
    ]

    timeframes = [
        "One night",
        "Last 7 days",
        "Last month",
        "Last 6 months"
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

    def open_graph_window():
        selected_param = param_var.get()
        selected_time = time_var.get()

        # Crea nuova finestra
        graph_window = ctk.CTkToplevel()
        graph_window.title(f"{selected_param} - {selected_time}")
        graph_window.geometry("600x400")

        ctk.CTkLabel(graph_window, text=f"{selected_param} ({selected_time})",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(graph_window, text="⚠ No available data",
                     font=ctk.CTkFont(size=14)).pack(pady=30)

    ctk.CTkButton(frame, text="Show Diagram", command=open_graph_window).pack(pady=30)

    return frame

import json
import os


import re

def get_profile_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="👤 Profile", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    # Dati del profilo
    profile_info = {
        "Name and Surname": "Giulia Rossi",
        "Fiscal Code": "ABC123DEF",
        "Birthdate": "1996-08-01",
        "Gender": "Female",
        "Residency": "Torino",
        "Domicile": "Via Po, 12",
        "Nationality": "Italian",
        "Family Doctor": "Dr. Bianchi",
        "Psychologist": "Dr.ssa Neri",
        "Phone Number": "+39 331 1234567",
        "E-mail": "giulia@example.com",
        "Privacy Consent": "Yes"
    }

    # Frame interno per griglia
    table = ctk.CTkFrame(frame)
    table.pack(pady=10, padx=20)

    # Riempie la griglia con le etichette
    for i, (label, value) in enumerate(profile_info.items()):
        ctk.CTkLabel(table, text=label + ":", anchor="w", width=180).grid(row=i, column=0, sticky="w", pady=4, padx=4)
        ctk.CTkLabel(table, text=value, anchor="w").grid(row=i, column=1, sticky="w", pady=4, padx=4)

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


def get_diary_frame(parent_frame):
    frame = ctk.CTkFrame(parent_frame)
    ctk.CTkLabel(frame, text="🛌 Sleep Questionnaire", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

    questions = [
        "1️⃣ Difficulty falling asleep",
        "2️⃣ Difficulty staying asleep",
        "3️⃣ Problem waking up too early",
        "4️⃣ How satisfied are you with your current sleep pattern (0=very satisfied, 4=very dissatisfied)",
        "5️⃣ To what extent do you consider your sleep problem to interfere with your daily functioning (concentration, memory, fatigue, etc.) (0=not at all, 4=very much)",
        "6️⃣ How noticeable to others do you think your sleeping problem is in terms of impairing the quality of your life (0=not at all, 4=very much)",
        "7️⃣ How worried are you about your current sleep problem (0=not at all, 4=very much)"
    ]

    sliders = []  # Lista per salvare i riferimenti agli slider

    # Frame per messaggio di conferma con un po' di spazio e colore di sfondo
    confirmation_label = ctk.CTkLabel(frame, 
                                      text="", 
                                      font=ctk.CTkFont(size=14), 
                                      text_color="green", 
                                      bg_color="white")  # Colore di sfondo
    confirmation_label.pack(pady=(20, 10), fill="x", padx=10)  # Aggiunto più padding

    for question in questions:
        label = ctk.CTkLabel(frame, 
                             text=question, 
                             anchor="w", 
                             justify="left", 
                             wraplength=700)  # Larghezza max
        label.pack(fill="x", padx=10, pady=(10, 0))
        
        slider_frame = ctk.CTkFrame(frame)
        slider_frame.pack(fill="x", padx=20, pady=(0, 10))

        slider = ctk.CTkSlider(slider_frame, from_=0, to=4, number_of_steps=4)
        slider.pack(side="left", fill="x", expand=True)

        # Aggiungiamo la numerazione sopra o sotto lo slider
        for i in range(5):  # Numeri da 0 a 4
            ctk.CTkLabel(slider_frame, text=str(i), font=ctk.CTkFont(size=10)).pack(side="left", padx=20)

        sliders.append(slider)

    # Funzione da eseguire quando premi il bottone
    def submit_answers():
        answers = [round(slider.get()) for slider in sliders]
        # Mostriamo il messaggio di conferma nell'interfaccia
        confirmation_label.config(text="✅ Risposte inviate con successo!", text_color="green")
        
        # Nascondi il messaggio di conferma dopo 2 secondi
        frame.after(2000, lambda: confirmation_label.config(text=""))

    # Bottone per inviare le risposte
    submit_button = ctk.CTkButton(frame, text="📤 Submit Answers", command=submit_answers)
    submit_button.pack(pady=20)

    return frame




    # Dati salvati
    diary_file = "diary_answers.json"
    saved_data = {}
    if os.path.exists(diary_file):
        with open(diary_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

    # Organizzazione in due pagine
    pages = [[], []]
    entries = {}
    current_page = [0]

    content_frame = ctk.CTkFrame(frame)
    content_frame.pack(pady=10)

    # Crea tutte le entry e salvale
    for i, question in enumerate(questions):
        qid = f"q{i+1}"
        container = ctk.CTkFrame(content_frame)
        ctk.CTkLabel(container, text=question, anchor="w").pack(pady=2, padx=10, anchor="w")
        entry = ctk.CTkEntry(container, width=400)
        entry.pack(pady=2, padx=10)
        if qid in saved_data:
            entry.insert(0, saved_data[qid])
        entries[qid] = entry
        pages[i // 5].append(container)

    def show_page(index):
        for container in pages[0] + pages[1]:
            container.pack_forget()
        for widget in pages[index]:
            widget.pack(pady=5)
        current_page[0] = index
        # Mostra o nascondi i bottoni
        if index == 0:
            arrow_button.configure(text="⏩", command=next_page)
            save_button.pack_forget()
        else:
            arrow_button.configure(text="⏪", command=prev_page)
            save_button.pack(side="left")

    def next_page():
        show_page(1)

    def prev_page():
        show_page(0)

    def save_answers():
        responses = {qid: entry.get().strip() for qid, entry in entries.items()}
        if any(not val for val in responses.values()):
            messagebox.showerror("Errore", "Compila tutte le domande prima di salvare.")
            return
        with open(diary_file, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Salvato", "Risposte salvate con successo!")

    # Frame per i bottoni
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(fill="x", pady=10, padx=10)

    arrow_button = ctk.CTkButton(button_frame, text="⏩", width=60, command=next_page)
    arrow_button.pack(side="right")

    save_button = ctk.CTkButton(button_frame, text="💾 Salva", command=save_answers)

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

    def book_new_visit():
        popup = ctk.CTkToplevel()
        popup.title("Book New Visit")
        popup.geometry("400x300")
        ctk.CTkLabel(popup, text="Select Practitioner").pack(pady=10)
        doctor_combo = ctk.CTkOptionMenu(popup, values=list(available_slots.keys()))
        doctor_combo.pack()

        def select_slot():
            selected_doctor = doctor_combo.get()
            slots = available_slots.get(selected_doctor, [])
            if not slots:
                messagebox.showinfo("No Availability", "No available slots for current month.")
                return

            slot_popup = ctk.CTkToplevel()
            slot_popup.title("Select Slot")
            slot_popup.geometry("400x300")

            slot_var = ctk.StringVar(value=slots[0])
            ctk.CTkOptionMenu(slot_popup, values=slots, variable=slot_var).pack(pady=20)

            def confirm_booking():
                slot = slot_var.get()
                code = generate_visit_code()
                booked_visits.append({
                    "doctor": selected_doctor,
                    "date": slot,
                    "code": code,
                })
                available_slots[selected_doctor].remove(slot)
                slot_popup.destroy()
                popup.destroy()
                refresh_visits_list()
                messagebox.showinfo("Booked", f"Visit booked. Code: {code}")

            ctk.CTkButton(slot_popup, text="Book", command=confirm_booking).pack(pady=10)

        ctk.CTkButton(popup, text="Next", command=select_slot).pack(pady=20)

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

def capture_face_image(filename):
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise RuntimeError("Cannot access camera")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("Capture Face - Press 's' to Save", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(filename, frame)
            break
    cap.release()
    cv2.destroyAllWindows()

def compare_faces(known_path, test_path):
    known_img = face_recognition.load_image_file(known_path)
    test_img = face_recognition.load_image_file(test_path)

    known_enc = face_recognition.face_encodings(known_img)
    test_enc = face_recognition.face_encodings(test_img)

    if not known_enc or not test_enc:
        return False

    return face_recognition.compare_faces([known_enc[0]], test_enc[0])[0]

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

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_success, on_logout):
        super().__init__(master)
        self.on_success = on_success
        self.on_logout = on_logout

        ctk.CTkLabel(self, text="Patient Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        self.id_entry = ctk.CTkEntry(self, placeholder_text="ID Code")
        self.id_entry.pack(pady=10)
        self.pw_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.pw_entry.pack(pady=10)
        ctk.CTkButton(self, text="Login", command=self.login_with_credentials).pack(pady=5)
        ctk.CTkButton(self, text="Use Face ID", command=self.login_with_faceid).pack(pady=5)
        ctk.CTkButton(self, text="Reset Password", command=self.check_password_constraints, fg_color="gray").pack(pady=10)

    def login_with_credentials(self):
        id_code = self.id_entry.get().strip()
        password = self.pw_entry.get().strip()
        result = authenticate(id_code, password)
        if result == "success":
            self.ask_faceid_setup(id_code)
        else:
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

    def ask_faceid_setup(self, id_code):
        if not users_db[id_code].get("face_id"):
            answer = messagebox.askyesno("Face ID Setup", "Would you like to enable Face ID?")
            if answer:
                filename = os.path.join(FACE_DIR, f"{id_code}_ref.jpg")
                capture_face_image(filename)
                users_db[id_code]["face_id"] = True
        self.on_success()

    def login_with_faceid(self):
        id_code = self.id_entry.get().strip()
        if not users_db.get(id_code):
            messagebox.showerror("Error", "User ID not found.")
            return
        if not users_db[id_code]["face_id"]:
            messagebox.showwarning("Face ID Not Enabled", "Face ID not enabled for this user.")
            return
        ref_path = os.path.join(FACE_DIR, f"{id_code}_ref.jpg")
        if not os.path.exists(ref_path):
            messagebox.showerror("Error", "Reference image not found.")
            return
        test_path = os.path.join(FACE_DIR, f"{id_code}_test.jpg")
        capture_face_image(test_path)
        if compare_faces(ref_path, test_path):
            self.on_success()
        else:
            messagebox.showerror("Access Denied", "Face not recognized.")

    def check_password_constraints(self):
        id_code = self.id_entry.get().strip()
        user = users_db.get(id_code)
        if not user:
            messagebox.showerror("Error", "Please enter a valid ID Code.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Reset Password")
        popup.geometry("400x250")
        ctk.CTkLabel(popup, text="New Password", font=ctk.CTkFont(size=16)).pack(pady=10)
        new_pw_entry = ctk.CTkEntry(popup, placeholder_text="New Password", show="*")
        new_pw_entry.pack(pady=5)

        def validate_and_save():
            new_password = new_pw_entry.get().strip()
            user["password"] = new_password
            user["attempts"] = 0
            messagebox.showinfo("Success", "Password updated successfully!")
            popup.destroy()

        ctk.CTkButton(popup, text="Confirm", command=validate_and_save).pack(pady=15)

    def logout(self):
        self.on_logout()



class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Patient App")
        self.geometry("1000x700")
        self.configure(fg_color="#f2f4f7")

        # Mostra solo il login all'avvio
        self.login_frame = LoginFrame(self, self.after_login, self.on_logout)
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

        # Logout button
        ctk.CTkButton(self, text="Logout", command=self.logout).pack(pady=20)

    def logout(self):
        # Go back to the login screen
        self.clear_app()
        self.login_frame = LoginFrame(self, self.after_login, self.logout)
        self.login_frame.pack(expand=True, fill="both")

    def clear_app(self):
        for widget in self.winfo_children():
            widget.destroy()


    def on_logout(self):
        # Do something like showing login screen again or cleaning up
        print("Logged out")

 
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
