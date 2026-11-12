
"""Database initialization for the TimeTag application.

This module creates the database tables required to manage employees,
RFID cards, and daily attendance records.
"""

import sqlite3
from pathlib import Path


# Get the project's root directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Store the database in the project's root directory.
DATABASE_NAME = PROJECT_ROOT / "TimeTag.db"


def create_database():
    """Create the TimeTag database and its tables.

    Creates the database file if it does not exist and initializes
    the employees, rfid_cards, and attendance tables.

    Enables foreign key enforcement for the database connection.

    Raises:
        sqlite3.Error: If the database cannot be initialized.
    """
    conn = sqlite3.connect(DATABASE_NAME)

    try:
        # Enable foreign key constraints for this connection.
        conn.execute("PRAGMA foreign_keys = ON")

        # Store employee information and current work status.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'employee'
                    CHECK (role IN ('admin', 'employee')),
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'inactive')),
                work_status TEXT NOT NULL DEFAULT 'absent'
                    CHECK (work_status IN ('present', 'absent'))
            )
        """)

        # Associate RFID cards with employees.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rfid_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                card_uid TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'inactive')),
                FOREIGN KEY (employee_id)
                    REFERENCES employees(id)
            )
        """)

        # Store one attendance record per employee per day.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                work_date TEXT NOT NULL,
                check_in TEXT,
                check_out TEXT,
                UNIQUE (employee_id, work_date),
                FOREIGN KEY (employee_id)
                    REFERENCES employees(id)
            )
        """)

        # Save all database changes.
        conn.commit()

    except sqlite3.Error:
        # Roll back changes if initialization fails.
        conn.rollback()
        raise

    finally:
        # Release the database connection.
        conn.close()
