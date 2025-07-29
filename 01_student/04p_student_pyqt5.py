import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui, QtCore

class StudentRecordApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Record System")
        self.setWindowIcon(QtGui.QIcon("icon.png"))  # Optional icon
        self.resize(800, 500)

        self.conn = sqlite3.connect("students.db")
        self.create_table()

        self.init_ui()
        self.load_data()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL,
                course TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Search Bar
        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(QtWidgets.QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Roll", "Course"])
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.update_btn = QtWidgets.QPushButton("Update")
        self.delete_btn = QtWidgets.QPushButton("Delete")

        self.add_btn.clicked.connect(self.add_record)
        self.update_btn.clicked.connect(self.update_record)
        self.delete_btn.clicked.connect(self.delete_record)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self.table.setRowCount(0)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students")
        for row_idx, row_data in enumerate(cursor.fetchall()):
            self.table.insertRow(row_idx)
            for col_idx, item in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(item)))

    def filter_data(self):
        text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            self.table.setRowHidden(row, text not in item.text().lower())

    def add_record(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Add Student", "Enter name:")
        if ok and name:
            roll, ok = QtWidgets.QInputDialog.getText(self, "Add Student", "Enter roll:")
            if ok and roll:
                course, ok = QtWidgets.QInputDialog.getText(self, "Add Student", "Enter course:")
                if ok and course:
                    cursor = self.conn.cursor()
                    cursor.execute("INSERT INTO students (name, roll, course) VALUES (?, ?, ?)", (name, roll, course))
                    self.conn.commit()
                    self.load_data()

    def update_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        id = self.table.item(selected, 0).text()
        name, ok = QtWidgets.QInputDialog.getText(self, "Update Student", "Enter name:", text=self.table.item(selected, 1).text())
        if ok and name:
            roll, ok = QtWidgets.QInputDialog.getText(self, "Update Student", "Enter roll:", text=self.table.item(selected, 2).text())
            if ok and roll:
                course, ok = QtWidgets.QInputDialog.getText(self, "Update Student", "Enter course:", text=self.table.item(selected, 3).text())
                if ok and course:
                    cursor = self.conn.cursor()
                    cursor.execute("UPDATE students SET name=?, roll=?, course=? WHERE id=?", (name, roll, course, id))
                    self.conn.commit()
                    self.load_data()

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        id = self.table.item(selected, 0).text()
        confirm = QtWidgets.QMessageBox.question(self, "Delete", f"Delete student ID {id}?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (id,))
            self.conn.commit()
            self.load_data()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = StudentRecordApp()
    window.show()
    sys.exit(app.exec_())
