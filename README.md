# TimeTag — RFID-Based Employee Time Tracking System

## About the Project

TimeTag is a desktop application for tracking employees' working hours using RFID cards or key fobs.

The application is being developed in Python and uses SQLite for data storage.

## Tech Stack

* Python
* SQLite (sqlite3)

## Project Structure

TimeTag/
├── database/
│   └── database.py
├── reports/
│   └── report.py
├── services/
│   ├── check_admin.py
│   ├── cli.py
│   ├── employees.py
│   └── rfid_reading.py
├── ui/
│   ├── dialogs/
│   │   ├── add_employee_dialog.py
│   │   ├── delete_employee_dialog.py
│   │   ├── edit_employee_dialog.py
│   │   ├── error_dialog.py
│   │   ├── manual_note_dialog.py
│   │   └── success_dialog.py
│   ├── pages/
│   │   ├── admin_page.py
│   │   ├── home_page.py
│   │   └── reports_page.py
│   ├── main_window.py
│   └── sidebar.py
├── main.py
├── .gitignore
├── README.md
├── run.bat
├── setup.bat
└── requirements.txt

## Getting Started

## Installation and Setup

### 1\. Clone or download the project

Open a terminal in the project directory.

### 2\. Create a virtual environment

```bash
python -m venv .venv
```

### 3\. Activate the virtual environment

**Windows — PowerShell**

```powershell
.\\.venv\\Scripts\\Activate.ps1
```

**Windows — Command Prompt**

```bat
.venv\\Scripts\\activate.bat
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4\. Install dependencies

```bash
pip install -r requirements.txt
```

### 5\.  Run the bot

```bash
python main.py
```

## Quick Start on Windows

You can use the included batch files instead:

1. Run `setup.bat` to prepare the environment.
2. Run `run.bat` to start the bot.

If either script does not work in your environment, follow the manual setup instructions above.

### Prerequisites

* Python 3.10 or later

### Run the Application

From the project root directory, run:

```bash
python main.py
```

The application initializes the SQLite database and creates the required tables if they do not already exist.

## Database Design

The database consists of three tables:

* employees — stores employee information and account status.
* rfid_tags — stores RFID tags information and its association with an employee.
* attendance — stores employees' arrival and departure timestamps.

The database enforces relationships between employees, RFID tags and attendance records using foreign keys. Each employee can have at most one attendance record per calendar day.
