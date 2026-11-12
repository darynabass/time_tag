"""
Головний екран: очікування картки + останні події.
"""

import customtkinter as ctk
from datetime import datetime

from ui.dialogs.success_dialog import SuccessDialog
from ui.dialogs.error_dialog import ErrorDialog


class HomePage(ctk.CTkFrame):
    """Центральна зона: очікування картки + список останніх подій."""

    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="white")

        # Лічильник для тестування (успіх/помилка по черзі)
        self._sim_counter = 0

        # Список подій — поки що заповнюємо фейковими даними.
        # Кожен елемент: {"name": str, "status": str, "time": str}
        # Коли буде бекенд — цей список братиметься з БД.
        self._events = [
            {"name": "Іваненко О.С.", "status": "Прихід", "time": "21.04.2025 14:32"},
            {"name": "Петренко М.В.", "status": "Вихід",  "time": "20.04.2025 17:10"},
        ]

        self._build_ui()

    # ------------------------------------------------------------------
    #  Побудова UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Дві колонки: ліворуч — очікування, праворуч — статус + події."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- Ліва колонка: очікування картки ----
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 20), pady=40)

        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=1)

        center_box = ctk.CTkFrame(left, fg_color="transparent")
        center_box.grid(row=0, column=0)

        ctk.CTkLabel(
            center_box,
            text="📡",
            font=ctk.CTkFont(size=90),
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            center_box,
            text="Очікування RFID-картки",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#1f2a44",
        ).pack()

        ctk.CTkLabel(
            center_box,
            text="Піднесіть картку до зчитувача",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(pady=(5, 30))

        ctk.CTkButton(
            center_box,
            text="Симулювати зчитування",
            width=220,
            height=40,
            corner_radius=10,
            command=self._on_simulate_scan,
        ).pack()

        # ---- Права колонка: статус + останні події ----
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(20, 40), pady=40)
        right.grid_columnconfigure(0, weight=1)

        # --- Блок "Поточний статус" ---
        status_card = ctk.CTkFrame(
            right, corner_radius=14,
            fg_color="#f4f7fb",
            border_width=1, border_color="#e1e7f0",
        )
        status_card.grid(row=0, column=0, sticky="ew", pady=(40, 15))
        status_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            status_card,
            text="Поточний статус",
            font=ctk.CTkFont(size=13),
            text_color="#667085",
        ).grid(row=0, column=0, padx=(20, 10), pady=(15, 0), sticky="w")

        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.grid(row=1, column=0, columnspan=2,
                        padx=20, pady=(4, 15), sticky="w")

        # Зелений кружечок
        ctk.CTkLabel(
            status_row,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color="#2ecc71",
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            status_row,
            text="На роботі",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#222222",
        ).pack(side="left")

        # --- Блок "Останні події" ---
        events_card = ctk.CTkFrame(
            right, corner_radius=14,
            fg_color="#ffffff",
            border_width=1, border_color="#e1e7f0",
        )
        events_card.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        events_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            events_card,
            text="Останні події",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#1f2a44",
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Контейнер для рядків подій — його вміст перемальовується
        # при кожному оновленні списку.
        self.events_list = ctk.CTkFrame(events_card, fg_color="transparent")
        self.events_list.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self._render_events()

    # ------------------------------------------------------------------
    #  Рендер списку подій
    # ------------------------------------------------------------------
    def _render_events(self):
        """Перемальовує список останніх подій."""
        # Очищаємо контейнер
        for w in self.events_list.winfo_children():
            w.destroy()

        for ev in self._events:
            row = ctk.CTkFrame(self.events_list, fg_color="transparent")
            row.pack(fill="x", pady=6)

            # Іконка статусу (кольорова крапка)
            color = "#2ecc71" if ev["status"] == "Прихід" else "#e74c3c"
            ctk.CTkLabel(
                row, text="●",
                font=ctk.CTkFont(size=14),
                text_color=color,
            ).pack(side="left", padx=(10, 8))

            # ПІБ
            ctk.CTkLabel(
                row,
                text=ev["name"],
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#222222",
            ).pack(side="left")

            # Час (праворуч)
            ctk.CTkLabel(
                row,
                text=ev["time"],
                font=ctk.CTkFont(size=12),
                text_color="#667085",
            ).pack(side="right", padx=(0, 10))

            # Статус
            ctk.CTkLabel(
                row,
                text=ev["status"],
                font=ctk.CTkFont(size=12),
                text_color=color,
            ).pack(side="right", padx=(0, 12))

    # ------------------------------------------------------------------
    #  Обробник кліку "Симулювати зчитування"
    # ------------------------------------------------------------------
    def _on_simulate_scan(self):
        """
        Тимчасовий обробник: по черзі — успіх/помилка.
        На наступному етапі замінимо на реальний виклик бекенду.
        """
        root = self.winfo_toplevel()

        if self._sim_counter % 2 == 0:
            # --- Успіх ---
            name = "Іваненко О.С."
            status = "Прихід"
            time_str = datetime.now().strftime("%d.%m.%Y %H:%M")

            # Додаємо подію в список і перемальовуємо
            self._events.insert(0, {
                "name": name,
                "status": status,
                "time": time_str,
            })
            self._events = self._events[:5]  # тримаємо максимум 5 останніх
            self._render_events()

            # Показуємо діалог
            SuccessDialog(
                parent=root,
                name=name,
                status=status,
                time=time_str,
            )
        else:
            # --- Помилка ---
            ErrorDialog(
                parent=root,
                message="Невідома або незареєстрована картка.",
            )

        self._sim_counter += 1