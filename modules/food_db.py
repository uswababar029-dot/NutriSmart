import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_connection

class FoodDBWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Food Database Management")
        self.window.geometry("750x550")
        self.window.configure(bg="#f0f4f0")
        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        tk.Label(self.window, text="Food Database Manager",
                 font=("Arial", 16, "bold"),
                 bg="#f0f4f0", fg="#e65100").pack(pady=10)

        form = tk.LabelFrame(self.window, text="Add Food",
                             bg="#f0f4f0", padx=10, pady=5)
        form.pack(fill="x", padx=20, pady=5)

        self.form_entries = {}
        fields = [("Name",12),("Calories",8),("Protein(g)",8),
                  ("Carbs(g)",8),("Fat(g)",8),("Fiber(g)",8),
                  ("Category",10)]

        for i, (label, width) in enumerate(fields):
            tk.Label(form, text=label+":", bg="#f0f4f0",
                     font=("Arial", 9)).grid(row=0, column=i*2, padx=4)
            entry = tk.Entry(form, width=width)
            entry.grid(row=0, column=i*2+1, padx=4)
            self.form_entries[label] = entry

        btn_frame = tk.Frame(form, bg="#f0f4f0")
        btn_frame.grid(row=1, column=0, columnspan=14, pady=6)

        tk.Button(btn_frame, text="Add Food",
                  command=self.add_food,
                  bg="#2e7d32", fg="white",
                  width=12, pady=4).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Delete Selected",
                  command=self.delete_food,
                  bg="#c62828", fg="white",
                  width=14, pady=4).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Refresh",
                  command=self.refresh_table,
                  bg="#1565c0", fg="white",
                  width=10, pady=4).pack(side="left", padx=5)

        search_frame = tk.Frame(self.window, bg="#f0f4f0")
        search_frame.pack(fill="x", padx=20, pady=4)
        tk.Label(search_frame, text="Search:", bg="#f0f4f0").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh_table())
        tk.Entry(search_frame, textvariable=self.search_var,
                 width=30).pack(side="left", padx=8)

        cols = ("ID","Name","Calories","Protein","Carbs",
                "Fat","Fiber","Category")
        self.tree = ttk.Treeview(self.window,
            columns=cols, show="headings", height=12)
        widths = [40,160,80,70,70,60,60,90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="x", padx=20, pady=5)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, calories, protein, carbs,
                       fat, fiber, category
                FROM foods WHERE name LIKE %s ORDER BY name
            """, (f"%{self.search_var.get()}%",))
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print(e)

    def add_food(self):
        try:
            e = self.form_entries
            name = e["Name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Name required!")
                return
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO foods
                (name,calories,protein,carbs,fat,fiber,category)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (name,
                  float(e["Calories"].get() or 0),
                  float(e["Protein(g)"].get() or 0),
                  float(e["Carbs(g)"].get() or 0),
                  float(e["Fat(g)"].get() or 0),
                  float(e["Fiber(g)"].get() or 0),
                  e["Category"].get().strip()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Food added!")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_food(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a row!")
            return
        food_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete this food item?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM foods WHERE id=%s", (food_id,))
                conn.commit()
                conn.close()
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))