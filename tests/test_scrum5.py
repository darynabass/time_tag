"""Isolated SCRUM-5 tests: only temporary SQLite files are used."""

import io
from contextlib import closing, redirect_stdout
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scrum5 import EmployeeError, EmployeeService
from scrum5.cli import main as cli_main

# Same column names and constraints as the original three-table TimeTag schema.
SCHEMA = """
CREATE TABLE employees (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'employee' CHECK (role IN ('admin','employee')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
  work_status TEXT NOT NULL DEFAULT 'absent' CHECK (work_status IN ('present','absent'))
);
CREATE TABLE rfid_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  employee_id INTEGER NOT NULL,
  card_uid TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
  FOREIGN KEY (employee_id) REFERENCES employees(id)
);
CREATE TABLE attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  employee_id INTEGER NOT NULL,
  work_date TEXT NOT NULL,
  check_in TEXT, check_out TEXT,
  UNIQUE (employee_id, work_date),
  FOREIGN KEY (employee_id) REFERENCES employees(id)
);
"""


class TestEmployeeService(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "TimeTag.db"
        # The sqlite3 connection context manager does not close the connection.
        # close explicitly so Windows can delete the temporary DB after each test.
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.executescript(SCHEMA)
        self.service = EmployeeService(self.db)

    def test_add_employee_defaults(self):
        eid = self.service.add_employee("  Іван   Петренко  ")
        emp = self.service.get_employee(eid)
        self.assertEqual(emp["full_name"], "Іван Петренко")
        self.assertEqual(emp["role"], "employee")
        self.assertEqual(emp["status"], "active")
        self.assertEqual(emp["work_status"], "absent")
        self.assertIsNone(emp["card_uid"])

    def test_add_card_and_search_by_cyrillic_case(self):
        eid = self.service.add_employee("Олена КОВАЛЬ", "A001")
        self.assertEqual(self.service.list_employees("кОвАлЬ")[0]["id"], eid)
        self.assertEqual(self.service.get_employee(eid)["card_uid"], "A001")

    def test_duplicate_card_rolls_back_new_employee(self):
        self.service.add_employee("Іван Іванов", "A001")
        with self.assertRaises(EmployeeError):
            self.service.add_employee("Петро Петров", "A001")
        self.assertEqual(len(self.service.list_employees()), 1)

    def test_duplicate_card_not_stolen_on_reassign(self):
        first = self.service.add_employee("Перший Співробітник", "A001")
        second = self.service.add_employee("Другий Співробітник")
        with self.assertRaises(EmployeeError):
            self.service.assign_card(second, "A001")
        self.assertEqual(self.service.get_employee(first)["card_uid"], "A001")
        self.assertIsNone(self.service.get_employee(second)["card_uid"])

    def test_edit_employee(self):
        eid = self.service.add_employee("Іван Петренко")
        out = self.service.edit_employee(eid, "Іван Коваль", "admin")
        self.assertEqual((out["full_name"], out["role"]), ("Іван Коваль", "admin"))

    def test_edit_role_only(self):
        eid = self.service.add_employee("Іван Петренко")
        self.assertEqual(self.service.edit_employee(eid, role="admin")["full_name"], "Іван Петренко")

    def test_card_replacement_preserves_inactive_history(self):
        eid = self.service.add_employee("Іван Петренко", "OLD1")
        self.service.assign_card(eid, "NEW2")
        self.assertEqual(self.service.get_employee(eid)["card_uid"], "NEW2")
        with closing(sqlite3.connect(self.db)) as conn, conn:
            rows = conn.execute("SELECT card_uid, status FROM rfid_tags WHERE employee_id=? ORDER BY id", (eid,)).fetchall()
        self.assertEqual(rows, [("OLD1", "inactive"), ("NEW2", "active")])

    def test_reissue_old_card_for_same_employee(self):
        eid = self.service.add_employee("Іван Петренко", "OLD1")
        self.service.assign_card(eid, "NEW2")
        self.service.assign_card(eid, "OLD1")
        self.assertEqual(self.service.get_employee(eid)["card_uid"], "OLD1")
        with closing(sqlite3.connect(self.db)) as conn, conn:
            count = conn.execute("SELECT COUNT(*) FROM rfid_tags WHERE employee_id=? AND status='active'", (eid,)).fetchone()[0]
        self.assertEqual(count, 1)

    def test_deactivate_and_reactivate_without_auto_restoring_card(self):
        eid = self.service.add_employee("Іван Петренко", "A001")
        self.service.deactivate_employee(eid)
        self.assertEqual(self.service.get_employee(eid)["status"], "inactive")
        self.assertIsNone(self.service.get_employee(eid)["card_uid"])
        self.assertEqual(self.service.list_employees(include_inactive=False), [])
        self.service.activate_employee(eid)
        self.assertIsNone(self.service.get_employee(eid)["card_uid"])
        self.service.assign_card(eid, "A001")
        self.assertEqual(self.service.get_employee(eid)["card_uid"], "A001")

    def test_cannot_assign_card_to_inactive_employee(self):
        eid = self.service.add_employee("Іван Петренко")
        self.service.deactivate_employee(eid)
        with self.assertRaises(EmployeeError):
            self.service.assign_card(eid, "A001")

    def test_unbind_card(self):
        eid = self.service.add_employee("Іван Петренко", "A001")
        self.service.unbind_cards(eid)
        self.assertIsNone(self.service.get_employee(eid)["card_uid"])

    def test_no_physical_deletion_of_employee_or_attendance(self):
        eid = self.service.add_employee("Іван Петренко", "A001")
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("INSERT INTO attendance(employee_id,work_date,check_in) VALUES (?, ?, ?)",
                         (eid, "2026-11-12", "2026-11-12T08:00:00"))
        self.service.deactivate_employee(eid)
        with closing(sqlite3.connect(self.db)) as conn, conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0], 1)

    def test_bad_input_and_missing_employee(self):
        with self.assertRaises(EmployeeError):
            self.service.add_employee(" ")
        with self.assertRaises(EmployeeError):
            self.service.add_employee("Іван", "INVALID UID")
        with self.assertRaises(EmployeeError):
            self.service.edit_employee(999, "Іван Іванов")
        with self.assertRaises(EmployeeError):
            self.service.add_employee("Валідне Ім'я", role="owner")

    def test_missing_file_is_not_created(self):
        missing = Path(self.tmp.name) / "missing.db"
        with self.assertRaises(EmployeeError):
            EmployeeService(missing)
        self.assertFalse(missing.exists())

    def test_wrong_schema_rejected(self):
        broken = Path(self.tmp.name) / "broken.db"
        with closing(sqlite3.connect(broken)) as conn, conn:
            conn.execute("CREATE TABLE employees(id integer)")
        with self.assertRaises(EmployeeError):
            EmployeeService(broken)

    def test_cli_add_list_edit(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli_main(["--db", str(self.db), "add", "--name", "Марія Коваль", "--card", "TAG99"]), 0)
            self.assertEqual(cli_main(["--db", str(self.db), "list", "--search", "коваль"]), 0)
        self.assertIn("TAG99", output.getvalue())
        self.assertIn("Марія Коваль", output.getvalue())

    def test_cli_errors_return_nonzero(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli_main(["--db", str(self.db), "show", "999"]), 1)


if __name__ == "__main__":
    unittest.main()
