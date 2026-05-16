import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection
from datetime import date

class FoodLogWindow:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("Food Intake Log")
        self.window.geometry("700x550")
        self.window.configure(bg="#f0f4f0")
        self.foods_data = []
        self.log_ids = []
        self.build_ui()
        self.load_all_foods()
        self.refresh_log()

    def build_ui(self):
        tk.Label(self.window, text="Log Food Intake",
                 font=("Arial", 16, "bold"),
                 bg="#f0f4f0", fg="#2e7d32").pack(pady=10)

        input_frame = tk.LabelFrame(self.window,
            text="Add Food Item", bg="#f0f4f0", padx=10, pady=10)
        input_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(input_frame, text="Search Food:", bg="#f0f4f0").grid(
            row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_foods)
        tk.Entry(input_frame, textvariable=self.search_var,
                 width=30).grid(row=0, column=1, padx=8, pady=4)

        tk.Label(input_frame, text="Select Food:", bg="#f0f4f0").grid(
            row=1, column=0, sticky="w")
        self.food_var = tk.StringVar()
        self.food_dropdown = ttk.Combobox(input_frame,
            textvariable=self.food_var, width=27, state="readonly")
        self.food_dropdown.grid(row=1, column=1, padx=8, pady=4)
        self.food_dropdown.bind("<<ComboboxSelected>>", self.show_food_info)

        tk.Label(input_frame, text="Quantity (servings):", bg="#f0f4f0").grid(
            row=2, column=0, sticky="w")
        self.qty_entry = tk.Entry(input_frame, width=10)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=2, column=1, sticky="w", padx=8)

        tk.Label(input_frame, text="Meal Type:", bg="#f0f4f0").grid(
            row=3, column=0, sticky="w")
        self.meal_var = tk.StringVar(value="breakfast")
        ttk.Combobox(input_frame, textvariable=self.meal_var,
                     values=["breakfast", "lunch", "dinner", "snack"],
                     width=15, state="readonly").grid(
            row=3, column=1, sticky="w", padx=8, pady=4)

        self.info_label = tk.Label(input_frame,
            text="Select a food to see nutrition info",
            bg="#e8f5e9", fg="#1b5e20", font=("Arial", 10), padx=8, pady=5)
        self.info_label.grid(row=4, column=0, columnspan=3,
                              sticky="ew", pady=6)

        tk.Button(input_frame, text="Add to Log",
                  command=self.add_food,
                  bg="#2e7d32", fg="white",
                  width=15, pady=5).grid(row=5, column=1,
                  sticky="e", padx=8, pady=5)

        tk.Label(self.window,
                 text=f"Today's Log ({date.today()})",
                 font=("Arial", 12, "bold"),
                 bg="#f0f4f0").pack(pady=(10, 0))

        cols = ("Food", "Qty", "Meal", "Calories", "Protein", "Carbs", "Fat")
        self.tree = ttk.Treeview(self.window,
            columns=cols, show="headings", height=8)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
        self.tree.pack(fill="x", padx=20, pady=5)

        self.total_label = tk.Label(self.window,
            text="Total Calories Today: 0",
            font=("Arial", 12, "bold"),
            bg="#fff9c4", pady=6)
        self.total_label.pack(fill="x", padx=20)

        tk.Button(self.window, text="Delete Selected Entry",
                  command=self.delete_entry,
                  bg="#c62828", fg="white",
                  width=20, pady=5).pack(pady=5)

    def load_all_foods(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM foods ORDER BY name")
            self.foods_data = cursor.fetchall()
            conn.close()
            self.food_dropdown['values'] = [row[1] for row in self.foods_data]
        except Exception as e:
            print("Load foods error:", e)

    def search_foods(self, *args):
        query = self.search_var.get().lower()
        filtered = [row[1] for row in self.foods_data if query in row[1].lower()]
        self.food_dropdown['values'] = filtered

    def show_food_info(self, event=None):
        selected = self.food_var.get()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT calories, protein, carbs, fat FROM foods WHERE name=%s",
                (selected,))
            row = cursor.fetchone()
            conn.close()
            if row:
                cal, pro, carb, fat = row
                self.info_label.config(
                    text=f"Per serving → Calories: {cal} | "
                         f"Protein: {pro}g | Carbs: {carb}g | Fat: {fat}g")
        except Exception as e:
            print(e)

    def add_food(self):
        selected_name = self.food_var.get()
        if not selected_name:
            messagebox.showerror("Error", "Please select a food!")
            return
        try:
            qty = float(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity!")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM foods WHERE name=%s", (selected_name,))
            food_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO food_logs
                (user_id, food_id, quantity, meal_type, log_date)
                VALUES (%s,%s,%s,%s,%s)
            """, (self.user_id, food_id, qty, self.meal_var.get(), date.today()))
            conn.commit()
            conn.close()
            self.refresh_log()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_log(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.name, fl.quantity, fl.meal_type,
                       ROUND(f.calories*fl.quantity,1),
                       ROUND(f.protein*fl.quantity,1),
                       ROUND(f.carbs*fl.quantity,1),
                       ROUND(f.fat*fl.quantity,1),
                       fl.id
                FROM food_logs fl
                JOIN foods f ON fl.food_id = f.id
                WHERE fl.user_id=%s AND fl.log_date=%s
                ORDER BY fl.id
            """, (self.user_id, date.today()))
            rows = cursor.fetchall()
            conn.close()
            total = 0
            self.log_ids = []
            for row in rows:
                self.tree.insert("", "end", values=row[:7])
                self.log_ids.append(row[7])
                total += row[3]
            self.total_label.config(
                text=f"Total Calories Today: {round(total)} kcal")
        except Exception as e:
            print("Refresh error:", e)

    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a row to delete!")
            return
        idx = self.tree.index(selected[0])
        log_id = self.log_ids[idx]
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM food_logs WHERE id=%s", (log_id,))
            conn.commit()
            conn.close()
            self.refresh_log()
        except Exception as e:
            messagebox.showerror("Error", str(e))