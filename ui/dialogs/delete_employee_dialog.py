"""
Діалог «Видалення працівника» — підтвердження.
"""

import customtkinter as ctk


class DeleteEmployeeDialog(ctk.CTkToplevel):
    """Модальне вікно підтвердження видалення."""

    def __init__(self, parent, name: str):
        super().__init__(parent)

        self.title("Видалення працівника")
        self.geometry("440x300")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#fdf3f3")

        # ---- Іконка ----
        ctk.CTkLabel(
            self,
            text="⚠️",
            font=ctk.CTkFont(size=52),
        ).pack(pady=(25, 8))

        # ---- Заголовок ----
        ctk.CTkLabel(
            self,
            text="Видалити працівника?",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#b3261e",
        ).pack()

        # ---- Текст ----
        ctk.CTkLabel(
            self,
            text=f"Ви дійсно хочете видалити працівника\n«{name}»?",
            font=ctk.CTkFont(size=13),
            text_color="#444444",
            justify="center",
        ).pack(pady=(8, 6))

        ctk.CTkLabel(
            self,
            text="Цю дію неможливо буде скасувати.",
            font=ctk.CTkFont(size=12),
            text_color="#8f1d16",
        ).pack()

        # ---- Кнопки ----
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=30, pady=(20, 20))

        ctk.CTkButton(
            buttons,
            text="Скасувати",
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#e1e7f0",
            hover_color="#d0d8e5",
            text_color="#1f2a44",
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            buttons,
            text="Видалити",
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#b3261e",
            hover_color="#8f1d16",
            command=lambda: self._on_confirm(name),
        ).pack(side="right")

        self._center_on_parent(parent)

    def _on_confirm(self, name: str):
        print(f"[debug] Видалення працівника: '{name}'")
        self.destroy()

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{px + (pw - w)//2}+{py + (ph - h)//2}")