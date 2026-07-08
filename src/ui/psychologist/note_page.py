import customtkinter as ctk
from ui.style_ctk import *
import math

class PsychologistNotesPage(ctk.CTkFrame):
    def __init__(self, master, main_window, patient_id=None):
        super().__init__(master, fg_color=COLORS["background"])
        self.main_window = main_window
        self.patient_id = patient_id
        self.notes = []

        create_label(self, text="Session Notes", size=FONT_SIZES["large"]).pack(pady=20)

        # Back button
        create_secondary_button(self, text="Back", command=lambda: self.main_window.show_page("patient_psychologist")).pack(pady=10)

        # Scrollable section for existing notes
        container = ctk.CTkFrame(self)
        container.pack(pady=10, padx=20, fill="both", expand=True)

        canvas = ctk.CTkCanvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        self.notes_frame = ctk.CTkFrame(canvas)

        self.notes_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.notes_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.add_note("The last session went well. The patient was responsive and open.\nSuggested breathing exercises and follow-up in two weeks.")

        self.save_all_button = create_primary_button(self, text="Save Changes to Notes", command=self.save_all_notes)
        self.save_all_button.pack(pady=(10, 15))

        # Visual separator
        ctk.CTkLabel(self, text="────────────────────────────────────────", text_color="gray").pack(pady=15)

        # Section to add new notes
        create_label(self, text="Add New Note:", size=FONT_SIZES["medium"]).pack(pady=(5, 5))

        self.new_note_box = ctk.CTkTextbox(
            self,
            width=700,
            height=100,
            font=("Helvetica", 18),
            wrap="word",
            corner_radius=10,
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CCCCCC"
        )
        self.new_note_box.pack(pady=(0, 10))

        self.save_button = create_primary_button(self, text="Add Note", command=self.save_new_note)
        self.save_button.pack(pady=10)

    def go_back(self):
        self.pack_forget()
        self.destroy()
        self.main_window.show_main_view()  # Assumendo che main_window abbia questo metodo

    def calculate_height(self, text):
        lines = text.count("\n") + math.ceil(len(text) / 80)
        return max(4, min(lines, 20)) * 20

    def add_note(self, text):
        height = self.calculate_height(text)

        note_box = ctk.CTkTextbox(
            self.notes_frame,
            width=700,
            height=height,
            font=("Helvetica", 18),
            wrap="word",
            corner_radius=10,
            fg_color="white",
            text_color="black",
            border_width=1,
            border_color="#CCCCCC"
        )
        note_box.pack(pady=(15, 5), padx=20)
        note_box.insert("1.0", text)
        self.notes.append({"textbox": note_box})

    def save_new_note(self):
        new_text = self.new_note_box.get("1.0", "end").strip()
        if new_text:
            self.add_note(new_text)
            self.new_note_box.delete("1.0", "end")
            show_custom_warning(self, title="Saved", message="New note added in memory.")
        else:
            show_custom_warning(self, title="Empty", message="Please enter a note before saving.")

    def save_all_notes(self):
        updated_notes = []
        for note in self.notes:
            text = note["textbox"].get("1.0", "end").strip()
            updated_notes.append(text)

        show_custom_warning(self, title="Saved", message=f"{len(updated_notes)} notes updated in memory.")
