"""
Головне вікно застосунку.
Складається з Sidebar (ліворуч) + центральна зона зі сторінками (праворуч).
"""

import customtkinter as ctk

from ui.sidebar import Sidebar
from ui.pages.home_page import HomePage
from ui.pages.reports_page import ReportsPage
from ui.pages.admin_page import AdminPage

from services.controllers.rfid_controller import RFIDController


class MainWindow(ctk.CTk):
    """Головне вікно програми."""

    def __init__(self):
        super().__init__()

        self.title("Трекер робочого часу")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # RFID Controller
        self.rfid_controller = RFIDController()
        self.current_page = None

        # --- Ліва панель ---
        self.sidebar = Sidebar(self, on_navigate=self._on_navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # --- Центральна зона ---
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # --- Створюємо всі сторінки один раз ---
        # Усі вони лежать в одній комірці (0,0) одна на одній.
        # Показ потрібної — через tkraise().
        self.pages = {
            "home": HomePage(self.content, self.rfid_controller),
            "reports": ReportsPage(self.content),
            "admin": AdminPage(self.content, self.rfid_controller),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        # За замовчуванням — головна
        self._show_page("home")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    #  Навігація
    # ------------------------------------------------------------------
    def _on_navigate(self, key: str):
        """Викликається з sidebar при кліку на кнопку."""
        if key in self.pages:
            self._show_page(key)
        else:
            print(f"[nav] Невідома сторінка: {key}")

    def _show_page(self, key: str):
        """Піднімає потрібну сторінку на передній план."""

        if self.current_page is not None:
            on_hide = getattr(self.current_page, "on_hide", None)
            if callable(on_hide):
                on_hide()

        page = self.pages[key]
        page.tkraise()
        self.current_page = page

        on_show = getattr(page, "on_show", None)
        if callable(on_show):
            on_show()

        print(f"[nav] Показано сторінку: {key}")

    def _on_close(self):
        """Зупиняє RFID-зчитувач перед закриттям програми."""

        if self.current_page is not None:
            on_hide = getattr(self.current_page, "on_hide", None)
            if callable(on_hide):
                on_hide()

        self.destroy()