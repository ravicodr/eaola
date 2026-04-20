import sqlite3
import datetime

DB_PATH = "emotion_history.db"


def init_users_table():
    """Create the users table in the existing DB if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password      TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            role          TEXT NOT NULL DEFAULT 'student',
            created_at    TEXT NOT NULL
        )
    ''')
    # Insert default teacher and student accounts if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        defaults = [
            ("teacher",  "123", "teacher@example.com",  "teacher",  now),
            ("student",  "123", "student@example.com",  "student",  now),
            ("student2", "123", "student2@example.com", "student",  now),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, email, role, created_at) VALUES (?,?,?,?,?)",
            defaults
        )
    conn.commit()
    conn.close()
    print("[DB] Users table initialized.")


def create_user(username, password, email, role):
    """
    Register a new user.
    Returns (True, "success") or (False, "error message").
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (username, password, email, role, created_at) VALUES (?,?,?,?,?)",
            (username.strip(), password, email.strip().lower(), role, now)
        )
        conn.commit()
        return True, "success"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken. Please choose another."
        elif "email" in str(e):
            return False, "Email already registered. Try logging in."
        return False, "Registration failed. Please try again."
    finally:
        conn.close()


def get_user_by_username(username):
    """Return user dict or None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password, email, role FROM users WHERE username=?",
        (username.strip(),)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "password": row[1],
                "email": row[2], "role": row[3]}
    return None


def get_user_by_email(email):
    """Return user dict or None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password, email, role FROM users WHERE email=?",
        (email.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "password": row[1],
                "email": row[2], "role": row[3]}
    return None


def get_all_users():
    """Return all registered users (for admin view)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, role, created_at FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_password(username, new_password):
    """Update a user's password."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()
