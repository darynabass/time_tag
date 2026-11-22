"""Формування звіту відвідувань (backlog 1.6).

Читає записи з таблиці attendance, підставляє ПІБ працівника, сортує за
датою та часом і зберігає звіт у файл Excel (.xlsx) у вигляді табеля:
по аркушу на місяць, дні місяця — рядки, а для кожного працівника три
стовпці «Прихід / Вихід / Відпрацьовано». Графік роботи — з 9:00 до 18:00.

Дата (work_date) та час (check_in / check_out) можуть бути збережені в різних
поширених форматах: 2025-04-21, 21.04.2025, 08:55, 08:55:30,
2025-04-21 08:55:30 — розпізнаються всі.
"""

from __future__ import annotations

import calendar
import sqlite3
from contextlib import closing
from datetime import date, datetime, time
from pathlib import Path

from database.database import DATABASE_NAME

REPORT_HEADERS = ("Дата", "Працівник", "Прихід", "Вихід", "Відпрацьовано")
EMPTY_VALUE = "—"

# Графік роботи: запізнення — прихід після WORK_START, ранній вихід — раніше
# WORK_END, пізній вихід — після WORK_END.
WORK_START = time(9, 0)
WORK_END = time(18, 0)

MONTH_NAMES = ("", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
               "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень")


class ReportError(Exception):
    """Помилка формування або збереження звіту; текст можна показувати користувачу."""


