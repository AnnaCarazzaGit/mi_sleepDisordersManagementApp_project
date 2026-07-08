import customtkinter as ctk

# ---------------------------
# COLOR PALETTE - LIGHT 
# ---------------------------
COLORS = {
    "primary": "#5CA9E6",         # Bright blue
    "primary_hover": "#4997D0",   # Deeper hover blue
    "primary_pressed": "#3B87C0", # Clicked blue

    "secondary": "#80B5E5",       # Light pastel blue
    "secondary_hover": "#A4CCE9", # Hover secondary

    "background": "#A9D8F4",      # Soft sky blue
    "text": "#1F2937",            # Dark readable text
    "border": "#D0E3F0",           # Soft border color
    "card": "#FFFFFF"       
}

# ---------------------------
# FONT SETTINGS
# ---------------------------
FONT_FAMILY = "Segoe UI"
FONT_SIZES = {
    "small": 18,
    "medium": 22,
    "large": 30
}

# ---------------------------
# THEME MANAGEMENT
# ---------------------------
def set_theme(theme="light"):
    """Force light mode and apply appearance."""
    ctk.set_appearance_mode(theme)

def apply_window_style(window):
    """Apply global style to the root window."""
    window.configure(fg_color=COLORS["background"])

# ---------------------------
# BUTTONS
# ---------------------------
def create_primary_button(master, text, command=None, width=200, height=40):
    return ctk.CTkButton(
        master, text=text, command=command,
        width=width, height=height,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        text_color="white",
        corner_radius=12
    )

def create_secondary_button(master, text, command=None, width=160, height=40):
    return ctk.CTkButton(
        master, text=text, command=command,
        width=width, height=height,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        fg_color=COLORS["secondary"],
        hover_color=COLORS["secondary_hover"],
        text_color=COLORS["text"],
        corner_radius=12
    )

# ---------------------------
# ENTRIES
# ---------------------------
def create_entry(master, placeholder_text="", show=None, width=220, height=40):
    return ctk.CTkEntry(
        master, placeholder_text=placeholder_text,
        show=show, width=width, height=height,
        font=(FONT_FAMILY, FONT_SIZES["medium"])
    )

def create_readonly_entry(master, text, width=220, height=40):
    entry = ctk.CTkEntry(
        master, width=width, height=height,
        font=(FONT_FAMILY, FONT_SIZES["medium"])
    )
    entry.insert(0, text)
    entry.configure(state="disabled")
    return entry

# ---------------------------
# LABELS
# ---------------------------
def create_label(master, text, size=18, color=None, **kwargs):
    if color is None:
        color = COLORS["text"]
    return ctk.CTkLabel(
        master, text=text,
        font=(FONT_FAMILY, size),
        text_color=color,
        **kwargs
    )

# ---------------------------
# FRAMES
# ---------------------------
def create_frame(master, width=200, height=100, bg_color=None):
    if bg_color is None:
        bg_color = COLORS["background"]
    return ctk.CTkFrame(
        master, width=width, height=height,
        fg_color=bg_color,
        corner_radius=12,
        border_width=1,
        border_color="#4D4D4D"
    )

# ---------------------------
# DROPDOWN
# ---------------------------
def create_dropdown(master, options, command=None, width=220):
    var = ctk.StringVar(value=options[0])
    dropdown = ctk.CTkOptionMenu(
        master,
        values=options,
        variable=var,
        command=command,
        width=width,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        fg_color=COLORS["primary"],
        button_color=COLORS["primary_hover"],
        button_hover_color=COLORS["primary_pressed"],
        dropdown_font=(FONT_FAMILY, FONT_SIZES["medium"]),
        text_color="white"
    )
    return dropdown, var

# ---------------------------
# CHECKBOX
# ---------------------------
def create_checkbox(master, text, command=None, width=160, height=30):
    return ctk.CTkCheckBox(
        master, text=text, command=command,
        width=width, height=height,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        text_color=COLORS["text"],
        fg_color=COLORS["primary"]
    )

# ---------------------------
# RADIO BUTTON
# ---------------------------
def create_radiobutton(master, text, variable, value, command=None, width=160, height=30):
    return ctk.CTkRadioButton(
        master, text=text, variable=variable, value=value, command=command,
        width=width, height=height,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        text_color=COLORS["text"],
        fg_color=COLORS["primary"]
    )

# ---------------------------
# SLIDER
# ---------------------------
def create_slider(master, command=None, width=220, height=28, from_=0, to=100, number_of_steps=100):
    return ctk.CTkSlider(
        master, command=command,
        width=width, height=height,
        from_=from_, to=to,
        number_of_steps=number_of_steps,
        button_color=COLORS["primary"],
        progress_color=COLORS["primary_hover"]
    )

# ---------------------------
# CUSTOM ERROR POPUP
# ---------------------------
def show_custom_error(master, title="Error", message="Something went wrong."):
    popup = ctk.CTkToplevel(master)
    popup.title(title)
    popup.geometry("400x300")
    popup.resizable(False, False)
    popup.configure(fg_color=COLORS["background"])
    popup.grab_set()

    # Red title
    title_label = ctk.CTkLabel(
        popup, text=title,
        font=(FONT_FAMILY, FONT_SIZES["large"]),
        text_color="red"
    )
    title_label.pack(pady=(20, 10))

    # Message
    msg_label = ctk.CTkLabel(
        popup, text=message,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        text_color=COLORS["text"],
        wraplength=360,
        justify="center"
    )
    msg_label.pack(pady=(0, 20))

    # Close button
    close_btn = create_primary_button(popup, text="Close", command=popup.destroy)
    close_btn.pack()

    # Center the popup relative to parent
    popup.update_idletasks()
    x = master.winfo_x() + (master.winfo_width() // 2) - (popup.winfo_width() // 2)
    y = master.winfo_y() + (master.winfo_height() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")

# ---------------------------
# CUSTOM WARNING POPUP
# ---------------------------
def show_custom_warning(master, title="Warning", message="Attention required."):
    popup = ctk.CTkToplevel(master)
    popup.title(title)
    popup.geometry("400x300")
    popup.resizable(False, False)
    popup.configure(fg_color=COLORS["background"])
    popup.grab_set()

    # Amber/orange title
    title_label = ctk.CTkLabel(
        popup, text=title,
        font=(FONT_FAMILY, FONT_SIZES["large"]),
        text_color="#D97706"  # amber orange for warning
    )
    title_label.pack(pady=(20, 10))

    # Message
    msg_label = ctk.CTkLabel(
        popup, text=message,
        font=(FONT_FAMILY, FONT_SIZES["medium"]),
        text_color=COLORS["text"],
        wraplength=360,
        justify="center"
    )
    msg_label.pack(pady=(0, 20))

    # Close button
    close_btn = create_primary_button(popup, text="Close", command=popup.destroy)
    close_btn.pack()

    # Center the popup relative to parent
    popup.update_idletasks()
    x = master.winfo_x() + (master.winfo_width() // 2) - (popup.winfo_width() // 2)
    y = master.winfo_y() + (master.winfo_height() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")
