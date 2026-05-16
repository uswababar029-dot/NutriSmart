import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

class AdminWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Admin — User Management")
        self.window.geometry("600x400")
        self.window.configure(bg="#f0f4f0")
        self.build_ui()

    def build_ui(self):
        tk.Label(self.window, text="All Users",
                 font=("Arial", 16, "bold"),
                 bg="#f0f4f0", fg="#e65100").pack(pady=15)

        cols = ("ID", "Username", "Role", "Created At")
        self.tree = ttk.Treeview(self.window,
            columns=cols, show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(fill="x", padx=20)

        tk.Button(self.window, text="Refresh",
                  command=self.load_users,
                  bg="#1565c0", fg="white",
                  width=15, pady=6).pack(pady=10)

        self.load_users()

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role, created_at FROM users")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print("Admin load error:", e)