# ----------------------------------------------------------------------
#  Розбір дати й часу
# ----------------------------------------------------------------------
def _parse_date(value) -> date | None:
    if not isinstance(value, str):
        return None
    text = value.strip()[:10]
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _parse_time(value) -> time | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        return time.fromisoformat(text).replace(tzinfo=None)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(text).time().replace(tzinfo=None)
    except ValueError:
        pass
    for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def _worked_minutes(check_in: time | None, check_out: time | None) -> int | None:
    """Повні хвилини між приходом і виходом; None, якщо запис неповний."""
    if check_in is None or check_out is None:
        return None
    start = datetime.combine(date.min, check_in.replace(second=0, microsecond=0))
    end = datetime.combine(date.min, check_out.replace(second=0, microsecond=0))
    seconds = (end - start).total_seconds()
    if seconds < 0:
        return None
    return int(seconds // 60)


def _format_minutes(minutes: int | None) -> str:
    if minutes is None:
        return EMPTY_VALUE
    return f"{minutes // 60}:{minutes % 60:02d}"


def _show(raw, parsed, fmt: str) -> str:
    if parsed is not None:
        return parsed.strftime(fmt)
    return str(raw).strip() if raw not in (None, "") else EMPTY_VALUE


# ----------------------------------------------------------------------
#  Дані звіту
# ----------------------------------------------------------------------
def _build_row(employee_id: int, full_name: str, work_date, check_in, check_out) -> dict:
    day = _parse_date(work_date)
    time_in = _parse_time(check_in)
    time_out = _parse_time(check_out)
    minutes = _worked_minutes(time_in, time_out)
    return {
        "employee_id": employee_id,
        # Значення для відображення в таблиці.
        "date": _show(work_date, day, "%d.%m.%Y"),
        "name": full_name,
        "check_in": _show(check_in, time_in, "%H:%M"),
        "check_out": _show(check_out, time_out, "%H:%M"),
        "hours": _format_minutes(minutes),
        # Розпізнані значення (для сортування та експорту).
        "date_value": day,
        "check_in_value": time_in,
        "check_out_value": time_out,
        "minutes": minutes,
    }


def get_report_rows(db_path: str | Path | None = None,
                    newest_first: bool = True) -> list[dict]:
    """Повертає записи відвідувань, відсортовані за датою й часом приходу.

    Args:
        db_path: шлях до бази (за замовчуванням — TimeTag.db у корені проєкту).
        newest_first: True — спочатку найновіші записи, False — найстаріші.

    Raises:
        ReportError: якщо базу не знайдено або її не вдалося прочитати.
    """
    path = Path(db_path) if db_path is not None else Path(DATABASE_NAME)
    if not path.is_file():
        raise ReportError(f"Базу даних не знайдено: {path}")

    try:
        with closing(sqlite3.connect(path)) as conn:
            records = conn.execute(
                """
                SELECT e.id, e.full_name, a.work_date, a.check_in, a.check_out
                  FROM attendance AS a
                  JOIN employees AS e ON e.id = a.employee_id
                """
            ).fetchall()
    except sqlite3.Error as exc:
        raise ReportError("Не вдалося прочитати дані відвідувань із бази.") from exc

    rows = [_build_row(*record) for record in records]
    rows.sort(
        key=lambda r: (r["date_value"] or date.min,
                       r["check_in_value"] or time.min,
                       r["name"].casefold()),
        reverse=newest_first,
    )
    return rows


# ----------------------------------------------------------------------
#  Експорт в Excel
# ----------------------------------------------------------------------
def default_report_filename() -> str:
    """Назва файлу звіту за замовчуванням, наприклад attendance_report_2025-04-21.xlsx."""
    return f"attendance_report_{date.today():%Y-%m-%d}.xlsx"


_UA_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"


def _alphabetical_key(name: str) -> list[int]:
    """Ключ сортування за українським алфавітом (щоб «І» не потрапляло після «Я»)."""
    return [_UA_ALPHABET.find(ch) if ch in _UA_ALPHABET else 100 + ord(ch)
            for ch in name.casefold()]


def _short_name(full_name: str) -> str:
    """«Іваненко Олександр Сергійович» -> «Іваненко О.С.»."""
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    initials = "".join(f"{part[0].upper()}." for part in parts[1:3])
    return f"{parts[0]} {initials}"


def _group_by_month(rows: list[dict]) -> dict:
    """{(рік, місяць): {id працівника: {"name": ..., "days": {день: [прихід, вихід]}}}}.

    Якщо за день кілька записів — береться найраніший прихід і найпізніший вихід.
    Записи з нерозпізнаною датою в табель не потрапляють.
    """
    months: dict = {}
    for row in rows:
        day = row["date_value"]
        if day is None:
            continue
        employee = months.setdefault((day.year, day.month), {}).setdefault(
            row["employee_id"], {"name": row["name"], "days": {}})
        current = employee["days"].setdefault(day.day, [None, None])
        time_in, time_out = row["check_in_value"], row["check_out_value"]
        if time_in is not None:
            time_in = time_in.replace(second=0, microsecond=0)
            if current[0] is None or time_in < current[0]:
                current[0] = time_in
        if time_out is not None:
            time_out = time_out.replace(second=0, microsecond=0)
            if current[1] is None or time_out > current[1]:
                current[1] = time_out
    return months


def _write_month_sheet(ws, year: int, month: int, employees: dict) -> None:
    """Малює табель одного місяця: див. зразок «Графік.xls»."""
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.properties import PageSetupProperties

    days_in_month = calendar.monthrange(year, month)[1]
    first_row = 3
    last_row = first_row + days_in_month - 1
    total_row = last_row + 1
    late_row, early_row, over_row = total_row + 1, total_row + 2, total_row + 3

    ordered = sorted(employees.values(), key=lambda e: _alphabetical_key(e["name"]))
    names = [_short_name(e["name"]) for e in ordered]
    for index, name in enumerate(names):  # однакові скорочення — повні ПІБ
        if names.count(name) > 1:
            names[index] = ordered[index]["name"]

    font = Font(name="Arial", size=10)
    font_bold = Font(name="Arial", size=10, bold=True)
    font_small = Font(name="Arial", size=9)
    font_note = Font(name="Arial", size=9, italic=True, color="555555")
    center = Alignment(horizontal="center", vertical="center")
    right = Alignment(horizontal="right", vertical="center")
    fill_in = PatternFill("solid", start_color="FF99CC", end_color="FF99CC")
    fill_out = PatternFill("solid", start_color="CCFFCC", end_color="CCFFCC")
    fill_work = PatternFill("solid", start_color="CCFFFF", end_color="CCFFFF")
    yellow = PatternFill("solid", start_color="FFFF00", end_color="FFFF00")

    start = f"TIME({WORK_START.hour},{WORK_START.minute},0)"
    end = f"TIME({WORK_END.hour},{WORK_END.minute},0)"

    for day in range(1, days_in_month + 1):
        cell = ws.cell(first_row + day - 1, 1, day)
        cell.font, cell.alignment = font, right

    for group, employee in enumerate(ordered):
        c_in = 2 + group * 3
        c_out, c_work = c_in + 1, c_in + 2
        col_in, col_out, col_work = (get_column_letter(c) for c in (c_in, c_out, c_work))

        # Шапка: ім'я (об'єднане на три стовпці) і підписи стовпців.
        ws.cell(1, c_in, names[group]).font = font_bold
        ws.cell(1, c_in).alignment = center
        ws.merge_cells(start_row=1, start_column=c_in, end_row=1, end_column=c_work)
        for offset, title in enumerate(("Прихід", "Вихід", "Відпрацьовано")):
            cell = ws.cell(2, c_in + offset, title)
            cell.font, cell.alignment = font_small, center

        # Дні місяця.
        for day in range(1, days_in_month + 1):
            row = first_row + day - 1
            record = employee["days"].get(day)
            work = ws.cell(row, c_work,
                           f'=IF(AND(ISNUMBER({col_in}{row}),ISNUMBER({col_out}{row}),'
                           f'{col_out}{row}>={col_in}{row}),{col_out}{row}-{col_in}{row},"")')
            work.number_format, work.font, work.alignment = "[h]:mm", font, center
            if record is None:
                continue
            for column, value, fill in ((c_in, record[0], fill_in), (c_out, record[1], fill_out)):
                cell = ws.cell(row, column)
                cell.value = value
                cell.number_format, cell.font, cell.alignment = "HH:MM", font, center
                if value is not None:
                    cell.fill = fill
            work.fill = fill_work

        # Підсумки під таблицею: мітка з'єднана на «Прихід»+«Вихід», значення — у третьому стовпці.
        summary = (
            (total_row, "Разом за місяць:", f"=SUM({col_work}{first_row}:{col_work}{last_row})", "[h]:mm"),
            (late_row, "Всього запізнень:",
             f"=SUMPRODUCT(ISNUMBER({col_in}{first_row}:{col_in}{last_row})*"
             f"({col_in}{first_row}:{col_in}{last_row}>{start}))", "0"),
            (early_row, "Всього ранніх виходів:",
             f"=SUMPRODUCT(ISNUMBER({col_out}{first_row}:{col_out}{last_row})*"
             f"({col_out}{first_row}:{col_out}{last_row}<{end}))", "0"),
            (over_row, "Всього пізніх виходів:",
             f"=SUMPRODUCT(ISNUMBER({col_out}{first_row}:{col_out}{last_row})*"
             f"({col_out}{first_row}:{col_out}{last_row}>{end}))", "0"),
        )
        for row, label, formula, number_format in summary:
            ws.cell(row, c_in, label).font = font
            ws.cell(row, c_in).alignment = right
            ws.merge_cells(start_row=row, start_column=c_in, end_row=row, end_column=c_out)
            value = ws.cell(row, c_work, formula)
            value.number_format, value.font, value.alignment = number_format, font_bold, center

        # Жовтий: прихід після 9:00, вихід раніше або пізніше 18:00 (оновлюється при правках).
        ws.conditional_formatting.add(
            f"{col_in}{first_row}:{col_in}{last_row}",
            FormulaRule(formula=[f"AND(ISNUMBER({col_in}{first_row}),{col_in}{first_row}>{start})"],
                        fill=yellow))
        ws.conditional_formatting.add(
            f"{col_out}{first_row}:{col_out}{last_row}",
            FormulaRule(formula=[f"AND(ISNUMBER({col_out}{first_row}),"
                                 f"OR({col_out}{first_row}<{end},{col_out}{first_row}>{end}))"],
                        fill=yellow))

        # Рамки: тонка сітка, товста рамка навколо блоку працівника.
        thin, thick = Side(style="thin"), Side(style="medium")
        for row in range(1, over_row + 1):
            for column in (c_in, c_out, c_work):
                ws.cell(row, column).border = Border(
                    left=thick if column == c_in else thin,
                    right=thick if column == c_work else thin,
                    top=thick if row == 1 else thin,
                    bottom=thick if row == over_row else thin,
                )

        ws.column_dimensions[col_in].width = 8
        ws.column_dimensions[col_out].width = 13
        ws.column_dimensions[col_work].width = 13.5

    ws.column_dimensions["A"].width = 3.5
    start_text = f"{WORK_START.hour}:{WORK_START.minute:02d}"
    end_text = f"{WORK_END.hour}:{WORK_END.minute:02d}"
    ws.cell(over_row + 2, 1, f"Графік роботи: з {start_text} до {end_text}").font = font_bold
    note = ws.cell(over_row + 3, 1,
                   "Жовтим виділено час, що виходить за графік: запізнення, ранні та пізні виходи.")
    note.font = font_note

    ws.freeze_panes = "B3"
    ws.page_setup.orientation = "portrait"
    ws.print_title_rows = "1:2"
    ws.print_title_cols = "A:A"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)


