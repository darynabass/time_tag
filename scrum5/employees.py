"""SCRUM-5: employee registry for the existing TimeTag SQLite schema.

No table creation, schema migration, or writes to attendance records.
Designed for use by the group's GUI and the separate ``scrum5.cli`` tool.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


class EmployeeError(ValueError):
    """Validation or business rule error safe to show to an end user."""


REQUIRED_COLUMNS = {
    "employees": {"id", "full_name", "role", "status", "work_status"},
    "rfid_tags": {"id", "employee_id", "card_uid", "status"},
}
ROLES = ("employee", "admin")
STATUSES = ("active", "inactive")


def _name(value: str) -> str:
    if not isinstance(value, str):
        raise EmployeeError("ПІБ працівника повинно бути текстом.")
    # Preserve Cyrillic and meaningful punctuation; normalize repeated spaces.
    if any(ord(char) < 32 and char not in "\t\r\n" for char in value):
        raise EmployeeError("ПІБ містить недопустимі символи.")
    result = " ".join(value.split())
    if not 2 <= len(result) <= 120:
        raise EmployeeError("ПІБ повинно містити від 2 до 120 символів.")
    return result


def _uid(value: str) -> str:
    if not isinstance(value, str):
        raise EmployeeError("UID картки повинен бути текстом.")
    result = value.strip()
    if not 1 <= len(result) <= 128 or any(c.isspace() or ord(c) < 32 for c in result):
        raise EmployeeError("UID картки: від 1 до 128 символів без пробілів.")
    return result


def _id(value: int) -> int:
    if type(value) is not int or value < 1:
        raise EmployeeError("ID працівника має бути додатним цілим числом.")
    return value


def _role(value: str) -> str:
    if value not in ROLES:
        raise EmployeeError("Роль повинна бути 'employee' або 'admin'.")
    return value


class EmployeeService:
    """Independent SCRUM-5 service with transactions and no schema changes.

    By default uses TimeTag.db in the root of the cloned repository. Pass a
    different db_path if the team chose another location. Requires an existing
    initialized database instead of silently making an empty one.
    """

    def __init__(self, db_path: str | Path | None = None):
        root = Path(__file__).resolve().parent.parent
        self.db_path = Path(db_path) if db_path is not None else root / "TimeTag.db"
        self.db_path = self.db_path.expanduser().resolve()
        if not self.db_path.is_file():
            raise EmployeeError(
                f"Базу не знайдено: {self.db_path}. "
                "Спочатку створіть її штатною функцією create_database()."
            )
        self._check_schema()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _check_schema(self) -> None:
        with self._connection() as conn:
            for table, required in REQUIRED_COLUMNS.items():
                columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
                if not required.issubset(columns):
                    missing = ", ".join(sorted(required - columns))
                    raise EmployeeError(
                        f"База має несумісну схему: {table}; відсутні поля: {missing}"
                    )

    @staticmethod
    def _get(conn: sqlite3.Connection, employee_id: int) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM employees WHERE id=?", (_id(employee_id),)).fetchone()
        if row is None:
            raise EmployeeError(f"Працівника з ID {employee_id} не знайдено.")
        return row

    @staticmethod
    def _details(conn: sqlite3.Connection, employee_id: int) -> dict:
        row = conn.execute("""
            SELECT e.id, e.full_name, e.role, e.status, e.work_status,
                   (SELECT t.card_uid FROM rfid_tags AS t
                     WHERE t.employee_id=e.id AND t.status='active'
                     ORDER BY t.id DESC LIMIT 1) AS card_uid
              FROM employees AS e WHERE e.id=?
        """, (employee_id,)).fetchone()
        if row is None:
            raise EmployeeError(f"Працівника з ID {employee_id} не знайдено.")
        return dict(row)

    def get_employee(self, employee_id: int) -> dict:
        with self._connection() as conn:
            return self._details(conn, _id(employee_id))

    def list_employees(self, search: str = "", include_inactive: bool = True) -> list[dict]:
        if not isinstance(search, str):
            raise EmployeeError("Пошуковий запит повинен бути текстом.")
        with self._connection() as conn:
            rows = conn.execute("""
                SELECT e.id, e.full_name, e.role, e.status, e.work_status,
                       (SELECT t.card_uid FROM rfid_tags AS t
                         WHERE t.employee_id=e.id AND t.status='active'
                         ORDER BY t.id DESC LIMIT 1) AS card_uid
                  FROM employees AS e
            """).fetchall()
        # SQLite's built-in LOWER() is ASCII-only; casefold supports Ukrainian.
        needle = search.strip().casefold()
        result = [dict(row) for row in rows
                  if (include_inactive or row["status"] == "active")
                  and (needle in row["full_name"].casefold()
                       or (needle and needle in str(row["id"]))) ]
        return sorted(result, key=lambda emp: (emp["status"] != "active",
                                                emp["full_name"].casefold(), emp["id"]))

    def add_employee(self, full_name: str, card_uid: str | None = None,
                     role: str = "employee") -> int:
        name = _name(full_name)
        role = _role(role)
        uid = _uid(card_uid) if card_uid is not None and card_uid != "" else None
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO employees (full_name, role) VALUES (?, ?)", (name, role)
            )
            employee_id = cursor.lastrowid
            if uid is not None:
                try:
                    conn.execute(
                        "INSERT INTO rfid_tags (employee_id, card_uid) VALUES (?, ?)",
                        (employee_id, uid),
                    )
                except sqlite3.IntegrityError as exc:
                    raise EmployeeError("Цей UID картки вже зареєстрований.") from exc
            return employee_id

    def edit_employee(self, employee_id: int, full_name: str | None = None,
                      role: str | None = None) -> dict:
        employee_id = _id(employee_id)
        if full_name is None and role is None:
            raise EmployeeError("Вкажіть нове ПІБ або роль.")
        name = _name(full_name) if full_name is not None else None
        role = _role(role) if role is not None else None
        with self._connection() as conn:
            current = self._get(conn, employee_id)
            conn.execute(
                "UPDATE employees SET full_name=?, role=? WHERE id=?",
                (name if name is not None else current["full_name"],
                 role if role is not None else current["role"], employee_id),
            )
            return self._details(conn, employee_id)

    def deactivate_employee(self, employee_id: int) -> dict:
        """Soft-delete: retain attendance history; disable all employee cards."""
        employee_id = _id(employee_id)
        with self._connection() as conn:
            self._get(conn, employee_id)
            conn.execute("UPDATE employees SET status='inactive' WHERE id=?", (employee_id,))
            conn.execute("UPDATE rfid_tags SET status='inactive' WHERE employee_id=?", (employee_id,))
            return self._details(conn, employee_id)

    def activate_employee(self, employee_id: int) -> dict:
        """Activate account; cards remain inactive until explicitly assigned."""
        employee_id = _id(employee_id)
        with self._connection() as conn:
            self._get(conn, employee_id)
            conn.execute("UPDATE employees SET status='active' WHERE id=?", (employee_id,))
            return self._details(conn, employee_id)

    def assign_card(self, employee_id: int, card_uid: str) -> dict:
        """Associate one active card; keep old card rows for history/auditing."""
        employee_id = _id(employee_id)
        uid = _uid(card_uid)
        with self._connection() as conn:
            employee = self._get(conn, employee_id)
            if employee["status"] != "active":
                raise EmployeeError("Не можна видати картку неактивному працівнику.")
            existing = conn.execute(
                "SELECT employee_id FROM rfid_tags WHERE card_uid=?", (uid,)
            ).fetchone()
            if existing is not None and existing["employee_id"] != employee_id:
                raise EmployeeError("Картка вже належить іншому працівнику.")
            conn.execute("UPDATE rfid_tags SET status='inactive' WHERE employee_id=?",
                         (employee_id,))
            if existing is not None:
                conn.execute("UPDATE rfid_tags SET status='active' WHERE card_uid=?", (uid,))
            else:
                try:
                    conn.execute(
                        "INSERT INTO rfid_tags (employee_id, card_uid) VALUES (?, ?)",
                        (employee_id, uid),
                    )
                except sqlite3.IntegrityError as exc:
                    raise EmployeeError("Цей UID картки вже зареєстрований.") from exc
            return self._details(conn, employee_id)

    def unbind_cards(self, employee_id: int) -> dict:
        employee_id = _id(employee_id)
        with self._connection() as conn:
            self._get(conn, employee_id)
            conn.execute("UPDATE rfid_tags SET status='inactive' WHERE employee_id=?",
                         (employee_id,))
            return self._details(conn, employee_id)
