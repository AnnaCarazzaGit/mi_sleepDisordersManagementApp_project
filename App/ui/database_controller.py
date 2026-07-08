import sqlite3

class DatabaseController:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        """
        Connects to the SQLite database and returns the connection object.
        Rows fetched will behave like dictionaries.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables dict-like access to columns
        return conn


    def get_user(self, username, password):
        """
        Retrieves user details based on the username and password.
        Used for login validation.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM USER WHERE Id = ? AND Password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()  # Fetch one result (should be user data)
        conn.close()
        return result  # Returns None if user not found, otherwise a tuple with user data


    def get_manager_by_pin(self, pin):
        """
        Retrieves manager pin.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM APP_MANAGER WHERE pin = ?"
        cursor.execute(query, (pin,))
        result = cursor.fetchone()  # Fetch one result (should be user data)
        conn.close()
        return result  # Returns None if user not found, otherwise a tuple with user data


    def get_user_by_id(self, user_id):
        """
        Retrieves family doctor details based on the user_id.
        This is used when you need to load the profile page of a user.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM Personal_Info JOIN FAMILY_DOCTOR ON Personal_Info.User_Id = FAMILY_DOCTOR.Family_Doctor_Id " \
        "WHERE Personal_Info.User_Id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    

    def get_psychologist_by_id(self, user_id):
        """
        Retrieves psychologist details based on the user_id.
        This is used when you need to load the profile page of a user.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM Personal_Info JOIN PSYCHOLOGIST ON Personal_Info.User_Id = PSYCHOLOGIST.Psychologist_Id " \
        "WHERE Personal_Info.User_Id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    

    def get_patient_visits(self, patient_id):
        """
        Returns a dictionary with the last past visit and the next upcoming visit for a patient.
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Last past visit
        cursor.execute("""
            SELECT Date FROM VISIT
            WHERE Patient_Id = ? AND Date < DATE('now')
            ORDER BY Date DESC
            LIMIT 1
        """, (patient_id,))
        last_visit_row = cursor.fetchone()
        last_visit = last_visit_row["Date"] if last_visit_row else "N/A"

        # Next upcoming visit
        cursor.execute("""
            SELECT Date FROM VISIT
            WHERE Patient_Id = ? AND Date >= DATE('now')
            ORDER BY Date ASC
            LIMIT 1
        """, (patient_id,))
        next_visit_row = cursor.fetchone()
        next_visit = next_visit_row["Date"] if next_visit_row else "N/A"

        conn.close()
        return {
            "last_visit": last_visit,
            "next_visit": next_visit
        }


    def get_patient_consults(self, patient_id):
        """
        Returns a dictionary with the last past and next upcoming psychological consult for a patient.
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Last past consult
        cursor.execute("""
            SELECT Date, Note FROM CONSULT
            WHERE Patient_Id = ? AND Date < DATE('now')
            ORDER BY Date DESC
            LIMIT 1
        """, (patient_id,))
        last_consult_row = cursor.fetchone()
        last_consult = last_consult_row["Date"] if last_consult_row else "N/A"
        last_consult_note = last_consult_row["Note"] if last_consult_row else "N/A"

        # Next upcoming consult
        cursor.execute("""
            SELECT Date, Note FROM CONSULT
            WHERE Patient_Id = ? AND Date >= DATE('now')
            ORDER BY Date ASC
            LIMIT 1
        """, (patient_id,))
        next_consult_row = cursor.fetchone()
        next_consult = next_consult_row["Date"] if next_consult_row else "N/A"
        next_consult_note = next_consult_row["Note"] if next_consult_row else "N/A"

        conn.close()
        return {
            "last_consult": last_consult,
            "next_consult": next_consult,
            "last_consult_note": last_consult_note,
            "next_consult_note": next_consult_note
        }


    def get_patient_by_cf(self, cf):
        """
        Looks up a patient by fiscal code (CF).
        Returns a dictionary with patient details if found, otherwise None.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT 
                pi.User_Id,
                pi.Name,
                pi.Surname,
                pi.Gender,
                pi.Birthdate,
                pi.Email,
                pi.Phone_Number
            FROM Personal_Info pi
            WHERE pi.User_Id = ?
        """
        cursor.execute(query, (cf,))
        row = cursor.fetchone()
        conn.close()

        if row:
            patient_id = row["User_Id"]
            visits = self.get_patient_visits(patient_id)
            consults = self.get_patient_consults(patient_id)
            return {
                "User_Id": row["User_Id"],
                "Name": row["Name"],
                "Surname": row["Surname"],
                "Gender": row["Gender"],
                "Birth_Date": row["Birthdate"],
                "Email": row["Email"],
                "Phone_Number": row["Phone_Number"],
                "Last_Visit": visits["last_visit"],
                "Next_Visit": visits["next_visit"],
                "Last_Consult": consults["last_consult"],
                "Next_Consult": consults["next_consult"],
                "Last_Consult_Note": consults["last_consult_note"],
                "Next_Consult_Note": consults["next_consult_note"]
            }
        return None


    def load_prescription(self, patient_id):
        """
        Retrieves all prescriptions for a given patient based on patient_id.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = """
        SELECT 
            V.Code AS visit_code,
            V.Date AS visit_date,
            P.Drug_Name AS medication,
            P.Dosage AS dosage,
            P.Frequency AS frequency,
            P.Text AS text,
            P.Therapy AS therapy
        FROM VISIT V
        JOIN Prescription P ON V.Code = P.Visit_Code
        WHERE V.Patient_Id = ?
        ORDER BY V.Date DESC
        """
        cursor.execute(query, (patient_id,))
        results = cursor.fetchall()
        conn.close()

        prescriptions = []
        for row in results:
            prescriptions.append({
            "id": row["visit_code"],  
            "visit_date": row["visit_date"],
            "medication": row["medication"],
            "dosage": row["dosage"],
            "frequency": row["frequency"],
            "text": row["text"],
            "therapy": row["therapy"]
        })

        return prescriptions


    def get_patient_list_for_doctor(self, doctor_id):
        """
        Retrieves all patients assigned to a specific doctor.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM patients WHERE doctor_id = ?"
        cursor.execute(query, (doctor_id,))
        patients = cursor.fetchall()
        conn.close()
        return patients
    

    def generate_visit_code(self, conn):
        """
        Generate a visit code.
        """
        cursor = conn.cursor()
        cursor.execute("SELECT Code FROM VISIT")
        existing_codes = {row[0] for row in cursor.fetchall()}

        base = 1000
        while True:
            code = f"VIS{base}"
            if code not in existing_codes:
                return code
            base += 1


    def create_new_prescription(self, patient_id, doctor_id, medication, dosage, frequency, text, therapy, date_prescribed):
        """
        Adds a new prescription for a given patient.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Generate unique visit code
            visit_code = self.generate_visit_code(conn)

            # Step 1: create the visit
            cursor.execute("""
            INSERT INTO VISIT (Code, Date, Patient_Id, Family_Doctor_Id)
            VALUES (?, ?, ?, ?)
            """, (visit_code, date_prescribed, patient_id, doctor_id))
            
            # Step 2: create the relative prescription
            cursor.execute("""
            INSERT INTO PRESCRIPTION (Visit_Code, Drug_Name, Dosage, Frequency, Text, Therapy)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (visit_code, medication, dosage, frequency, text, therapy))
        
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    def update_prescription(self, prescription_id, medication, dosage, frequency, text, therapy):
        """
        Updates an existing prescription.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = """
        UPDATE Prescription
        SET Drug_Name = ?, Dosage = ?, Frequency = ?, Text = ?, Therapy = ?
        WHERE Visit_Code = ?
        """
        cursor.execute(query, (medication, dosage, frequency, text, therapy, prescription_id))
        conn.commit()  
        conn.close()


    def delete_prescription(self, prescription_id):
        """
        Deletes a prescription and its associated visit.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            
            cursor.execute("DELETE FROM PRESCRIPTION WHERE Visit_Code = ?", (prescription_id,))
            
            cursor.execute("DELETE FROM VISIT WHERE Code = ?", (prescription_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    def create_user(self, username, password, role):
        """
        Creates a new user in the database (e.g., for registration).
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = """
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """
        cursor.execute(query, (username, password, role))
        conn.commit()  
        conn.close()
    

    def update_user_profile(self, user_id, phone, address, email, password):
        """
        Updates the password for a given family_doctor.
        This is useful for password reset functionality.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE USER
                SET Password = ?
                WHERE Id = ?
            """, (password, user_id))

            cursor.execute("""
                UPDATE Personal_Info
                SET Phone_Number = ?, Email = ?
                WHERE User_Id = ?
            """, (phone, email, user_id))

            cursor.execute("""
                UPDATE FAMILY_DOCTOR
                SET Clinic_Address = ?
                WHERE Family_Doctor_Id = ?
            """, (address, user_id))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e  
        finally:
            conn.close()


    def update_psychologist_profile(self, user_id, phone, address, email, password):
        """
        Updates the password for a given psychologist.
        This is useful for password reset functionality.
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE USER
                SET Password = ?
                WHERE Id = ?
            """, (password, user_id))

            cursor.execute("""
                UPDATE Personal_Info
                SET Phone_Number = ?, Email = ?
                WHERE User_Id = ?
            """, (phone, email, user_id))

            cursor.execute("""
                UPDATE PSYCHOLOGIST
                SET Clinic_Address = ?
                WHERE Psychologist_Id = ?
            """, (address, user_id))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    def get_visits_for_week(self, doctor_id, start_date, end_date):
        """
        Retrieves all visits for a doctor between start_date and end_date (YYYY-MM-DD).
        Returns a list of dictionaries with date, time, and patient full name.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT V.Date, V.Hour, PI.Name || ' ' || PI.Surname AS patient_name,
                PI.User_Id AS Patient_Id, PI.Name, PI.Surname
            FROM VISIT V
            JOIN Personal_Info PI ON V.Patient_Id = PI.User_Id
            WHERE V.Family_Doctor_Id = ? AND V.Date BETWEEN ? AND ?
        """
        cursor.execute(query, (doctor_id, start_date, end_date))
        results = cursor.fetchall()
        conn.close()
        return results


    def get_consults_for_week(self, psychologist_id, start_date, end_date):
        """
        Retrieves all psychological consults for a psychologist between start_date and end_date (YYYY-MM-DD).
        Returns a list of dictionaries with date, time, and patient full name.
        """
        conn = self.connect()
        cursor = conn.cursor()
        query = """
            SELECT C.Date, C.Hour, PI.Name || ' ' || PI.Surname AS patient_name,
                PI.User_Id AS Patient_Id, PI.Name, PI.Surname
            FROM CONSULT C
            JOIN Personal_Info PI ON C.Patient_Id = PI.User_Id
            WHERE C.Psychologist_Id = ? AND C.Date BETWEEN ? AND ?
        """
        cursor.execute(query, (psychologist_id, start_date, end_date))
        results = cursor.fetchall()
        conn.close()
        return results


    def add_appointment(self, doctor_id, date_str, time_str, patient_name):
        """
        Inserts a new appointment into the database for the specified doctor.
        Looks up the patient by their full name (exact Name + Surname match).
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Find patient ID by full name
        cursor.execute("""
            SELECT User_Id FROM Personal_Info
            WHERE Name || ' ' || Surname = ?
        """, (patient_name,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise ValueError("Patient not found.")

        patient_id = row["User_Id"]

        # Check if a visit already exists at the same time
        cursor.execute("""
            SELECT * FROM VISIT
            WHERE Date = ? AND Hour = ? AND Family_Doctor_Id = ?
        """, (date_str, time_str, doctor_id))
        if cursor.fetchone():
            conn.close()
            raise ValueError("An appointment already exists at this time.")

        # Insert the new visit
        cursor.execute("""
            INSERT INTO VISIT (Date, Hour, Patient_Id, Family_Doctor_Id)
            VALUES (?, ?, ?, ?)
        """, (date_str, time_str, patient_id, doctor_id))

        conn.commit()
        conn.close()


    def add_appointment_psychologist(self, psychologist_id, date_str, time_str, patient_name):
        """
        Inserts a new consult into the database for the specified psychologist.
        Looks up the patient by their full name (exact Name + Surname match).
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Find patient ID by full name
        cursor.execute("""
            SELECT User_Id FROM Personal_Info
            WHERE Name || ' ' || Surname = ?
        """, (patient_name,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise ValueError("Patient not found.")

        patient_id = row["User_Id"]

        # Check if a consult already exists at the same time
        cursor.execute("""
            SELECT * FROM CONSULT
            WHERE Date = ? AND Hour = ? AND Psychologist_Id = ?
        """, (date_str, time_str, psychologist_id))
        if cursor.fetchone():
            conn.close()
            raise ValueError("A consult already exists at this time.")

        # Insert the new consult
        cursor.execute("""
            INSERT INTO CONSULT (Date, Hour, Patient_Id, Psychologist_Id)
            VALUES (?, ?, ?, ?)
        """, (date_str, time_str, patient_id, psychologist_id))

        conn.commit()
        conn.close()


    def update_password(self, username, new_password):
        """
        Updates the password for the specified user (by username/ID).
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE USER SET Password = ?
                WHERE Id = ?
            """, (new_password, username))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
