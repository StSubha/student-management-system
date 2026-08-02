"""
Student Management System — PyQt5 + SQLite

A desktop GUI application for managing student records: add, update, delete,
search, and export to CSV. Includes input validation and a clean, modern
interface built with PyQt5's QTableWidget.

Run with: python main.py
"""

import sys
import sqlite3
import csv
from openpyxl import Workbook
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QMessageBox, QFileDialog, QHeaderView, QStatusBar, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DB_NAME = "students.db"

COURSES = [
    "BSc Data Science", "BSc Computer Science", "BCA", "BTech CSE",
    "BTech IT", "BCom", "BA", "BBA", "MSc Data Science", "MCA", "Other",
]


class Database:
    """Handles all SQLite operations, kept separate from the UI layer."""

    def __init__(self, db_name=DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                course TEXT NOT NULL,
                email TEXT
            )
        """)
        self.conn.commit()

    def add(self, name, age, course, email):
        self.cursor.execute(
            "INSERT INTO students (name, age, course, email) VALUES (?, ?, ?, ?)",
            (name, age, course, email),
        )
        self.conn.commit()

    def update(self, student_id, name, age, course, email):
        self.cursor.execute(
            "UPDATE students SET name=?, age=?, course=?, email=? WHERE id=?",
            (name, age, course, email, student_id),
        )
        self.conn.commit()

    def delete(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
        self.conn.commit()

    def search(self, keyword):
        query = "SELECT * FROM students WHERE name LIKE ? OR course LIKE ? OR email LIKE ?"
        like = f"%{keyword}%"
        return self.cursor.execute(query, (like, like, like)).fetchall()

    def all_students(self):
        return self.cursor.execute("SELECT * FROM students ORDER BY id").fetchall()

    def close(self):
        self.conn.close()


class StudentManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.selected_id = None
        self._init_ui()
        self.refresh_table()

    def _init_ui(self):
        self.setWindowTitle("Student Management System")
        self.setGeometry(200, 100, 900, 550)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        title = QLabel("🎓 Student Management System")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # --- Form ---
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.course_input = QComboBox()
        self.course_input.addItems(COURSES)
        self.course_input.setEditable(True)  # still allows typing a custom course
        self.email_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Course:", self.course_input)
        form_layout.addRow("Email:", self.email_input)
        main_layout.addLayout(form_layout)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add")
        update_btn = QPushButton("✏️ Update")
        delete_btn = QPushButton("🗑️ Delete")
        clear_btn = QPushButton("🧹 Clear")
        export_btn = QPushButton("📤 Export")

        add_btn.clicked.connect(self.add_student)
        update_btn.clicked.connect(self.update_student)
        delete_btn.clicked.connect(self.delete_student)
        clear_btn.clicked.connect(self.clear_form)
        export_btn.clicked.connect(self.export_data)

        for b in (add_btn, update_btn, delete_btn, clear_btn, export_btn):
            btn_layout.addWidget(b)
        main_layout.addLayout(btn_layout)

        # --- Search ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, course, or email...")
        self.search_input.textChanged.connect(self.search_students)
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Course", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.load_selected_row)
        main_layout.addWidget(self.table)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    # ------------------------ Actions ------------------------ #
    def _validate_inputs(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        course = self.course_input.currentText().strip()

        if not name or not age or not course:
            QMessageBox.warning(self, "Input Error", "Name, Age, and Course are required.")
            return None
        if not age.isdigit() or not (1 <= int(age) <= 120):
            QMessageBox.warning(self, "Input Error", "Age must be a valid number.")
            return None
        return name, int(age), course, self.email_input.text().strip()

    def add_student(self):
        data = self._validate_inputs()
        if not data:
            return
        self.db.add(*data)
        self.status.showMessage(f"Added {data[0]}", 3000)
        self.clear_form()
        self.refresh_table()

    def update_student(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Selection Error", "Select a student to update first.")
            return
        data = self._validate_inputs()
        if not data:
            return
        self.db.update(self.selected_id, *data)
        self.status.showMessage(f"Updated {data[0]}", 3000)
        self.clear_form()
        self.refresh_table()

    def delete_student(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Selection Error", "Select a student to delete first.")
            return
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Delete this student record? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.db.delete(self.selected_id)
            self.status.showMessage("Student deleted", 3000)
            self.clear_form()
            self.refresh_table()

    def search_students(self):
        keyword = self.search_input.text().strip()
        rows = self.db.search(keyword) if keyword else self.db.all_students()
        self._populate_table(rows)

    def clear_form(self):
        self.name_input.clear()
        self.age_input.clear()
        self.course_input.setCurrentIndex(-1)
        self.email_input.clear()
        self.selected_id = None
        self.table.clearSelection()

    def load_selected_row(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        self.selected_id = int(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.age_input.setText(self.table.item(row, 2).text())
        self.course_input.setCurrentText(self.table.item(row, 3).text())
        self.email_input.setText(self.table.item(row, 4).text())

    def refresh_table(self):
        self._populate_table(self.db.all_students())

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.status.showMessage(f"{len(rows)} student(s)", 3000)

    def export_data(self):
        rows = self.db.all_students()
        if not rows:
            QMessageBox.information(self, "No Data", "There are no records to export.")
            return

        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Student Data", "students.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)",
        )
        if not filepath:
            return

        headers = ["ID", "Name", "Age", "Course", "Email"]

        if filepath.endswith(".csv"):
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
        else:
            if not filepath.endswith(".xlsx"):
                filepath += ".xlsx"
            wb = Workbook()
            ws = wb.active
            ws.title = "Students"
            ws.append(headers)
            for row in rows:
                ws.append(row)
            # widen columns a bit so data isn't cramped on open
            for col_cells in ws.columns:
                max_len = max(len(str(c.value)) for c in col_cells)
                ws.column_dimensions[col_cells[0].column_letter].width = max_len + 4
            wb.save(filepath)

        QMessageBox.information(self, "Exported", f"Data exported to {filepath}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = StudentManagementApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
