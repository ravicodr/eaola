import sqlite3
import datetime

DB_PATH = "emotion_history.db"


def init_db():
    """Create all tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Emotion logs table (now includes session_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            emotion     TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            date        TEXT NOT NULL,
            session_id  INTEGER
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            start_time  TEXT NOT NULL,
            end_time    TEXT,
            duration    TEXT,
            avg_score   INTEGER DEFAULT 0,
            total_alerts INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] emotion_history.db initialized.")


# ─── EMOTION LOGS ────────────────────────────────────────────────────────────

def log_emotion(username, emotion, session_id=None):
    """Insert a new emotion record for a student."""
    now = datetime.datetime.now()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emotion_logs (username, emotion, timestamp, date, session_id) VALUES (?, ?, ?, ?, ?)",
        (username, emotion, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d"), session_id)
    )
    conn.commit()
    conn.close()


def get_all_logs():
    """Fetch all emotion records, newest first."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, emotion, timestamp, date FROM emotion_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_logs_by_student(username):
    """Fetch emotion records for a specific student."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, emotion, timestamp, date FROM emotion_logs WHERE username=? ORDER BY id DESC",
        (username,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_summary():
    """Get count of each emotion across all students."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT emotion, COUNT(*) as count FROM emotion_logs GROUP BY emotion ORDER BY count DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_students():
    """Get list of all unique student usernames who have been logged."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT username FROM emotion_logs ORDER BY username")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


# ─── HEATMAP ─────────────────────────────────────────────────────────────────

def get_heatmap_data(session_id=None):
    """
    Returns heatmap data: for each student, their emotion at each time bucket.
    Format: { "student1": [{"time": "10:01", "emotion": "Engaged"}, ...], ... }
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if session_id:
        cursor.execute(
            """SELECT username, emotion, timestamp FROM emotion_logs
               WHERE session_id=? ORDER BY username, timestamp""",
            (session_id,)
        )
    else:
        # Last 30 minutes of data
        cursor.execute(
            """SELECT username, emotion, timestamp FROM emotion_logs
               WHERE date = ? ORDER BY username, timestamp""",
            (datetime.datetime.now().strftime("%Y-%m-%d"),)
        )

    rows = cursor.fetchall()
    conn.close()

    heatmap = {}
    for username, emotion, timestamp in rows:
        if username not in heatmap:
            heatmap[username] = []
        # Group into 1-minute buckets
        minute = timestamp[:5]  # "HH:MM"
        # Only add if last entry for this minute is different (deduplicate)
        if not heatmap[username] or heatmap[username][-1]['time'] != minute:
            heatmap[username].append({"time": minute, "emotion": emotion})

    return heatmap


# ─── SESSIONS ────────────────────────────────────────────────────────────────

def start_session():
    """Start a new class session, return its ID."""
    now = datetime.datetime.now()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (date, start_time) VALUES (?, ?)",
        (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def end_session(session_id, avg_score, total_alerts):
    """Mark a session as ended and store summary stats."""
    now = datetime.datetime.now()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get start time to compute duration
    cursor.execute("SELECT start_time, date FROM sessions WHERE id=?", (session_id,))
    row = cursor.fetchone()
    duration = "N/A"
    if row:
        start_str = f"{row[1]} {row[0]}"
        try:
            start_dt = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            diff = now - start_dt
            mins = int(diff.total_seconds() // 60)
            secs = int(diff.total_seconds() % 60)
            duration = f"{mins}m {secs}s"
        except Exception:
            pass

    cursor.execute(
        """UPDATE sessions SET end_time=?, duration=?, avg_score=?, total_alerts=?
           WHERE id=?""",
        (now.strftime("%H:%M:%S"), duration, avg_score, total_alerts, session_id)
    )
    conn.commit()
    conn.close()


def get_all_sessions():
    """Fetch all past sessions, newest first."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, date, start_time, end_time, duration, avg_score, total_alerts FROM sessions ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_session_detail(session_id):
    """Fetch session info + emotion breakdown for a specific session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, date, start_time, end_time, duration, avg_score, total_alerts FROM sessions WHERE id=?",
        (session_id,)
    )
    session = cursor.fetchone()

    cursor.execute(
        "SELECT emotion, COUNT(*) FROM emotion_logs WHERE session_id=? GROUP BY emotion ORDER BY COUNT(*) DESC",
        (session_id,)
    )
    emotion_breakdown = cursor.fetchall()

    cursor.execute(
        "SELECT DISTINCT username FROM emotion_logs WHERE session_id=?",
        (session_id,)
    )
    students = [r[0] for r in cursor.fetchall()]

    conn.close()
    return session, emotion_breakdown, students