def export_to_excel(rows: list[dict], file_path: str | Path) -> str:
    """Зберігає звіт у файл .xlsx і повертає шлях до збереженого файлу.

    На кожен місяць — окремий аркуш (спочатку найновіший) у вигляді табеля.

    Raises:
        ReportError: немає даних, не встановлено openpyxl або файл не вдалося
            зберегти (наприклад, він відкритий в Excel).
    """
    if not rows:
        raise ReportError("Немає даних для експорту.")

    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise ReportError(
            "Для експорту потрібна бібліотека openpyxl. "
            "Встановіть: pip install openpyxl"
        ) from exc

    months = _group_by_month(rows)
    if not months:
        raise ReportError("У записах немає коректних дат — звіт не можна сформувати.")

    path = Path(file_path)
    if path.suffix.lower() != ".xlsx":
        path = path.with_suffix(".xlsx")

    workbook = Workbook()
    workbook.remove(workbook.active)
    for year, month in sorted(months, reverse=True):
        sheet = workbook.create_sheet(f"{MONTH_NAMES[month]} {year}")
        _write_month_sheet(sheet, year, month, months[(year, month)])
    workbook.active = 0

    try:
        workbook.save(path)
    except PermissionError as exc:
        raise ReportError(
            f"Не вдалося зберегти файл {path.name}. Закрийте його в Excel і спробуйте ще раз."
        ) from exc
    except OSError as exc:
        raise ReportError(f"Не вдалося зберегти файл: {exc}") from exc
    return str(path)
