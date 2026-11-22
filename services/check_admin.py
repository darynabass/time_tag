"""Адміністраторський доступ (backlog 2.1).

Картка вважається адміністраторською, якщо:
  * вона зареєстрована в таблиці rfid_tags і має статус 'active';
  * працівник-власник має статус 'active';
  * роль працівника — 'admin'.

Якщо в системі ще немає жодного такого адміністратора (перший запуск),
його можна створити з інтерфейсу — див. create_first_admin().
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from database.database import DATABASE_NAME
from services.employees import EmployeeError, EmployeeService


class AdminAccessError(Exception):
    """Причина відмови у доступі; текст можна показувати користувачу."""


def _resolve_db_path(db_path: str | Path | None) -> Path:
    path = Path(db_path) if db_path is not None else Path(DATABASE_NAME)
    if not path.is_file():
        raise AdminAccessError(f"Базу даних не знайдено: {path}")
    return path


def check_admin_card(card_uid: str, db_path: str | Path | None = None) -> dict:
    """Перевіряє, що картка належить активному адміністратору.

    Args:
        card_uid: UID картки, отриманий від зчитувача.
        db_path: шлях до бази (за замовчуванням — TimeTag.db у корені проєкту).

    Returns:
        Словник {"id": ..., "full_name": ...} адміністратора.

    Raises:
        AdminAccessError: якщо доступ заборонено або базу не вдалося прочитати.
    """
    uid = card_uid.strip() if isinstance(card_uid, str) else ""
    if not uid:
        raise AdminAccessError("Картку не зчитано. Спробуйте ще раз.")

    path = _resolve_db_path(db_path)
    try:
        with closing(sqlite3.connect(path)) as conn:
            row = conn.execute(
                """
                SELECT e.id, e.full_name, e.role,
                       e.status AS employee_status,
                       t.status AS card_status
                  FROM rfid_tags AS t
                  JOIN employees AS e ON e.id = t.employee_id
                 WHERE t.card_uid = ?
                """,
                (uid,),
            ).fetchone()
    except sqlite3.Error as exc:
        raise AdminAccessError("Не вдалося перевірити картку: помилка бази даних.") from exc

    if row is None:
        raise AdminAccessError("Невідома або незареєстрована картка.")
    emp_id, full_name, role, employee_status, card_status = row
    if card_status != "active":
        raise AdminAccessError("Цю картку деактивовано.")
    if employee_status != "active":
        raise AdminAccessError("Обліковий запис працівника деактивовано.")
    if role != "admin":
        raise AdminAccessError("Ця картка не має адмін-прав.")

    return {"id": emp_id, "full_name": full_name}


def has_usable_admin(db_path: str | Path | None = None) -> bool:
    """True, якщо є хоча б один активний адміністратор з активною карткою."""
    path = _resolve_db_path(db_path)
    try:
        with closing(sqlite3.connect(path)) as conn:
            row = conn.execute(
                """
                SELECT 1
                  FROM employees AS e
                  JOIN rfid_tags AS t ON t.employee_id = e.id
                 WHERE e.role = 'admin' AND e.status = 'active' AND t.status = 'active'
                 LIMIT 1
                """
            ).fetchone()
    except sqlite3.Error as exc:
        raise AdminAccessError("Не вдалося перевірити адміністраторів: помилка бази даних.") from exc
    return row is not None


def create_first_admin(full_name: str, card_uid: str,
                       db_path: str | Path | None = None) -> dict:
    """Створює адміністратора, якщо в системі ще немає жодного придатного до входу.

    Захист: коли адміністратор уже є, функція відмовляє — інакше будь-хто міг би
    видати собі адмін-права. Подальших працівників додає вже авторизований адмін.

    Returns:
        Словник {"id": ..., "full_name": ...} створеного адміністратора.

    Raises:
        AdminAccessError: адміністратор уже існує, не введено картку, ПІБ або UID
            некоректні, картка вже зареєстрована, або помилка бази даних.
    """
    path = _resolve_db_path(db_path)
    if has_usable_admin(path):
        raise AdminAccessError("Адміністратор уже існує. Увійдіть за його карткою.")

    uid = card_uid.strip() if isinstance(card_uid, str) else ""
    if not uid:
        raise AdminAccessError("Піднесіть картку до зчитувача або введіть UID картки.")

    try:
        service = EmployeeService(path)
        employee_id = service.add_employee(full_name, uid, "admin")
        employee = service.get_employee(employee_id)
    except EmployeeError as exc:
        raise AdminAccessError(str(exc)) from exc
    except sqlite3.Error as exc:
        raise AdminAccessError("Не вдалося створити адміністратора: помилка бази даних.") from exc

    return {"id": employee["id"], "full_name": employee["full_name"]}
