"""
Модальне вікно успішної реєстрації.
Показується після зчитування картки, якщо працівник знайдений.
"""

import customtkinter as ctk


class SuccessDialog(ctk.CTkToplevel):
    """
    Діалог успіху.

    Використання:
        SuccessDialog(
            parent=app,
            name="Іваненко О.С.",
            status="Прихід",
            time="21.04.2025 14:32",
        )
    """

    def __init__(self, parent, name: str, status: str, time: str):
        super().__init__(parent)

        self.title("Успішно")
        self.geometry("420x340")
        self.resizable(False, False)

        # Модальне вікно: блокує взаємодію з головним, поки не закриють
        self.transient(parent)
        self.grab_set()

        # Кольори
        self.configure(fg_color="#f4fbf6")

        # --- Іконка ---
        ctk.CTkLabel(
            self,
            text="✅",
            font=ctk.CTkFont(size=56),
        ).pack(pady=(25, 10))

        # --- Заголовок ---
        ctk.CTkLabel(
            self,
            text="Успішно",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1f7a3d",
        ).pack()

        # --- Деталі ---
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.pack(pady=15, padx=30, fill="x")

        self._add_row(details_frame, "Працівник:", name)
        self._add_row(details_frame, "Статус:", status)
        self._add_row(details_frame, "Час:", time)

        # --- Кнопка "ОК" ---
        ctk.CTkButton(
            self,
            text="ОК",
            width=140,
            height=38,
            corner_radius=8,
            fg_color="#1f7a3d",
            hover_color="#155c2d",
            command=self.destroy,
        ).pack(pady=(10, 20))

        # Центруємо вікно відносно батька
        self._center_on_parent(parent)

    def _add_row(self, parent, label: str, value: str):
        """Один рядок "Підпис: значення"."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        ctk.CTkLabel(
            row,
            text=label,
            width=110,
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color="#555555",
        ).pack(side="left")

        ctk.CTkLabel(
            row,
            text=value,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222222",
        ).pack(side="left")

    def _center_on_parent(self, parent):
        """Розміщує діалог по центру батьківського вікна."""
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")