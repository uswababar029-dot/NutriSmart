CREATE DATABASE if not exists  nutrismart;
USE nutrismart;

USE nutrismart;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user','admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    full_name VARCHAR(100),
    age INT,
    gender ENUM('male','female'),
    weight FLOAT,
    height FLOAT,
    activity_level VARCHAR(50),
    health_goal VARCHAR(100),
    health_condition VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    calories FLOAT,
    protein FLOAT,
    carbs FLOAT,
    fat FLOAT,
    fiber FLOAT,
    category VARCHAR(50)
);

CREATE TABLE food_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    food_id INT,
    quantity FLOAT,
    meal_type ENUM('breakfast','lunch','dinner','snack'),
    log_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

CREATE TABLE diet_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    plan_date DATE,
    meal_type VARCHAR(50),
    food_name VARCHAR(100),
    recommended_qty FLOAT,
    calories FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
-- Default admin account
INSERT INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin');

-- Sample food items
INSERT INTO foods (name, calories, protein, carbs, fat, fiber, category) VALUES
('Rice (1 cup)', 206, 4.3, 45, 0.4, 0.6, 'Grain'),
('Chicken Breast (100g)', 165, 31, 0, 3.6, 0, 'Protein'),
('Apple', 95, 0.5, 25, 0.3, 4.4, 'Fruit'),
('Egg (1 whole)', 78, 6, 0.6, 5, 0, 'Protein'),
('Milk (1 cup)', 149, 8, 12, 8, 0, 'Dairy'),
('Banana', 105, 1.3, 27, 0.4, 3.1, 'Fruit'),
('Brown Bread (1 slice)', 69, 3.6, 12, 1.1, 1.9, 'Grain'),
('Lentils (1 cup)', 230, 18, 40, 0.8, 16, 'Protein'),
('Yogurt (1 cup)', 100, 17, 6, 0.7, 0, 'Dairy'),
('Chapati (1 piece)', 120, 3.1, 18, 3.7, 2.2, 'Grain'),
('Dal (1 cup)', 180, 12, 30, 0.9, 8, 'Protein'),
('Orange', 62, 1.2, 15, 0.2, 3.1, 'Fruit');