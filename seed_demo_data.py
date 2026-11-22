"""Необов'язковий скрипт: додає демонстраційні дані до бази.

Потрібен, щоб перевірити звіт відвідувань (1.6), поки реєстрація приходу/виходу
карткою ще не реалізована. Можна запускати на базі, де вже є ваші працівники чи
адміністратор: існуючі дані не змінюються, додається лише те, чого бракує.

Запуск із кореня проєкту:
    python seed_demo_data.py

Що додається:
  * адміністратор з карткою ADMIN001 — лише якщо в системі ще немає адміністратора;
  * три працівники з картками CARD001–CARD003 (якщо таких карток ще немає);
  * відвідування за кілька останніх робочих днів для цих трьох працівників
    (лише тим, у кого ще немає жодного запису).
"""

import sqlite3
from contextlib import closing
from datetime import date, timedelta

from database.database import DATABASE_NAME, create_database
from services.check_admin import has_usable_admin
from services.employees import EmployeeService

ADMIN = ("Адміністратор Системи", "ADMIN001")

# (ПІБ, UID картки)
EMPLOYEES = [
    ("Іваненко Олександр Сергійович", "CARD001"),
    ("Петренко Марія Василівна", "CARD002"),
    ("Коваленко Андрій Іванович", "CARD003"),
]

# (прихід, вихід) — чергуються по днях і працівниках
TIMES = [("08:55:10", "17:30:42"), ("09:02:31", "18:00:05"), ("08:45:00", "17:15:20")]


def _card_owner(conn, card_uid):
    row = conn.execute(
        "SELECT employee_id FROM rfid_tags WHERE card_uid = ?", (card_uid,)
    ).fetchone()
    return row[0] if row else None


def _last_workdays(count):
    days, day = [], date.today()
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day -= timedelta(days=1)
    return days


def main() -> int:
    create_database()
    service = EmployeeService()
    changed = False

    # 1. Адміністратор — тільки якщо жодного ще немає.
    if has_usable_admin():
        print("Адміністратор уже є — демонстраційного не додаю.")
    elif _is_taken(ADMIN[1]):
        print(f"Картка {ADMIN[1]} уже зайнята — адміністратора не додано.")
    else:
        service.add_employee(ADMIN[0], ADMIN[1], "admin")
        print(f"+ адміністратор {ADMIN[0]} (картка {ADMIN[1]})")
        changed = True

    # 2. Працівники.
    for name, card in EMPLOYEES:
        if _is_taken(card):
            continue
        service.add_employee(name, card, "employee")
        print(f"+ працівник {name} (картка {card})")
        changed = True

    # 3. Відвідування для демонстраційних працівників без записів.
    workdays = _last_workdays(4)
    with closing(sqlite3.connect(DATABASE_NAME)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for e_index, (name, card) in enumerate(EMPLOYEES):
            employee_id = _card_owner(conn, card)
            if employee_id is None:
                continue
            has_records = conn.execute(
                "SELECT 1 FROM attendance WHERE employee_id = ? LIMIT 1", (employee_id,)
            ).fetchone()
            if has_records:
                continue
            for d_index, work_day in enumerate(workdays):
                check_in, check_out = TIMES[(d_index + e_index) % len(TIMES)]
                # Найновіший запис останнього працівника — без виходу (ще на роботі).
                if d_index == 0 and e_index == len(EMPLOYEES) - 1:
                    check_out = None
                conn.execute(
                    "INSERT INTO attendance (employee_id, work_date, check_in, check_out) "
                    "VALUES (?, ?, ?, ?)",
                    (employee_id, work_day.isoformat(), check_in, check_out),
                )
            print(f"+ відвідування для {name}")
            changed = True
        conn.commit()

    print("Готово." if changed else "Демонстраційні дані вже є — нічого не додано.")
    return 0


def _is_taken(card_uid) -> bool:
    with closing(sqlite3.connect(DATABASE_NAME)) as conn:
        return _card_owner(conn, card_uid) is not None


if __name__ == "__main__":
    raise SystemExit(main())
