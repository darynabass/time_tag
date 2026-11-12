"""
Діалог «Ручна відмітка» (тільки для адміністратора).
Дозволяє вручну зафіксувати прихід/вихід працівника.
"""

import customtkinter as ctk


class ManualNoteDialog(ctk.CTkToplevel):
    """Модальне вікно ручної відмітки."""

    def __init__(self, parent, employee_name: str):
        super().__init__(parent)

        self.title("Ручна відмітка")
        self.geometry("480x420")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#ffffff")

        # ---- Заголовок ----
        ctk.CTkLabel(
            self,
            text="🔁  Ручна відмітка",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(25, 20))

        # ---- Працівник ----
        ctk.CTkLabel(
            self,
            text="Працівник *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(0, 5))

        self._name_entry = ctk.CTkEntry(
            self, width=420, height=38, corner_radius=8,
        )
        self._name_entry.insert(0, employee_name)
        self._name_entry.pack(padx=30)

        # ---- Дата й час ----
        ctk.CTkLabel(
            self,
            text="Дата та час",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(15, 5))

        dt_row = ctk.CTkFrame(self, fg_color="transparent")
        dt_row.pack(padx=30, fill="x")

        self._date_entry = ctk.CTkEntry(
            dt_row, placeholder_text="дд.мм.рррр", width=200, height=38,
            corner_radius=8,
        )
        self._date_entry.pack(side="left")

        self._time_entry = ctk.CTkEntry(
            dt_row, placeholder_text="гг:хх", width=200, height=38,
            corner_radius=8,
        )
        self._time_entry.pack(side="right")

        # ---- Тип події ----
        ctk.CTkLabel(
            self,
            text="Тип події",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(15, 5))

        self._event_var = ctk.StringVar(value="Прихід")
        ctk.CTkSegmentedButton(
            self,
            values=["Прихід", "Вихід"],
            variable=self._event_var,
            width=420,
            height=38,
            corner_radius=8,
        ).pack(padx=30)

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
            text="Підтвердити",
            width=200,
            height=40,
            corner_radius=8,
            command=self._on_confirm,
        ).pack(side="right")

        # ---- Підказка ----
        ctk.CTkLabel(
            self,
            text="Програма автоматично визначить, чи це прихід чи вихід,\n"
                 "залежно від останнього запису працівника.",
            font=ctk.CTkFont(size=11),
            text_color="#667085",
            justify="center",
        ).pack(pady=(0, 10))

        self._center_on_parent(parent)

    def _on_confirm(self):
        name = self._name_entry.get().strip()
        date = self._date_entry.get().strip()
        time = self._time_entry.get().strip()
        event = self._event_var.get()

        if not name:
            print("[debug] Працівник не вказаний")
            return

        print(f"[debug] Ручна відмітка → '{name}', {date or '—'} {time or '—'}, "
              f"подія='{event}'")
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")