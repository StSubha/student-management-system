
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Connect to SQLite (or create if not exists)
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT NOT NULL UNIQUE,
        department TEXT NOT NULL
    )
''')
conn.commit()

# GUI
root = tk.Tk()
root.title("Student Record System")
root.geometry("700x500")
root.config(bg="#f4f4f4")

# Labels and Inputs
tk.Label(root, text="Name", font=("Arial", 12)).place(x=30, y=30)
tk.Label(root, text="Roll No", font=("Arial", 12)).place(x=30, y=70)
tk.Label(root, text="Department", font=("Arial", 12)).place(x=30, y=110)

name_var = tk.StringVar()
roll_var = tk.StringVar()
dept_var = tk.StringVar()
search_var = tk.StringVar()

name_entry = tk.Entry(root, textvariable=name_var, width=30)
roll_entry = tk.Entry(root, textvariable=roll_var, width=30)
dept_entry = tk.Entry(root, textvariable=dept_var, width=30)
search_entry = tk.Entry(root, textvariable=search_var, width=25)

name_entry.place(x=150, y=30)
roll_entry.place(x=150, y=70)
dept_entry.place(x=150, y=110)
search_entry.place(x=450, y=20)

# Table (Treeview)
tree = ttk.Treeview(root, columns=("ID", "Name", "Roll", "Department"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Roll", text="Roll No")
tree.heading("Department", text="Department")
tree.place(x=30, y=200, width=640, height=250)

def clear_form():
    name_var.set("")
    roll_var.set("")
    dept_var.set("")

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

def add_student():
    name = name_var.get()
    roll = roll_var.get()
    dept = dept_var.get()
    if name and roll and dept:
        try:
            cursor.execute("INSERT INTO students (name, roll, department) VALUES (?, ?, ?)", (name, roll, dept))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully")
            refresh_table()
            clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll number must be unique")
    else:
        messagebox.showwarning("Input Error", "All fields are required")

def select_item(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected, 'values')
        name_var.set(values[1])
        roll_var.set(values[2])
        dept_var.set(values[3])

def update_student():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Selection Error", "Select a student to update")
        return

    values = tree.item(selected, 'values')
    id = values[0]

    new_name = name_var.get()
    new_roll = roll_var.get()
    new_dept = dept_var.get()

    try:
        cursor.execute("UPDATE students SET name=?, roll=?, department=? WHERE id=?",
                       (new_name, new_roll, new_dept, id))
        conn.commit()
        messagebox.showinfo("Updated", "Student record updated")
        refresh_table()
        clear_form()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Roll number must be unique")

def delete_student():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Selection Error", "Select a student to delete")
        return
    id = tree.item(selected, 'values')[0]
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    messagebox.showinfo("Deleted", "Student deleted successfully")
    refresh_table()
    clear_form()

def search_student():
    query = search_var.get()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM students WHERE name LIKE ? OR roll LIKE ?", (f"%{query}%", f"%{query}%"))
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

# Buttons
tk.Button(root, text="Add", width=12, command=add_student).place(x=30, y=150)
tk.Button(root, text="Update", width=12, command=update_student).place(x=150, y=150)
tk.Button(root, text="Delete", width=12, command=delete_student).place(x=270, y=150)
tk.Button(root, text="Clear", width=12, command=clear_form).place(x=390, y=150)
tk.Button(root, text="Search", width=12, command=search_student).place(x=580, y=18)

tree.bind("<ButtonRelease-1>", select_item)

# Start
refresh_table()
root.mainloop()
