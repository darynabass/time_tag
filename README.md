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
├── main.py
├── .gitignore
├── README.md
└── requirements.txt

## Getting Started

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
