import io
import csv
import uuid
import datetime
from flask import Blueprint, session, redirect, render_template, Response, jsonify, request, url_for

from models import class_history, confusion_alerts, attendance_log, current_session, meeting_state, teacher_pip
from emotion_logger import (get_all_logs, get_summary, get_all_students,
                             get_heatmap_data, start_session, end_session,
                             get_all_sessions, get_session_detail)

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect('/')
    return render_template('teacher.html')


# ─── SESSION CONTROL ─────────────────────────────────────────────────────────

@teacher_bp.route('/start_session', methods=['POST'])
def start_class_session():
    if session.get('role') != 'teacher':
        return redirect('/')
    if not current_session["active"]:
        sid = start_session()
        current_session["id"]         = sid
        current_session["active"]     = True
        current_session["start_time"] = datetime.datetime.now().strftime("%H:%M:%S")
    return jsonify({"status": "started", "session_id": current_session["id"]})


@teacher_bp.route('/end_class')
def end_class():
    if session.get('role') != 'teacher':
        return redirect('/')

    total_time = len(class_history) * 5
    avg_score  = (sum(d['score'] for d in class_history) / len(class_history)
                  if class_history else 0)
    highlights = [d for d in class_history if d['vibe'] in ("Bored", "Distracted")]

    # Close the active session in DB
    if current_session["active"] and current_session["id"]:
        end_session(current_session["id"], int(avg_score), len(confusion_alerts))
        current_session["active"] = False

    return render_template(
        'report.html',
        duration=f"{total_time // 60} mins",
        avg_score=int(avg_score),
        alerts=len(confusion_alerts),
        highlights=highlights,
        session_id=current_session["id"]
    )


# ─── SESSIONS LIST ───────────────────────────────────────────────────────────

@teacher_bp.route('/sessions')
def sessions_list():
    if session.get('role') != 'teacher':
        return redirect('/')
    sessions_data = get_all_sessions()
    return render_template('sessions.html', sessions=sessions_data)


@teacher_bp.route('/session/<int:session_id>')
def session_detail(session_id):
    if session.get('role') != 'teacher':
        return redirect('/')
    sess, emotion_breakdown, students = get_session_detail(session_id)
    heatmap = get_heatmap_data(session_id)
    return render_template('session_detail.html',
                           sess=sess,
                           emotion_breakdown=emotion_breakdown,
                           students=students,
                           heatmap=heatmap)


# ─── EMOTION HISTORY ─────────────────────────────────────────────────────────

@teacher_bp.route('/emotion_history')
def emotion_history():
    if session.get('role') != 'teacher':
        return redirect('/')
    logs     = get_all_logs()
    summary  = get_summary()
    students = get_all_students()
    return render_template('emotion_history.html', logs=logs,
                           summary=summary, students=students)


# ─── DOWNLOADS ───────────────────────────────────────────────────────────────

@teacher_bp.route('/download_attendance')
def download_attendance():
    if session.get('role') != 'teacher':
        return redirect('/')
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Username', 'Login Time', 'Status'])
    for user, time_str in attendance_log.items():
        cw.writerow([user, time_str, 'Present'])
    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=attendance.csv"})


@teacher_bp.route('/download_emotion_logs')
def download_emotion_logs():
    if session.get('role') != 'teacher':
        return redirect('/')
    logs = get_all_logs()
    si   = io.StringIO()
    cw   = csv.writer(si)
    cw.writerow(['Username', 'Emotion', 'Time', 'Date'])
    for row in logs:
        cw.writerow(row)
    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=emotion_logs.csv"})


# ─── MEETING LINK ─────────────────────────────────────────────────────────────

@teacher_bp.route('/generate_meeting_link', methods=['POST'])
def generate_meeting_link():
    """Generate a unique meeting room link for students to join."""
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403
    room_id = uuid.uuid4().hex[:10]
    meeting_state["active"]     = True
    meeting_state["room_id"]    = room_id
    meeting_state["created_at"] = datetime.datetime.now().strftime("%H:%M:%S")
    return jsonify({
        "status":     "created",
        "room_id":    room_id,
        "created_at": meeting_state["created_at"]
    })


@teacher_bp.route('/revoke_meeting_link', methods=['POST'])
def revoke_meeting_link():
    """Revoke (deactivate) the current meeting link."""
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403
    meeting_state["active"]     = False
    meeting_state["room_id"]    = None
    meeting_state["created_at"] = None
    return jsonify({"status": "revoked"})


@teacher_bp.route('/get_meeting_link')
def get_meeting_link():
    """Return the current meeting link state (for polling from the UI)."""
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(meeting_state)


@teacher_bp.route('/join/<room_id>')
def join_meeting(room_id):
    """Handle student joining via a meeting link."""
    if meeting_state["active"] and meeting_state["room_id"] == room_id:
        # If already logged in as a student, send straight to dashboard
        if session.get('role') == 'student':
            return redirect(url_for('student.student_dashboard'))
        # Otherwise send to login page
        return redirect(url_for('auth.login'))
    # Invalid or expired link — redirect to splash
    return redirect(url_for('auth.splash'))


# ─── TEACHER PIP ──────────────────────────────────────────────────────────────

@teacher_bp.route('/toggle_teacher_pip', methods=['POST'])
def toggle_teacher_pip():
    """Toggle whether the teacher's live PiP feed is visible to students."""
    if session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403
    teacher_pip["active"] = not teacher_pip["active"]
    return jsonify({"active": teacher_pip["active"]})
