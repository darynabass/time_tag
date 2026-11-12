"""
Точка входу програми.
Запуск:  python app.py
"""

import customtkinter as ctk

from ui.main_window import MainWindow


def main():
    # Глобальні налаштування теми
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()