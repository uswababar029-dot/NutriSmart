import tkinter as tk
import importlib

def open_main_app(user_id, username, role):
    root = tk.Tk()
    root.title(f"NutriSmart — {username}")
    root.geometry("500x420")
    root.configure(bg="#f0f4f0")

    tk.Label(root, text=f"Welcome, {username}!",
             font=("Arial", 18, "bold"),
             bg="#f0f4f0", fg="#2e7d32").pack(pady=20)

    tk.Label(root, text="What would you like to do today?",
             font=("Arial", 11),
             bg="#f0f4f0", fg="#555").pack()

    btn_frame = tk.Frame(root, bg="#f0f4f0")
    btn_frame.pack(pady=20)

    user_buttons = [
        ("My Profile & BMI",  "modules.profile",   "ProfileWindow"),
        ("Log Food Intake",   "modules.food_log",  "FoodLogWindow"),
        ("My Diet Plan",      "modules.diet_plan", "DietPlanWindow"),
        ("View Analysis",     "modules.analysis",  "AnalysisWindow"),
    ]

    for i, (label, mod, cls) in enumerate(user_buttons):
        def make_cmd(m, c):
            def cmd():
                module = importlib.import_module(m)
                getattr(module, c)(root, user_id)
            return cmd
        tk.Button(btn_frame, text=label,
                  command=make_cmd(mod, cls),
                  bg="#ffffff", fg="#2e7d32",
                  width=22, pady=8,
                  relief="ridge").grid(
            row=i // 2, column=i % 2, padx=10, pady=5)

    if role == "admin":
        tk.Label(root, text="Admin Tools",
                 font=("Arial", 11, "bold"),
                 bg="#f0f4f0", fg="#e65100").pack(pady=5)
        admin_frame = tk.Frame(root, bg="#f0f4f0")
        admin_frame.pack()

        admin_buttons = [
            ("Manage Food DB",  "modules.food_db", "FoodDBWindow"),
            ("User Management", "modules.admin",   "AdminWindow"),
        ]
        for i, (label, mod, cls) in enumerate(admin_buttons):
            def make_admin(m, c):
                def cmd():
                    module = importlib.import_module(m)
                    getattr(module, c)(root)
                return cmd
            tk.Button(admin_frame, text=label,
                      command=make_admin(mod, cls),
                      bg="#fbe9e7", fg="#e65100",
                      width=20, pady=6).grid(
                row=0, column=i, padx=10)

    tk.Button(root, text="Logout",
              command=root.destroy,
              bg="#f5f5f5", fg="#555",
              width=15, pady=6).pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    from modules.auth import AuthWindow
    AuthWindow()