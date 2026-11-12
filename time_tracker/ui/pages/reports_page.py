"""
Сторінка «Звіти».
Поки що — візуальна заглушка з фейковими даними.
Пізніше: реальні дані з БД + фільтри + експорт в Excel.
"""

import customtkinter as ctk


class ReportsPage(ctk.CTkFrame):
    """Сторінка звітів відвідувань."""

    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="white")

        # Фейкові дані (пізніше — з БД)
        self._reports = [
            {"date": "21.04.2025", "name": "Іваненко О.С.",
             "in": "08:55", "out": "17:30", "hours": "8:35"},
            {"date": "21.04.2025", "name": "Петренко М.В.",
             "in": "09:02", "out": "18:00", "hours": "8:58"},
            {"date": "20.04.2025", "name": "Коваленко А.І.",
             "in": "08:45", "out": "17:15", "hours": "8:30"},
            {"date": "20.04.2025", "name": "Шевченко Т.П.",
             "in": "09:10", "out": "18:05", "hours": "8:55"},
            {"date": "19.04.2025", "name": "Бондаренко І.В.",
             "in": "08:30", "out": "17:00", "hours": "8:30"},
        ]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # ---- Заголовок ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 20))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Звіти відвідувань",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1f2a44",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Перегляд та експорт даних про робочий час",
            font=ctk.CTkFont(size=13),
            text_color="#667085",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        # ---- Таблиця ----
        table_frame = ctk.CTkFrame(
            self, fg_color="#ffffff",
            corner_radius=12,
            border_width=1, border_color="#e1e7f0",
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 20))
        table_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Шапка таблиці
        headers = ["Дата", "Працівник", "Прихід", "Вихід", "Відпрацьовано"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                table_frame,
                text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#1f2a44",
                anchor="w",
            ).grid(row=0, column=col, padx=15, pady=(15, 10), sticky="w")

        # Розділювач
        ctk.CTkFrame(
            table_frame, fg_color="#e1e7f0", height=1,
        ).grid(row=1, column=0, columnspan=5, sticky="ew", padx=15)

        # Рядки з даними
        for i, row_data in enumerate(self._reports, start=2):
            values = [
                row_data["date"],
                row_data["name"],
                row_data["in"],
                row_data["out"],
                row_data["hours"],
            ]
            for col, val in enumerate(values):
                ctk.CTkLabel(
                    table_frame,
                    text=val,
                    font=ctk.CTkFont(size=13),
                    text_color="#222222",
                    anchor="w",
                ).grid(row=i, column=col, padx=15, pady=8, sticky="w")

        # ---- Панель кнопок ----
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 30))

        ctk.CTkButton(
            actions,
            text="📥  Експорт в Excel",
            width=180,
            height=40,
            corner_radius=10,
            command=self._on_export,
        ).pack(side="left")

        ctk.CTkButton(
            actions,
            text="🔄  Оновити",
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#e1e7f0",
            hover_color="#d0d8e5",
            text_color="#1f2a44",
            command=self._on_refresh,
        ).pack(side="left", padx=(10, 0))

    def _on_export(self):
        print("[debug] Експорт в Excel — логіка ще не підключена")

    def _on_refresh(self):
        print("[debug] Оновлення звітів — логіка ще не підключена")