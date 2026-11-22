"""
Сторінка «Адмін-панель».
Має два стани: екран входу та панель після авторизації.
"""

import customtkinter as ctk

from ui.dialogs.add_employee_dialog import AddEmployeeDialog
from ui.dialogs.edit_employee_dialog import EditEmployeeDialog
from ui.dialogs.delete_employee_dialog import DeleteEmployeeDialog
from ui.dialogs.manual_note_dialog import ManualNoteDialog
from services.check_admin import (
    AdminAccessError,
    check_admin_card,
    create_first_admin,
    has_usable_admin,
)


class AdminPage(ctk.CTkFrame):
    """Сторінка адміністратора."""

    # Фейковий працівник для тестування «Редагувати» та «Видалити»
    SAMPLE_EMPLOYEE = "Іваненко О.С."

    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="white")

        self._is_authorized = False
        self._admin = None  # дані адміністратора після входу

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
        self._login_box = box

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

        # Зчитувач працює як клавіатура: «набирає» UID картки й натискає Enter.
        # Тому достатньо, щоб це поле було у фокусі. UID приховано символами «•».
        self._card_entry = ctk.CTkEntry(
            box,
            width=260,
            height=40,
            show="•",
            justify="center",
            placeholder_text="UID картки",
        )
        self._card_entry.pack()
        self._card_entry.bind("<Return>", self._on_card_submitted)
        self._card_entry.bind("<KP_Enter>", self._on_card_submitted)

        self._login_error = ctk.CTkLabel(
            box,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#b3261e",
            wraplength=320,
        )
        self._login_error.pack(pady=(10, 10))

        ctk.CTkButton(
            box,
            text="Увійти",
            width=220,
            height=40,
            corner_radius=10,
            command=self._on_card_submitted,
        ).pack()

        self._setup_box = self._build_setup_box(view)

        return view

    def _build_setup_box(self, view) -> ctk.CTkFrame:
        """Форма створення першого адміністратора (показується, поки його немає)."""
        box = ctk.CTkFrame(view, fg_color="transparent")

        ctk.CTkLabel(
            box, text="🛠", font=ctk.CTkFont(size=80),
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            box,
            text="Створіть адміністратора",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1f2a44",
        ).pack()

        ctk.CTkLabel(
            box,
            text="У системі ще немає адміністратора. Введіть ПІБ і піднесіть\n"
                 "картку до зчитувача (або введіть її UID вручну).",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center",
        ).pack(pady=(5, 25))

        self._setup_name_entry = ctk.CTkEntry(
            box, width=300, height=40,
            placeholder_text="ПІБ адміністратора",
        )
        self._setup_name_entry.pack()
        # Enter у полі ПІБ переносить фокус на поле картки.
        self._setup_name_entry.bind(
            "<Return>", lambda _e: self._setup_card_entry.focus_set())

        self._setup_card_entry = ctk.CTkEntry(
            box, width=300, height=40, justify="center",
            placeholder_text="UID картки",
        )
        self._setup_card_entry.pack(pady=(10, 0))
        self._setup_card_entry.bind("<Return>", self._on_setup_submitted)
        self._setup_card_entry.bind("<KP_Enter>", self._on_setup_submitted)

        self._setup_error = ctk.CTkLabel(
            box,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#b3261e",
            wraplength=340,
        )
        self._setup_error.pack(pady=(10, 10))

        ctk.CTkButton(
            box,
            text="Створити адміністратора",
            width=240,
            height=40,
            corner_radius=10,
            command=self._on_setup_submitted,
        ).pack()

        return box

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

        self._admin_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#667085",
        )
        self._admin_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

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
    def on_show(self):
        """Викликається головним вікном при відкритті сторінки."""
        if not self._is_authorized:
            self._refresh_login_mode()

    def _refresh_login_mode(self):
        """Показує звичайний вхід або (якщо адміністратора ще немає) форму створення."""
        try:
            setup_needed = not has_usable_admin()
        except AdminAccessError:
            # База недоступна: покажемо звичайний вхід, помилка з'явиться при спробі входу.
            setup_needed = False

        if setup_needed:
            self._login_box.grid_forget()
            self._setup_box.grid(row=0, column=0)
            self._focus(self._setup_name_entry)
        else:
            self._setup_box.grid_forget()
            self._login_box.grid(row=0, column=0)
            self._focus(self._card_entry)

    def _focus(self, widget):
        # Невелика затримка: сторінка щойно піднята через tkraise().
        self.after(50, widget.focus_set)

    def _enter_panel(self, admin: dict):
        """Відкриває адмін-панель після успішної авторизації."""
        self._admin = admin
        self._is_authorized = True
        self._login_error.configure(text="")
        self._setup_error.configure(text="")
        self._admin_label.configure(text=f"Адміністратор: {admin['full_name']}")
        self._login_view.grid_forget()
        self._panel_view.grid(row=0, column=0, sticky="nsew")

    def _on_card_submitted(self, _event=None):
        """Перевіряє UID картки з поля вводу й відкриває адмін-панель."""
        card_uid = self._card_entry.get().strip()
        self._card_entry.delete(0, "end")

        try:
            admin = check_admin_card(card_uid)
        except AdminAccessError as exc:
            self._login_error.configure(text=str(exc))
            self._card_entry.focus_set()
            return

        self._enter_panel(admin)

    def _on_setup_submitted(self, _event=None):
        """Створює першого адміністратора й одразу входить у панель."""
        full_name = self._setup_name_entry.get().strip()
        card_uid = self._setup_card_entry.get().strip()

        try:
            admin = create_first_admin(full_name, card_uid)
        except AdminAccessError as exc:
            self._setup_error.configure(text=str(exc))
            return

        self._setup_name_entry.delete(0, "end")
        self._setup_card_entry.delete(0, "end")
        self._enter_panel(admin)

    def _on_logout(self):
        self._admin = None
        self._is_authorized = False
        self._admin_label.configure(text="")
        self._panel_view.grid_forget()
        self._login_view.grid(row=0, column=0, sticky="nsew")
        self._refresh_login_mode()

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