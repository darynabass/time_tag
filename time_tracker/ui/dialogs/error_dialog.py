"""
Модальне вікно помилки.
Показується, якщо картка невідома або незареєстрована.
"""

import customtkinter as ctk


class ErrorDialog(ctk.CTkToplevel):
    """
    Діалог помилки.

    Використання:
        ErrorDialog(parent=app, message="Невідома або незареєстрована картка.")
    """

    def __init__(self, parent, message: str):
        super().__init__(parent)

        self.title("Помилка")
        self.geometry("420x300")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color="#fdf3f3")

        # --- Іконка ---
        ctk.CTkLabel(
            self,
            text="❌",
            font=ctk.CTkFont(size=56),
        ).pack(pady=(25, 10))

        # --- Заголовок ---
        ctk.CTkLabel(
            self,
            text="Помилка",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#b3261e",
        ).pack()

        # --- Повідомлення ---
        ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="#444444",
            wraplength=340,
            justify="center",
        ).pack(pady=(10, 20), padx=30)

        # --- Кнопка "ОК" ---
        ctk.CTkButton(
            self,
            text="ОК",
            width=140,
            height=38,
            corner_radius=8,
            fg_color="#b3261e",
            hover_color="#8f1d16",
            command=self.destroy,
        ).pack(pady=(0, 20))

        self._center_on_parent(parent)

    def _center_on_parent(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")