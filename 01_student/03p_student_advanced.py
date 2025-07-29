import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
from PIL import Image, ImageTk

# ------------------------ Database Setup ------------------------ #
conn = sqlite3.connect("students.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    course TEXT
)
""")
conn.commit()

# ------------------------ Functions ------------------------ #
def add_student():
    name, age, course = name_entry.get(), age_entry.get(), course_entry.get()
    if not name or not age or not course:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    cursor.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)", (name, age, course))
    conn.commit()
    refresh_treeview()
    clear_entries()

def update_student():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "No student selected.")
        return
    student_id = tree.item(selected[0])['values'][0]
    cursor.execute("UPDATE students SET name=?, age=?, course=? WHERE id=?",
                   (name_entry.get(), age_entry.get(), course_entry.get(), student_id))
    conn.commit()
    refresh_treeview()
    clear_entries()

def delete_student():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "No student selected.")
        return
    student_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    refresh_treeview()
    clear_entries()

def search_student():
    keyword = search_entry.get()
    query = f"SELECT * FROM students WHERE name LIKE ? OR course LIKE ?"
    results = cursor.execute(query, (f'%{keyword}%', f'%{keyword}%')).fetchall()
    update_treeview(results)

def refresh_treeview():
    cursor.execute("SELECT * FROM students")
    update_treeview(cursor.fetchall())

def update_treeview(data):
    tree.delete(*tree.get_children())
    for row in data:
        tree.insert('', 'end', values=row)

def clear_entries():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)

def export_to_excel():
    cursor.execute("SELECT * FROM students")
    df = pd.DataFrame(cursor.fetchall(), columns=["ID", "Name", "Age", "Course"])
    filepath = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx")])
    if filepath:
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Exported", f"Data exported to {filepath}")

def on_tree_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])['values']
        name_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        course_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])
        age_entry.insert(0, values[2])
        course_entry.insert(0, values[3])

# ------------------------ GUI Setup ------------------------ #
root = tk.Tk()
root.title("Student Record System")
root.geometry("800x500")
root.resizable(True, True)

# Optional logo icon
try:
    img = Image.open("icon.png")  # Your PNG icon file
    img = img.resize((32, 32))
    icon = ImageTk.PhotoImage(img)
    root.iconphoto(False, icon)
except:
    pass

style = ttk.Style()
style.configure("Treeview", font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

form_frame = ttk.LabelFrame(frame, text="Student Details")
form_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

name_entry = ttk.Entry(form_frame, width=20)
name_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Label(form_frame, text="Name:").grid(row=0, column=0)

age_entry = ttk.Entry(form_frame, width=10)
age_entry.grid(row=0, column=3, padx=5, pady=5)
ttk.Label(form_frame, text="Age:").grid(row=0, column=2)

course_entry = ttk.Entry(form_frame, width=20)
course_entry.grid(row=0, column=5, padx=5, pady=5)
ttk.Label(form_frame, text="Course:").grid(row=0, column=4)

ttk.Button(form_frame, text="Add", command=add_student).grid(row=1, column=0, pady=10)
ttk.Button(form_frame, text="Update", command=update_student).grid(row=1, column=1)
ttk.Button(form_frame, text="Delete", command=delete_student).grid(row=1, column=2)
ttk.Button(form_frame, text="Export Excel", command=export_to_excel).grid(row=1, column=3)

search_entry = ttk.Entry(form_frame, width=25)
search_entry.grid(row=1, column=4)
ttk.Button(form_frame, text="Search", command=search_student).grid(row=1, column=5)

# Treeview
columns = ("ID", "Name", "Age", "Course")
tree = ttk.Treeview(frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor=tk.CENTER)

tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

refresh_treeview()
root.mainloop()

