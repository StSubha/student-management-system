# 🎓 Student Management System

A desktop GUI application for managing student records — add, update,
delete, search, and export data — built with **PyQt5** and **SQLite**.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

## Features
- **Add / Update / Delete** student records with validated input (age must
  be a real number in a sane range, required fields enforced)
- **Live search** — filters the table as you type, matching name, course,
  or email
- **Export to Excel or CSV** — choose the format when saving
- **Course dropdown** with common presets (editable, so you can still type
  a custom course if it's not in the list) — keeps data consistent instead
  of relying on free-text entry
- **Delete confirmation dialog** to prevent accidental data loss
- **Click-to-edit**: selecting a row in the table auto-fills the form for
  quick updates
- Persistent storage via SQLite — data survives between sessions

## Architecture
The app separates concerns into two layers:
- `Database` class — handles all SQLite queries, isolated from the UI
- `StudentManagementApp` class — handles the PyQt5 interface and user
  interaction

This separation makes it straightforward to swap the storage layer (e.g.
to PostgreSQL) or the UI layer later without rewriting both.

## Tech Stack
Python, PyQt5, SQLite3

## How to run locally
```bash
git clone https://github.com/StSubha/student-management-system.git
cd student-management-system
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python main.py
```

## What I'd improve with more time
- Add data validation for email format
- Add sorting by column (click table headers)
- Add pagination for large student lists
- Package as a standalone `.exe` with PyInstaller for non-technical users
- Add unit tests for the `Database` class
