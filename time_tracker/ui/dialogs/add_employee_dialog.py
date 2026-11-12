"""
Діалог «Додавання працівника».
Поки без бекенду — після натискання «Зберегти» лише виводить дані в консоль.
"""

import customtkinter as ctk


class AddEmployeeDialog(ctk.CTkToplevel):
    """Модальне вікно додавання нового працівника."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Додавання працівника")
        self.geometry("480x460")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#ffffff")

        # ---- Заголовок ----
        ctk.CTkLabel(
            self,
            text="👤  Додавання працівника",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(25, 20))

        # ---- Поле "ПІБ" ----
        self._name_entry = self._add_field(
            label="ПІБ *",
            placeholder="Прізвище Ім'я По батькові",
        )

        # ---- Поле "Статус" ----
        ctk.CTkLabel(
            self,
            text="Статус",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(15, 5))

        self._status_var = ctk.StringVar(value="На роботі")
        ctk.CTkOptionMenu(
            self,
            values=["На роботі", "Відсутній"],
            variable=self._status_var,
            width=420,
            height=38,
            corner_radius=8,
        ).pack(padx=30)

        # ---- Поле "RFID-картка" ----
        ctk.CTkLabel(
            self,
            text="RFID-картка",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(15, 5))

        card_frame = ctk.CTkFrame(
            self, fg_color="#f4f7fb",
            corner_radius=8,
            border_width=1, border_color="#e1e7f0",
        )
        card_frame.pack(padx=30, fill="x")

        ctk.CTkLabel(
            card_frame,
            text="📡  Піднесіть картку до зчитувача",
            font=ctk.CTkFont(size=13),
            text_color="#667085",
        ).pack(pady=12)

        # ---- Кнопки ----
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=30, pady=(25, 20))

        ctk.CTkButton(
            buttons,
            text="Скасувати",
            width=200,
            height=40,
            corner_radius=8,
            fg_color="#e1e7f0",
            hover_color="#d0d8e5",
            text_color="#1f2a44",
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            buttons,
            text="Зберегти",
            width=200,
            height=40,
            corner_radius=8,
            command=self._on_save,
        ).pack(side="right")

        self._center_on_parent(parent)

    def _add_field(self, label: str, placeholder: str) -> ctk.CTkEntry:
        """Додає підпис + поле вводу."""
        ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(0, 5))

        entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            width=420,
            height=38,
            corner_radius=8,
        )
        entry.pack(padx=30)
        return entry

    def _on_save(self):
        """Тимчасовий обробник — виводить дані в консоль."""
        name = self._name_entry.get().strip()
        status = self._status_var.get()

        if not name:
            print("[debug] ПІБ не заповнено — збереження скасовано")
            return

        print(f"[debug] Додавання працівника → ПІБ='{name}', статус='{status}'")
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")