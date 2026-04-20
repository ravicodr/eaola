import datetime
from collections import Counter
from flask import Blueprint, request, session, jsonify
from textblob import TextBlob

from models import (active_student_sessions, class_history, confusion_alerts,
                    sentiment_logs, active_peers, camera_states, poll_state,
                    hand_raise_queue, auto_confusion_alert, current_session, teacher_pip)
from config import TEACHER_SUGGESTIONS

api_bp = Blueprint('api', __name__)


@api_bp.route('/get_stats')
def get_stats():
    # ── Only count active students (1 entry per student, keyed by username) ──
    valid = {u: s for u, s in active_student_sessions.items()
             if s['status'] != "Camera Off"}

    if not valid:
        current_counts = {"Engaged": 0, "Thinking": 0, "Bored": 0,
                          "Distracted": 0, "Confused": 0}
        active_count   = 0
        vibe           = "Waiting..."
        students_list  = []
    else:
        statuses       = [s['status'] for s in valid.values()]
        active_count   = len(statuses)
        current_counts = Counter(statuses)
        vibe           = current_counts.most_common(1)[0][0]
        # Build student list with name + current emotion (1 per student)
        students_list  = [{"username": u, "status": s['status']}
                          for u, s in valid.items()]

    advice           = TEACHER_SUGGESTIONS.get(vibe, "Monitoring class...")
    latest_sentiment = sentiment_logs[-1] if sentiment_logs else None

    poll_data = {
        "active":    poll_state['active'],
        "question":  poll_state['question'],
        "options":   poll_state['options'],
        "has_voted": session.get('user') in poll_state['voted_users']
    }

    user       = session.get('user', '')
    hand_raised = any(h['username'] == user for h in hand_raise_queue)

    return jsonify({
        "active_students": active_count,
        "current_vibe":    vibe,
        "teacher_advice":  advice,
        "latest_sentiment": latest_sentiment,
        "poll":            poll_data,
        "history": {
            "Engaged":    current_counts.get("Engaged", 0),
            "Thinking":   current_counts.get("Thinking", 0),
            "Bored":      current_counts.get("Bored", 0),
            "Distracted": current_counts.get("Distracted", 0),
            "Confused":   current_counts.get("Confused", 0) + current_counts.get("Frustrated", 0)
        },
        "students_list":  students_list,
        "timeline":       class_history[-20:],
        "alerts":         len(confusion_alerts),
        "auto_confusion": auto_confusion_alert,
        "hand_queue":     hand_raise_queue,
        "hand_raised":    hand_raised,
        "session_active": current_session["active"],
        "teacher_pip":    teacher_pip["active"]
    })


@api_bp.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    user = session.get('user')
    if user and user in camera_states:
        camera_states[user][0] = not camera_states[user][0]
        state = "ON" if camera_states[user][0] else "OFF"
        return jsonify({"status": "success", "state": state})
    return jsonify({"status": "error"})


@api_bp.route('/signal_confusion', methods=['POST'])
def signal_confusion():
    confusion_alerts.append(datetime.datetime.now().strftime("%H:%M:%S"))
    return jsonify({"status": "received"})


@api_bp.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    data = request.json
    text = data.get('text', '')
    user = data.get('user', 'Unknown')
    blob = TextBlob(text)
    if blob.sentiment.polarity < -0.3:
        sentiment_logs.append(f"⚠️ {user}: '{text}' (Negative sentiment)")
        return jsonify({"status": "alert_generated"})
    return jsonify({"status": "neutral"})


@api_bp.route('/join_audio_room', methods=['POST'])
def join_audio_room():
    peer_id = request.json.get('peer_id')
    if peer_id and peer_id not in active_peers:
        active_peers.append(peer_id)
    others = [p for p in active_peers if p != peer_id]
    return jsonify({"peers": others})


@api_bp.route('/leave_audio_room', methods=['POST'])
def leave_audio_room():
    peer_id = request.json.get('peer_id')
    if peer_id in active_peers:
        active_peers.remove(peer_id)
    return jsonify({"status": "left"})


@api_bp.route('/raise_hand', methods=['POST'])
def raise_hand():
    user = session.get('user')
    if not user:
        return jsonify({"status": "error"})
    if not any(h['username'] == user for h in hand_raise_queue):
        hand_raise_queue.append({
            "username": user,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        })
    return jsonify({"status": "raised"})


@api_bp.route('/lower_hand', methods=['POST'])
def lower_hand():
    user = request.json.get('user') or session.get('user')
    hand_raise_queue[:] = [h for h in hand_raise_queue if h['username'] != user]
    return jsonify({"status": "lowered"})


@api_bp.route('/dismiss_hand', methods=['POST'])
def dismiss_hand():
    if session.get('role') != 'teacher':
        return jsonify({"status": "error"})
    user = request.json.get('user')
    hand_raise_queue[:] = [h for h in hand_raise_queue if h['username'] != user]
    return jsonify({"status": "dismissed"})


@api_bp.route('/get_heatmap')
def get_heatmap():
    from emotion_logger import get_heatmap_data
    session_id = request.args.get('session_id')
    data = get_heatmap_data(session_id)
    return jsonify(data)
