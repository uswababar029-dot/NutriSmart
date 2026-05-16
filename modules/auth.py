import tkinter as tk
from tkinter import messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

class AuthWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("NutriSmart - Login")
        self.window.geometry("400x450")
        self.window.configure(bg="#f0f4f0")
        self.current_user = None
        self.build_login_screen()
        self.window.mainloop()

    def build_login_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        tk.Label(self.window, text="NutriSmart",
                 font=("Arial", 24, "bold"),
                 bg="#f0f4f0", fg="#2e7d32").pack(pady=30)

        tk.Label(self.window, text="Smart Nutrition Control",
                 font=("Arial", 11),
                 bg="#f0f4f0", fg="#555").pack()

        frame = tk.Frame(self.window, bg="#f0f4f0")
        frame.pack(pady=20)

        tk.Label(frame, text="Username:", bg="#f0f4f0").grid(
            row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(frame, text="Password:", bg="#f0f4f0").grid(
            row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)

        tk.Button(self.window, text="Login",
                  command=self.login,
                  bg="#2e7d32", fg="white",
                  width=20, pady=8).pack(pady=10)

        tk.Button(self.window, text="Register New Account",
                  command=self.build_register_screen,
                  bg="#ffffff", fg="#2e7d32",
                  width=20, pady=8).pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, role FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                user_id, role = result
                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.window.destroy()
                from main import open_main_app
                open_main_app(user_id, username, role)
            else:
                messagebox.showerror("Error", "Wrong username or password!")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def build_register_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        tk.Label(self.window, text="Create Account",
                 font=("Arial", 18, "bold"),
                 bg="#f0f4f0", fg="#2e7d32").pack(pady=20)

        frame = tk.Frame(self.window, bg="#f0f4f0")
        frame.pack(pady=10)

        fields = ["Username", "Password", "Confirm Password"]
        self.reg_entries = {}

        for i, field in enumerate(fields):
            tk.Label(frame, text=field+":", bg="#f0f4f0").grid(
                row=i, column=0, sticky="w", pady=5)
            show = "*" if "Password" in field else ""
            entry = tk.Entry(frame, width=25, show=show)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.reg_entries[field] = entry

        tk.Button(self.window, text="Register",
                  command=self.register,
                  bg="#2e7d32", fg="white",
                  width=20, pady=8).pack(pady=10)

        tk.Button(self.window, text="Back to Login",
                  command=self.build_login_screen,
                  bg="#ffffff", fg="#2e7d32",
                  width=20, pady=8).pack()

    def register(self):
        username = self.reg_entries["Username"].get().strip()
        password = self.reg_entries["Password"].get().strip()
        confirm = self.reg_entries["Confirm Password"].get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Account created! Please login.")
            self.build_login_screen()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

if __name__ == "__main__":
    AuthWindow()