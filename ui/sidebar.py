"""
Ліва бічна панель з навігацією та годинником.
"""

import customtkinter as ctk
from datetime import datetime


class Sidebar(ctk.CTkFrame):
    """Бічна панель: логотип, кнопки навігації, годинник."""

    def __init__(self, master, on_navigate=None):
        super().__init__(master, width=220, corner_radius=0, fg_color="#1f2a44")
        self.on_navigate = on_navigate

        # Притискаємо годинник донизу
        self.grid_rowconfigure(10, weight=1)

        # --- Логотип ---
        ctk.CTkLabel(
            self,
            text="⏱ FokusFlow",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white",
        ).grid(row=0, column=0, padx=20, pady=(20, 25), sticky="w")

        # --- Кнопки навігації ---
        nav_items = [
            ("🏠  Головна", "home"),
            ("📊  Звіти", "reports"),
            ("🔐  Адмін-панель", "admin"),
        ]

        for i, (label, key) in enumerate(nav_items, start=1):
            ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color="#2d3b5e",
                text_color="white",
                font=ctk.CTkFont(size=14),
                command=lambda k=key: self._handle_click(k),
            ).grid(row=i, column=0, padx=12, pady=4, sticky="ew")

        # --- Годинник ---
        self.clock_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#aab3c5",
            justify="left",
        )
        self.clock_label.grid(row=11, column=0, padx=20, pady=15, sticky="sw")

        self._tick_clock()

    def _handle_click(self, key: str):
        if self.on_navigate:
            self.on_navigate(key)

    def _tick_clock(self):
        now = datetime.now().strftime("%H:%M:%S\n%d.%m.%Y")
        self.clock_label.configure(text=now)
        self.after(1000, self._tick_clock)