"""
Сторінка «Звіти».
Показує записи відвідувань із бази даних (відсортовані за датою й часом)
та зберігає сформований звіт у файл Excel.
"""

from tkinter import filedialog, ttk

import customtkinter as ctk

from reports.report import REPORT_HEADERS, ReportError, default_report_filename
from ui.controllers.reports_controller import ReportsController
from ui.dialogs.error_dialog import ErrorDialog


class ReportsPage(ctk.CTkFrame):
    """Сторінка звітів відвідувань."""

    COLUMNS = ("date", "name", "check_in", "check_out", "hours")
    COLUMN_WIDTHS = (110, 260, 90, 90, 130)

    def __init__(self, master, controller=None):
        super().__init__(master, corner_radius=0, fg_color="white")

        self._controller = controller or ReportsController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self._configure_style()

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
        table_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 10))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self._tree = ttk.Treeview(
            table_frame,
            columns=self.COLUMNS,
            show="headings",
            style="Reports.Treeview",
            selectmode="browse",
        )
        for key, title, width in zip(self.COLUMNS, REPORT_HEADERS, self.COLUMN_WIDTHS):
            self._tree.heading(key, text=title, anchor="w")
            self._tree.column(key, width=width, anchor="w", stretch=True)
        self._tree.tag_configure("odd", background="#f7f9fc")

        scrollbar = ctk.CTkScrollbar(table_frame, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 8), pady=12)

        # ---- Рядок стану ----
        self._status = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color="#667085",
        )
        self._status.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 10))

        # ---- Панель кнопок ----
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 30))

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

    # ------------------------------------------------------------------
    #  Оформлення таблиці
    # ------------------------------------------------------------------
    @staticmethod
    def _configure_style():
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Reports.Treeview",
            background="#ffffff", fieldbackground="#ffffff",
            foreground="#222222", borderwidth=0,
            rowheight=34, font=("Segoe UI", 11),
        )
        style.configure(
            "Reports.Treeview.Heading",
            background="#f4f7fb", foreground="#1f2a44",
            font=("Segoe UI", 11, "bold"),
            relief="flat", padding=(8, 8),
        )
        style.map(
            "Reports.Treeview",
            background=[("selected", "#dbe7ff")],
            foreground=[("selected", "#1f2a44")],
        )
        style.map("Reports.Treeview.Heading", background=[("active", "#e1e7f0")])

    # ------------------------------------------------------------------
    #  Дані
    # ------------------------------------------------------------------
    def on_show(self):
        """Викликається головним вікном щоразу, коли відкривається сторінка."""
        self.refresh()

    def refresh(self):
        """Перечитує записи з бази та перемальовує таблицю."""
        try:
            rows = self._controller.load()
        except ReportError as exc:
            self._fill_table([])
            self._set_status("", success=False)
            ErrorDialog(self.winfo_toplevel(), str(exc))
            return

        self._fill_table(rows)
        if rows:
            self._set_status(f"Записів: {len(rows)}", success=False)
        else:
            self._set_status("Записів відвідування ще немає.", success=False)

    def _fill_table(self, rows):
        self._tree.delete(*self._tree.get_children())
        for index, row in enumerate(rows):
            self._tree.insert(
                "", "end",
                values=(row["date"], row["name"], row["check_in"],
                        row["check_out"], row["hours"]),
                tags=("odd",) if index % 2 else (),
            )

    def _set_status(self, text: str, success: bool):
        self._status.configure(text=text,
                               text_color="#1f7a3d" if success else "#667085")

    # ------------------------------------------------------------------
    #  Кнопки
    # ------------------------------------------------------------------
    def _on_refresh(self):
        self.refresh()

    def _on_export(self):
        path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            title="Зберегти звіт",
            defaultextension=".xlsx",
            filetypes=[("Файл Excel", "*.xlsx")],
            initialfile=default_report_filename(),
        )
        if not path:  # користувач закрив вікно вибору файлу
            return

        try:
            saved_path = self._controller.export(path)
        except ReportError as exc:
            ErrorDialog(self.winfo_toplevel(), str(exc))
            return

        self._set_status(f"Звіт збережено: {saved_path}", success=True)
