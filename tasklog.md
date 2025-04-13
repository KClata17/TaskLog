#  TaskLog – A task Management System Web Application Using Flask & SQLite

**TaskLog** is a simple, secure, and user-friendly web app that allows individuals to manage their daily tasks.
Built with Flask and SQLite, it supports user registration, login, task creation with categories, status updates, 
and more — all in a clean, minimal interface.

---

##  Project Overview

- **Project Name**: TaskLog  
- **Language**: Python  
- **Framework**: Flask  
- **Database**: SQLite (`TaskLog_database.db`)  
- **ORM**: SQLAlchemy  
- **Authentication**: Flask-Login with secure password hashing

---

## Folder & File Structure
TaskLog/
├── app.py                          # Main Flask application with all routes, models, and logic
├── add_column.py                   # Script for adding columns to the DB (optional migration)
│
├── instance/                       # Folder for runtime configuration or DB if needed
│   └── (empty or can contain config.py / DB)
│
├── static/                         # Static assets CSS 
│   └── css/
│       └── style.css               # Main stylesheet for styling the web pages
│
├── templates/                      # All HTML templates rendered by Flask
│   ├── base.html                   # Base layout template with common structure (navbar, etc.)
│   ├── home.html                   # Homepage shown at `/`
│   ├── login.html                  # Login form
│   ├── user.html                   # Registration form
│   ├── userdetail.html             # List of all registered users
│   ├── updateuser.html             # User profile update form
│   ├── dashboard.html              # Dashboard view after login
│   ├── userdash.html               # User-specific dashboard
│   ├── tasklog.html                # Form to add new tasks
│   ├── tasklogdetail.html          # All tasks with status and category info
│   ├── updatetasklog.html          # Form to edit existing task
│   ├── completed_task.html         # View all completed tasks
│   ├── pending_tasks.html          # View all pending tasks
│   └── category_view.html          # Tasks filtered by category
│
├── __pycache__/                    # Auto-generated folder with compiled Python files
│   └── *.pyc                       # Bytecode cache files
│
├── .gitignore                      # Tells Git to ignore venv, __pycache__, *.db, etc.
├── README.md                       #  Project documentation (this file)
└── requirements.txt                # List of dependencies to install




---

## Database Design

This project uses **SQLite**, a lightweight relational DB, ideal for development.

### Tables Used:

- **`user_register`**  
  Stores user credentials (name, email, password) with hashed passwords.

- **`TaskLog`**  
  Each user’s tasks: title, description, status (pending/done), created date.

- **`task_catagories`**  
  Optional categories assigned to each task.

### Relationships:

one user - many tasks
one task - one category

---

##  Key Features

- User Registration & Login
- Secure Password Storage (with hashing)
- Task Creation, Update, Deletion
- Task Categories (Work, Personal, etc.)
- Status Toggle: Pending / Done
- View Tasks by Category or Status
- Flask Session Management

---

## Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/KClata17/TaskLog.git
cd TaskLog

###
python -m venv venv
venv\Scripts\activate   # (Windows)


pip install flask flask-sqlalchemy flask-login

##  
python app.py
Open your browser and navigate to http://127.0.0.1:5000/
Youtube Video link: https://youtu.be/2i_zjjIVwR0?si=hHr9jkJAx1SlDwuE


Github link https://github.com/KClata17/TaskLog