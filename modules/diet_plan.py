import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection
import random

class DietPlanWindow:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.target_calories = None
        self.window = tk.Toplevel(parent)
        self.window.title("Diet Plan & Recommendations")
        self.window.geometry("650x550")
        self.window.configure(bg="#f0f4f0")
        self.build_ui()

    def build_ui(self):
        tk.Label(self.window, text="Your Smart Diet Plan",
                 font=("Arial", 16, "bold"),
                 bg="#f0f4f0", fg="#2e7d32").pack(pady=12)

        self.cal_frame = tk.LabelFrame(self.window,
            text="Daily Calorie Target", bg="#f0f4f0", pady=10)
        self.cal_frame.pack(fill="x", padx=20, pady=5)

        self.cal_label = tk.Label(self.cal_frame,
            text="Press Calculate to see your daily calorie needs",
            font=("Arial", 11), bg="#f0f4f0")
        self.cal_label.pack()

        btn_frame = tk.Frame(self.window, bg="#f0f4f0")
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Calculate My Calories",
                  command=self.calculate_calories,
                  bg="#1565c0", fg="white",
                  width=20, pady=6).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Generate Meal Plan",
                  command=self.generate_plan,
                  bg="#2e7d32", fg="white",
                  width=20, pady=6).grid(row=0, column=1, padx=5)

        tk.Label(self.window, text="Recommended Meal Plan",
                 font=("Arial", 12, "bold"),
                 bg="#f0f4f0").pack(pady=(10, 0))

        cols = ("Meal", "Food Item", "Qty", "Calories", "Protein", "Carbs")
        self.tree = ttk.Treeview(self.window,
            columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=95, anchor="center")
        self.tree.pack(fill="x", padx=20, pady=5)

        self.plan_total_label = tk.Label(self.window,
            text="Plan Total: 0 kcal",
            font=("Arial", 11, "bold"),
            bg="#c8e6c9", pady=6)
        self.plan_total_label.pack(fill="x", padx=20)

    def calculate_calories(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT weight, height, age, gender, activity_level, health_goal
                FROM profiles WHERE user_id=%s
            """, (self.user_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                messagebox.showwarning("Warning",
                    "Please complete your profile first!")
                return

            weight, height, age, gender, activity, goal = row

            if gender == "male":
                bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
            else:
                bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)

            multipliers = {
                "sedentary": 1.2, "light": 1.375,
                "moderate": 1.55, "active": 1.725, "very active": 1.9
            }
            tdee = bmr * multipliers.get(activity, 1.55)

            if goal == "lose weight":
                target = tdee - 500
            elif goal in ["gain weight", "build muscle"]:
                target = tdee + 300
            else:
                target = tdee

            self.target_calories = round(target)
            self.cal_label.config(
                text=f"BMR: {round(bmr)} kcal  |  "
                     f"TDEE: {round(tdee)} kcal  |  "
                     f"Target: {self.target_calories} kcal/day")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_plan(self):
        if not self.target_calories:
            messagebox.showwarning("Warning", "Calculate calories first!")
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, calories, protein, carbs, category FROM foods")
            all_foods = cursor.fetchall()
            conn.close()

            meal_calories = {
                "Breakfast": self.target_calories * 0.25,
                "Lunch":     self.target_calories * 0.35,
                "Dinner":    self.target_calories * 0.30,
                "Snack":     self.target_calories * 0.10,
            }

            plan_total = 0
            for meal, cal_budget in meal_calories.items():
                random.shuffle(all_foods)
                remaining = cal_budget
                for food in all_foods:
                    name, cals, prot, carbs, cat = food
                    if remaining <= 0 or cals <= 0:
                        continue
                    qty = min(2, round(remaining / cals, 1))
                    if qty <= 0:
                        continue
                    actual_cal = round(cals * qty)
                    self.tree.insert("", "end", values=(
                        meal, name, qty, actual_cal,
                        round(prot * qty, 1),
                        round(carbs * qty, 1)
                    ))
                    remaining -= actual_cal
                    plan_total += actual_cal
                    if remaining <= 30:
                        break

            self.plan_total_label.config(
                text=f"Plan Total: {round(plan_total)} kcal  "
                     f"| Target: {self.target_calories} kcal")
        except Exception as e:
            messagebox.showerror("Error", str(e))