# --- GLOBAL STATE & DATA STORES ---

active_student_sessions = {}
class_history = []
confusion_alerts = []
attendance_log = {}
sentiment_logs = []
active_peers = []
camera_states = {}

# --- FEATURE: RAISE HAND QUEUE ---
hand_raise_queue = []   # list of {username, time}

# --- FEATURE: AUTO CONFUSION ALERT ---
auto_confusion_alert = {
    "active": False,
    "count": 0,
    "time": ""
}

# --- FEATURE: SESSION TRACKING ---
current_session = {
    "id": None,
    "start_time": None,
    "active": False
}

poll_state = {
    "active": False,
    "question": "",
    "options": {},
    "voted_users": []
}

# --- FEATURE: MEETING LINK ---
meeting_state = {
    "active": False,
    "room_id": None,
    "created_at": None
}

# --- FEATURE: TEACHER PIP (Picture-in-Picture live feed for students) ---
teacher_pip = {
    "active": False
}

users = {
    "teacher": {"password": "123", "role": "teacher", "email": "teacher@example.com"},
    "student": {"password": "123", "role": "student", "email": "student@example.com"},
    "student2": {"password": "123", "role": "student", "email": "student2@example.com"},
}
