import customtkinter as ctk
from ui.login_selector import LoginSelector  
from ui.style_ctk import set_theme, apply_window_style

def main():
    # Create the main application window
    root = ctk.CTk()
    root.title("Advanced Sleep Evaluation")
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")

    # Set the initial theme and apply global styling
    set_theme("light")
    apply_window_style(root)

    # Load the main application interface
    LoginSelector(root)

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
