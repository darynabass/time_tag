"""
Сторінка «Адмін-панель».
Має два стани: екран входу та панель після авторизації.
"""

import customtkinter as ctk

from ui.dialogs.add_employee_dialog import AddEmployeeDialog
from ui.dialogs.edit_employee_dialog import EditEmployeeDialog
from ui.dialogs.delete_employee_dialog import DeleteEmployeeDialog
from ui.dialogs.manual_note_dialog import ManualNoteDialog


class AdminPage(ctk.CTkFrame):
    """Сторінка адміністратора."""

    # Фейковий працівник для тестування «Редагувати» та «Видалити»
    SAMPLE_EMPLOYEE = "Іваненко О.С."

    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="white")

        self._is_authorized = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._login_view = self._build_login_view()
        self._panel_view = self._build_panel_view()

        self._login_view.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    #  Екран входу
    # ------------------------------------------------------------------
    def _build_login_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(0, weight=1)

        box = ctk.CTkFrame(view, fg_color="transparent")
        box.grid(row=0, column=0)

        ctk.CTkLabel(
            box, text="🔐", font=ctk.CTkFont(size=80),
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            box,
            text="Авторизація адміністратора",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1f2a44",
        ).pack()

        ctk.CTkLabel(
            box,
            text="Піднесіть адмін-картку до зчитувача",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(pady=(5, 30))

        ctk.CTkButton(
            box,
            text="Симулювати вхід",
            width=220,
            height=40,
            corner_radius=10,
            command=self._on_simulate_login,
        ).pack()

        return view

    # ------------------------------------------------------------------
    #  Панель адміністратора
    # ------------------------------------------------------------------
    def _build_panel_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)
        view.grid_rowconfigure(1, weight=1)

        # Заголовок
        header = ctk.CTkFrame(view, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 20))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Панель адміністратора",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1f2a44",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="Вийти",
            width=100,
            height=34,
            corner_radius=8,
            fg_color="#b3261e",
            hover_color="#8f1d16",
            command=self._on_logout,
        ).grid(row=0, column=1, sticky="e")

        # Тіло
        body = ctk.CTkFrame(
            view, fg_color="#f4f7fb",
            corner_radius=12,
            border_width=1, border_color="#e1e7f0",
        )
        body.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 30))
        body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            body,
            text="Управління працівниками",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1f2a44",
        ).grid(row=0, column=0, padx=25, pady=(20, 4), sticky="w")

        ctk.CTkLabel(
            body,
            text="Оберіть дію. Усі операції поки що працюють без реального бекенду.",
            font=ctk.CTkFont(size=13),
            text_color="#667085",
            justify="left",
        ).grid(row=1, column=0, padx=25, pady=(0, 20), sticky="w")

        actions_frame = ctk.CTkFrame(body, fg_color="transparent")
        actions_frame.grid(row=2, column=0, padx=25, pady=(0, 25), sticky="w")

        # Прив'язуємо кожну кнопку до свого методу
        buttons = [
            ("➕ Додати працівника", self._open_add_dialog),
            ("✏️ Редагувати",       self._open_edit_dialog),
            ("🗑 Видалити",          self._open_delete_dialog),
            ("🔁 Ручна відмітка",    self._open_manual_note_dialog),
        ]
        for label, handler in buttons:
            ctk.CTkButton(
                actions_frame,
                text=label,
                width=190,
                height=36,
                corner_radius=8,
                fg_color="#e1e7f0",
                hover_color="#d0d8e5",
                text_color="#1f2a44",
                command=handler,
            ).pack(side="left", padx=(0, 8))

        return view

    # ------------------------------------------------------------------
    #  Перемикання станів
    # ------------------------------------------------------------------
    def _on_simulate_login(self):
        print("[debug] Симуляція входу адміністратора")
        self._is_authorized = True
        self._login_view.grid_forget()
        self._panel_view.grid(row=0, column=0, sticky="nsew")

    def _on_logout(self):
        print("[debug] Вихід із панелі адміністратора")
        self._is_authorized = False
        self._panel_view.grid_forget()
        self._login_view.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    #  Відкриття діалогів
    # ------------------------------------------------------------------
    def _get_parent_window(self):
        """
        Повертає кореневе вікно (MainWindow) для центрування діалогів.
        ВАЖЛИВО: назва НЕ '_root' — щоб не конфліктувати з внутрішнім
        методом customtkinter.
        """
        return self.winfo_toplevel()

    def _open_add_dialog(self):
        AddEmployeeDialog(self._get_parent_window())

    def _open_edit_dialog(self):
        EditEmployeeDialog(
            self._get_parent_window(),
            name=self.SAMPLE_EMPLOYEE,
            status="На роботі",
        )

    def _open_delete_dialog(self):
        DeleteEmployeeDialog(self._get_parent_window(), name=self.SAMPLE_EMPLOYEE)

    def _open_manual_note_dialog(self):
        ManualNoteDialog(self._get_parent_window(), employee_name=self.SAMPLE_EMPLOYEE)