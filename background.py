import threading
import time
import datetime
from collections import Counter

from models import (active_student_sessions, class_history,
                    auto_confusion_alert, confusion_alerts)

CONFUSION_THRESHOLD = 3


def record_history():
    while True:
        time.sleep(5)
        if active_student_sessions:
            statuses = [
                s['status'] for s in active_student_sessions.values()
                if s['status'] != "Camera Off"
            ]
            if statuses:
                counts  = Counter(statuses)
                total   = len(statuses)
                positive = counts.get("Engaged", 0) + counts.get("Thinking", 0)
                score   = int((positive / total) * 100) if total > 0 else 0
                dominant = counts.most_common(1)[0][0] if counts else "Thinking"

                # Store per-emotion percentages for multi-line chart
                snapshot = {
                    "time":       datetime.datetime.now().strftime("%H:%M:%S"),
                    "score":      score,
                    "active":     total,
                    "vibe":       dominant,
                    # Each emotion as a percentage of active students
                    "Engaged":    round((counts.get("Engaged",    0) / total) * 100),
                    "Thinking":   round((counts.get("Thinking",   0) / total) * 100),
                    "Bored":      round((counts.get("Bored",      0) / total) * 100),
                    "Distracted": round((counts.get("Distracted", 0) / total) * 100),
                    "Confused":   round((counts.get("Confused",   0) +
                                         counts.get("Frustrated", 0)) / total * 100),
                }
                class_history.append(snapshot)

                # Keep last 60 snapshots (5 minutes of data)
                if len(class_history) > 60:
                    class_history.pop(0)

                # Auto confusion alert
                confused_count = counts.get("Confused", 0) + counts.get("Frustrated", 0)
                if confused_count >= CONFUSION_THRESHOLD:
                    auto_confusion_alert["active"] = True
                    auto_confusion_alert["count"]  = confused_count
                    auto_confusion_alert["time"]   = datetime.datetime.now().strftime("%H:%M:%S")
                    confusion_alerts.append(
                        f"AUTO: {confused_count} students confused at {auto_confusion_alert['time']}"
                    )
                else:
                    auto_confusion_alert["active"] = False


def start_background_workers():
    t = threading.Thread(target=record_history)
    t.daemon = True
    t.start()
    print("[BACKGROUND] History recorder + confusion monitor started.")
