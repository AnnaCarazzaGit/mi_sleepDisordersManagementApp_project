import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import re
import sqlite3
from ui.style_ctk import *

# import face_recognition
# from tkinter import messagebox
# import cv2
# import os


# --- DATABASE UTILITY ---
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


# --- AUTH FUNCTIONS ---
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


# --- CHECK PASSWORD ---
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


def update_password_in_db(user_id, new_password):
    conn = sqlite3.connect("insomnia_management.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE USER SET Password = ? WHERE Id = ?", (new_password, user_id))
    conn.commit()
    conn.close()


# --- LOGIN PAGE ---
class PatientLoginPage(ctk.CTkFrame):
    def __init__(self, root, on_success):
        super().__init__(root, fg_color=COLORS["background"])
        self.root = root
        self.on_success = on_success
        self.pack(fill="both", expand=True)

        logo_path = "logoASE.png" 
        logo_image = Image.open(logo_path)
        logo_ctk = CTkImage(light_image=logo_image, dark_image=logo_image, size=(350, 200)) 
        ctk.CTkLabel(self, image=logo_ctk, text="").pack(pady=20)

        create_label(self, text="Please, enter your credentials:", size=30).pack(pady=30)

        self.id_entry = create_entry(self, placeholder_text="ID Code")
        self.id_entry.pack(pady=10)

        self.pw_entry = create_entry(self, placeholder_text="Password", show="*")
        self.pw_entry.pack(pady=10)

        create_primary_button(self, text="Login", command=self.login_with_credentials).pack(pady=5)
        # create_primary_button(self, text="Use Face ID", command=self.login_with_faceid).pack(pady=5)

        self.reset_button = create_secondary_button(self, text="Reset Password", command=self.check_password_constraints)
        self.reset_button.pack(pady=10)
        self.reset_button.pack_forget()
        
        create_secondary_button(self, text="Back", command=self.logout_selector).pack(pady=10)

    def login_with_credentials(self):
        id_code = self.id_entry.get().strip()
        password = self.pw_entry.get().strip()
        result = authenticate(id_code, password)
        if result == "success":
            self.destroy()
            self.on_success(id_code)
        else:
            self.handle_result(result)

    # def capture_face_image(filename):
    #     cap = cv2.VideoCapture(1)
    #     if not cap.isOpened():
    #         raise RuntimeError("Cannot access camera")

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             continue
    #         cv2.imshow("Capture Face - Press 's' to Save", frame)
    #         if cv2.waitKey(1) & 0xFF == ord('s'):
    #             cv2.imwrite(filename, frame)
    #             break
    #     cap.release()
    #     cv2.destroyAllWindows()

    # def compare_faces(known_path, test_path):
    #     known_img = face_recognition.load_image_file(known_path)
    #     test_img = face_recognition.load_image_file(test_path)

    #     known_enc = face_recognition.face_encodings(known_img)
    #     test_enc = face_recognition.face_encodings(test_img)

    #     if not known_enc or not test_enc:
    #         return False

    #     return face_recognition.compare_faces([known_enc[0]], test_enc[0])[0]

    def handle_result(self, result):
        if result == "wrong_password":
            show_custom_error(self, title="Login Failed", message="Wrong ID or password.")
        elif result == "reset":
            show_custom_warning(self, title="Too Many Attempts", message="Too many failed attempts. Please reset your password.")
            if not self.reset_button.winfo_ismapped():
                self.reset_button.pack(pady=10)
        elif result == "ID not found":
            show_custom_error(self, title="User Not Found", message="No user found with that ID Code.")

    def check_password_constraints(self):
        id_code = self.id_entry.get().strip()
        user = users_db.get(id_code)
        if not user:
            show_custom_error(self, title="Error", message="Please enter a valid ID Code.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Reset Password")
        popup.geometry("400x250")
        popup.configure(fg_color=COLORS["background"])
        popup.grab_set()

        create_label(popup, text="New Password", size=FONT_SIZES["medium"]).pack(pady=10)
        new_pw_entry = create_entry(popup, placeholder_text="New Password", show="*")
        new_pw_entry.pack(pady=5)

        def validate_and_save():
            new_password = new_pw_entry.get().strip()
            old_password = user["password"]

            errors = check_password_constraints(new_password, old_password)
            if errors:
                show_custom_error(popup, title="Invalid Password", message="\n".join(errors))
                return

            user["password"] = new_password
            user["attempts"] = 0
            update_password_in_db(id_code, new_password)
            show_custom_warning(popup, title="Success", message="Password updated successfully!")
            popup.destroy()

        create_primary_button(popup, text="Confirm", command=validate_and_save).pack(pady=15)

    # def capture_face_image(filename):
    #     cap = cv2.VideoCapture(1)
    #     if not cap.isOpened():
    #         raise RuntimeError("Cannot access camera")

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             continue
    #         cv2.imshow("Capture Face - Press 's' to Save", frame)
    #         if cv2.waitKey(1) & 0xFF == ord('s'):
    #             cv2.imwrite(filename, frame)
    #             break
    #     cap.release()
    #     cv2.destroyAllWindows()


    # def ask_faceid_setup(self, id_code):
    #     user = users_db[id_code]
       
    #     if not user["consent"]:
    #         answer = messagebox.askyesno("Privacy Consent", "Do you consent to using Face ID (biometric data)?")
    #         if not answer:
    #             messagebox.showinfo("Face ID", "You can continue without Face ID.")
    #             self.on_success(id_code)
    #             return
           
    #         conn = sqlite3.connect("insomnia_management.db")
    #         cursor = conn.cursor()
    #         cursor.execute("UPDATE Personal_Info SET Privacy_Consent = 'Yes' WHERE User_Id = ?", (id_code,))
    #         conn.commit()
    #         conn.close()
    #         user["consent"] = True
      
    #     face_id_code = user["face_id"]
    #     if not face_id_code:
    #         messagebox.showerror("Error", "Missing Face_Id value for this user.")
    #         return

    #     face_path = os.path.join(FACE_DIR, f"{face_id_code}.jpg")
    #     if os.path.exists(face_path):
    #         self.on_success(id_code)
    #         return

    #     setup = messagebox.askyesno("Face ID Setup", "Would you like to enable Face ID now?")
    #     if setup:
    #         capture_face_image(face_path)

    #     self.on_success(id_code)

    # def login_with_faceid(self):
    #     id_code = self.id_entry.get().strip()

    #     user = users_db.get(id_code)
    #     if not user:
    #         messagebox.showerror("Error", "User ID not found.")
    #         return

    #     if not user["consent"]:
    #         messagebox.showwarning("Consent Missing", "Face ID is not enabled due to missing privacy consent.")
    #         return

    #     face_id_code = user["face_id"]
    #     if not face_id_code:
    #         messagebox.showerror("Error", "Face ID is not configured for this user.")
    #         return

    #     ref_path = os.path.join(FACE_DIR, f"{face_id_code}.jpg")
    #     if not os.path.exists(ref_path):
    #         messagebox.showerror("Error", f"Reference image '{face_id_code}.jpg' not found.")
    #         return

    #     test_path = os.path.join(FACE_DIR, f"{face_id_code}_test.jpg")
    #     capture_face_image(test_path)

    #     if compare_faces(ref_path, test_path):
    #         self.on_success(id_code)

    #     else:
    #         messagebox.showerror("Access Denied", "Face not recognized.")

    def logout_selector(self):
        self.pack_forget()
        self.destroy()
        from ui.login_selector import LoginSelector  
        LoginSelector(self.master).pack(fill="both", expand=True)

        