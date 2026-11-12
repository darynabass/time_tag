"""
Діалог «Редагування працівника».
Отримує поточні дані працівника (ім'я, статус) і дозволяє їх змінити.
Поки без бекенду — після «Зберегти» лише пише в консоль.
"""

import customtkinter as ctk


class EditEmployeeDialog(ctk.CTkToplevel):
    """Модальне вікно редагування працівника."""

    def __init__(self, parent, name: str, status: str):
        super().__init__(parent)

        self.title("Редагування працівника")
        self.geometry("480x400")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#ffffff")

        # ---- Заголовок ----
        ctk.CTkLabel(
            self,
            text="✏️  Редагування працівника",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(25, 20))

        # ---- Поле "ПІБ" (заповнене поточним значенням) ----
        ctk.CTkLabel(
            self,
            text="ПІБ *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(0, 5))

        self._name_entry = ctk.CTkEntry(
            self,
            width=420,
            height=38,
            corner_radius=8,
        )
        self._name_entry.insert(0, name)
        self._name_entry.pack(padx=30)

        # ---- Поле "Статус" ----
        ctk.CTkLabel(
            self,
            text="Статус",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1f2a44",
        ).pack(anchor="w", padx=30, pady=(15, 5))

        self._status_var = ctk.StringVar(value=status)
        ctk.CTkOptionMenu(
            self,
            values=["На роботі", "Відсутній"],
            variable=self._status_var,
            width=420,
            height=38,
            corner_radius=8,
        ).pack(padx=30)

        # ---- Кнопки ----
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=30, pady=(30, 20))

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

    def _on_save(self):
        new_name = self._name_entry.get().strip()
        new_status = self._status_var.get()

        if not new_name:
            print("[debug] ПІБ не може бути порожнім")
            return

        print(f"[debug] Редагування працівника → нове ім'я='{new_name}', "
              f"статус='{new_status}'")
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")