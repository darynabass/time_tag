"""Main entry point for the TimeTag application."""

from database.database import create_database

import customtkinter as ctk

from ui.main_window import MainWindow


def main():
    """Initialize the application database."""
    create_database()
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()