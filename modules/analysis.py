import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalysisWindow:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("Nutritional Analysis & Progress")
        self.window.geometry("750x600")
        self.window.configure(bg="#f0f4f0")
        self.build_ui()
        self.show_weekly_chart()

    def build_ui(self):
        tk.Label(self.window, text="Nutritional Analysis",
                 font=("Arial", 16, "bold"),
                 bg="#f0f4f0", fg="#2e7d32").pack(pady=10)

        btn_frame = tk.Frame(self.window, bg="#f0f4f0")
        btn_frame.pack()

        tk.Button(btn_frame, text="Weekly Calorie Chart",
                  command=self.show_weekly_chart,
                  bg="#1565c0", fg="white",
                  width=20, pady=6).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Macronutrient Pie Chart",
                  command=self.show_macro_pie,
                  bg="#6a1b9a", fg="white",
                  width=20, pady=6).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Today's Summary",
                  command=self.show_today_summary,
                  bg="#e65100", fg="white",
                  width=20, pady=6).grid(row=0, column=2, padx=5)

        self.chart_frame = tk.Frame(self.window, bg="#f0f4f0")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def clear_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def show_weekly_chart(self):
        self.clear_chart()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            dates, calories = [], []
            for i in range(6, -1, -1):
                day = date.today() - timedelta(days=i)
                cursor.execute("""
                    SELECT COALESCE(SUM(f.calories * fl.quantity), 0)
                    FROM food_logs fl
                    JOIN foods f ON fl.food_id = f.id
                    WHERE fl.user_id=%s AND fl.log_date=%s
                """, (self.user_id, day))
                total = cursor.fetchone()[0]
                dates.append(day.strftime("%a\n%d"))
                calories.append(float(total))
            conn.close()

            fig, ax = plt.subplots(figsize=(7, 4))
            bars = ax.bar(dates, calories, color="#2e7d32",
                          alpha=0.8, edgecolor="white")
            ax.set_title("Calorie Intake — Last 7 Days",
                         fontsize=13, fontweight="bold")
            ax.set_ylabel("Calories (kcal)")
            ax.set_ylim(0, max(calories + [2000]) * 1.2)
            for bar, val in zip(bars, calories):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 20,
                            f"{int(val)}", ha="center",
                            va="bottom", fontsize=9)
            ax.axhline(y=2000, color="red", linestyle="--",
                       alpha=0.6, label="Target 2000")
            ax.legend()
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_macro_pie(self):
        self.clear_chart()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(f.protein*fl.quantity),
                       SUM(f.carbs*fl.quantity),
                       SUM(f.fat*fl.quantity)
                FROM food_logs fl
                JOIN foods f ON fl.food_id=f.id
                WHERE fl.user_id=%s AND fl.log_date=%s
            """, (self.user_id, date.today()))
            row = cursor.fetchone()
            conn.close()
            protein = float(row[0] or 0)
            carbs   = float(row[1] or 0)
            fat     = float(row[2] or 0)
            if protein + carbs + fat == 0:
                messagebox.showinfo("Info", "No food logged today yet!")
                return
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.pie([protein, carbs, fat],
                   labels=[f"Protein\n{protein:.1f}g",
                            f"Carbs\n{carbs:.1f}g",
                            f"Fat\n{fat:.1f}g"],
                   colors=["#1565c0", "#2e7d32", "#e65100"],
                   autopct="%1.1f%%", startangle=90)
            ax.set_title("Today's Macronutrient Breakdown",
                         fontsize=13, fontweight="bold")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_today_summary(self):
        self.clear_chart()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(fl.id),
                       COALESCE(SUM(f.calories*fl.quantity),0),
                       COALESCE(SUM(f.protein*fl.quantity),0),
                       COALESCE(SUM(f.carbs*fl.quantity),0),
                       COALESCE(SUM(f.fat*fl.quantity),0),
                       COALESCE(SUM(f.fiber*fl.quantity),0)
                FROM food_logs fl
                JOIN foods f ON fl.food_id=f.id
                WHERE fl.user_id=%s AND fl.log_date=%s
            """, (self.user_id, date.today()))
            row = cursor.fetchone()
            conn.close()
            items, cals, prot, carbs, fat, fiber = row
            summary = tk.Frame(self.chart_frame, bg="#f0f4f0")
            summary.pack(pady=20, fill="x")
            stats = [
                ("Food Items Logged", str(items),       "#1565c0"),
                ("Total Calories",    f"{round(cals)} kcal", "#2e7d32"),
                ("Protein",           f"{round(prot,1)} g",  "#8e24aa"),
                ("Carbohydrates",     f"{round(carbs,1)} g", "#e65100"),
                ("Fat",               f"{round(fat,1)} g",   "#c62828"),
                ("Fiber",             f"{round(fiber,1)} g", "#37474f"),
            ]
            for i, (label, value, color) in enumerate(stats):
                card = tk.Frame(summary, bg="white", relief="ridge", bd=1)
                card.grid(row=i//3, column=i%3, padx=10, pady=8,
                          ipadx=15, ipady=10)
                tk.Label(card, text=label, font=("Arial", 10),
                         fg="gray", bg="white").pack()
                tk.Label(card, text=value, font=("Arial", 16, "bold"),
                         fg=color, bg="white").pack()
        except Exception as e:
            messagebox.showerror("Error", str(e))