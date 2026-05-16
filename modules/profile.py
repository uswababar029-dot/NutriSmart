import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

class ProfileWindow:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("My Health Profile")
        self.window.geometry("500x600")
        self.window.configure(bg="#f0f4f0")
        self.build_form()
        self.load_existing_profile()

    def build_form(self):
        tk.Label(self.window, text="Health Profile",
                 font=("Arial", 18, "bold"),
                 bg="#f0f4f0", fg="#2e7d32").pack(pady=15)

        frame = tk.Frame(self.window, bg="#f0f4f0")
        frame.pack(padx=30, pady=5)

        self.entries = {}
        fields = ["Full Name", "Age (years)", "Weight (kg)", "Height (cm)"]

        for i, label in enumerate(fields):
            tk.Label(frame, text=label+":", bg="#f0f4f0",
                     width=18, anchor="w").grid(row=i, column=0, pady=6)
            entry = tk.Entry(frame, width=25)
            entry.grid(row=i, column=1, pady=6, padx=10)
            self.entries[label] = entry

        tk.Label(frame, text="Gender:", bg="#f0f4f0",
                 width=18, anchor="w").grid(row=4, column=0, pady=6)
        self.gender_var = tk.StringVar(value="male")
        ttk.Combobox(frame, textvariable=self.gender_var,
                     values=["male", "female"],
                     width=22, state="readonly").grid(row=4, column=1, pady=6, padx=10)

        tk.Label(frame, text="Activity Level:", bg="#f0f4f0",
                 width=18, anchor="w").grid(row=5, column=0, pady=6)
        self.activity_var = tk.StringVar(value="sedentary")
        ttk.Combobox(frame, textvariable=self.activity_var,
                     values=["sedentary", "light", "moderate", "active", "very active"],
                     width=22, state="readonly").grid(row=5, column=1, pady=6, padx=10)

        tk.Label(frame, text="Health Goal:", bg="#f0f4f0",
                 width=18, anchor="w").grid(row=6, column=0, pady=6)
        self.goal_var = tk.StringVar(value="maintain weight")
        ttk.Combobox(frame, textvariable=self.goal_var,
                     values=["lose weight", "maintain weight", "gain weight",
                             "build muscle", "improve fitness"],
                     width=22, state="readonly").grid(row=6, column=1, pady=6, padx=10)

        tk.Label(frame, text="Health Condition:", bg="#f0f4f0",
                 width=18, anchor="w").grid(row=7, column=0, pady=6)
        self.condition_var = tk.StringVar(value="none")
        ttk.Combobox(frame, textvariable=self.condition_var,
                     values=["none", "diabetes", "hypertension",
                             "obesity", "heart disease"],
                     width=22, state="readonly").grid(row=7, column=1, pady=6, padx=10)

        self.bmi_label = tk.Label(self.window,
            text="BMI: Enter weight and height first",
            font=("Arial", 12), bg="#e8f5e9", fg="#1b5e20", pady=8)
        self.bmi_label.pack(pady=10, fill="x", padx=30)

        btn_frame = tk.Frame(self.window, bg="#f0f4f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Calculate BMI",
                  command=self.calculate_bmi,
                  bg="#1565c0", fg="white",
                  width=18, pady=6).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Save Profile",
                  command=self.save_profile,
                  bg="#2e7d32", fg="white",
                  width=18, pady=6).grid(row=0, column=1, padx=5)

    def calculate_bmi(self):
        try:
            weight = float(self.entries["Weight (kg)"].get())
            height = float(self.entries["Height (cm)"].get()) / 100
            bmi = round(weight / (height ** 2), 1)
            if bmi < 18.5:
                category, color = "Underweight", "#1565c0"
            elif bmi < 25:
                category, color = "Normal weight", "#2e7d32"
            elif bmi < 30:
                category, color = "Overweight", "#e65100"
            else:
                category, color = "Obese", "#b71c1c"
            self.bmi_label.config(
                text=f"BMI: {bmi}  |  Category: {category}", fg=color)
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers for weight and height!")

    def save_profile(self):
        try:
            name = self.entries["Full Name"].get().strip()
            age = int(self.entries["Age (years)"].get())
            weight = float(self.entries["Weight (kg)"].get())
            height = float(self.entries["Height (cm)"].get())

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM profiles WHERE user_id=%s", (self.user_id,))
            exists = cursor.fetchone()

            if exists:
                cursor.execute("""
                    UPDATE profiles SET full_name=%s, age=%s, gender=%s,
                    weight=%s, height=%s, activity_level=%s,
                    health_goal=%s, health_condition=%s WHERE user_id=%s
                """, (name, age, self.gender_var.get(), weight, height,
                      self.activity_var.get(), self.goal_var.get(),
                      self.condition_var.get(), self.user_id))
            else:
                cursor.execute("""
                    INSERT INTO profiles
                    (user_id, full_name, age, gender, weight, height,
                     activity_level, health_goal, health_condition)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (self.user_id, name, age, self.gender_var.get(),
                      weight, height, self.activity_var.get(),
                      self.goal_var.get(), self.condition_var.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Profile saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_existing_profile(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE user_id=%s", (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                _, _, name, age, gender, weight, height, activity, goal, cond = row
                self.entries["Full Name"].insert(0, name or "")
                self.entries["Age (years)"].insert(0, str(age or ""))
                self.entries["Weight (kg)"].insert(0, str(weight or ""))
                self.entries["Height (cm)"].insert(0, str(height or ""))
                self.gender_var.set(gender or "male")
                self.activity_var.set(activity or "sedentary")
                self.goal_var.set(goal or "maintain weight")
                self.condition_var.set(cond or "none")
        except Exception as e:
            print("Load error:", e)