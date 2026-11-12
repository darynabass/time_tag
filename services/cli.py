"""Command-line demo of SCRUM-5 without touching the team's GUI/main.py.

From the TimeTag repository root:
    py -m scrum5.cli list
    py -m scrum5.cli add --name "Іван Петренко" --card DEMO001
"""

from __future__ import annotations

import argparse
from services.employees import EmployeeError, EmployeeService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TimeTag | SCRUM-5: працівники")
    parser.add_argument("--db", help="Шлях до існуючої бази TimeTag.db")
    actions = parser.add_subparsers(dest="action", required=True)

    listing = actions.add_parser("list", help="Список та пошук працівників")
    listing.add_argument("--search", default="", help="ПІБ або ID")
    listing.add_argument("--active-only", action="store_true")

    item = actions.add_parser("show", help="Дані одного працівника")
    item.add_argument("id", type=int)

    item = actions.add_parser("add", help="Додати працівника")
    item.add_argument("--name", required=True)
    item.add_argument("--card", help="UID RFID-картки (не обов'язково)")
    item.add_argument("--role", choices=("employee", "admin"), default="employee")

    item = actions.add_parser("edit", help="Редагувати ПІБ / роль")
    item.add_argument("id", type=int)
    item.add_argument("--name")
    item.add_argument("--role", choices=("employee", "admin"))

    item = actions.add_parser("set-card", help="Прив'язати або замінити картку")
    item.add_argument("id", type=int)
    item.add_argument("--card", required=True)

    item = actions.add_parser("unbind-card", help="Деактивувати картки працівника")
    item.add_argument("id", type=int)

    for command in ("deactivate", "activate"):
        item = actions.add_parser(command, help=f"{command} працівника")
        item.add_argument("id", type=int)
    return parser


def _print_employees(rows: list[dict]) -> None:
    if not rows:
        print("Нічого не знайдено.")
        return
    for emp in rows:
        print(f"#{emp['id']:>3} | {emp['full_name']} | "
              f"роль: {emp['role']} | статус: {emp['status']} | "
              f"картка: {emp['card_uid'] or '—'}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        service = EmployeeService(args.db)
        if args.action == "list":
            _print_employees(service.list_employees(
                search=args.search, include_inactive=not args.active_only))
        elif args.action == "show":
            _print_employees([service.get_employee(args.id)])
        elif args.action == "add":
            number = service.add_employee(args.name, args.card, args.role)
            print(f"Працівника успішно додано. ID: {number}")
        elif args.action == "edit":
            _print_employees([service.edit_employee(args.id, args.name, args.role)])
        elif args.action == "set-card":
            _print_employees([service.assign_card(args.id, args.card)])
        elif args.action == "unbind-card":
            _print_employees([service.unbind_cards(args.id)])
        elif args.action == "deactivate":
            _print_employees([service.deactivate_employee(args.id)])
        elif args.action == "activate":
            _print_employees([service.activate_employee(args.id)])
    except EmployeeError as exc:
        print(f"Помилка: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
