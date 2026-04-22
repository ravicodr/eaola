import time
import numpy as np
import cv2
from flask import Blueprint, Response, session, stream_with_context

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("[WARNING] DeepFace not available — emotion detection disabled, defaulting to 'Thinking'")

from camera import global_camera
from models import active_student_sessions, camera_states, current_session, teacher_pip
from config import EMOTION_MAP
from emotion_logger import log_emotion

video_bp = Blueprint('video', __name__)


def generate_feed(user_role, camera_active, username="unknown"):
    """
    Stream video frames. For students:
    - Sessions keyed by USERNAME (not UUID) → only 1 entry per student
    - log_emotion only called when emotion CHANGES → no duplicate DB entries
    """

    # ── Register student by USERNAME (not random UUID) ────────────────────
    if user_role == 'student':
        if username not in active_student_sessions:
            active_student_sessions[username] = {
                'status': 'Thinking',
                'last_seen': time.time(),
                'last_logged': None   # track last logged emotion to avoid duplicates
            }

    frame_counter = 0
    try:
        while True:
            # ── Camera OFF ────────────────────────────────────────────────
            if not camera_active[0]:
                blank = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(blank, "CAMERA OFF", (200, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
                if user_role == 'student' and username in active_student_sessions:
                    active_student_sessions[username]['status'] = "Camera Off"
                ret, buffer = cv2.imencode('.jpg', blank)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.5)
                continue

            frame = global_camera.get_frame()

            # ── Student: emotion detection every 30 frames ────────────────
            if user_role == 'student':
                frame_counter += 1
                if frame_counter % 30 == 0:
                    try:
                        if DEEPFACE_AVAILABLE:
                            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                            objs  = DeepFace.analyze(small, actions=['emotion'],
                                                     enforce_detection=True, silent=True)
                            if objs:
                                raw   = objs[0]['dominant_emotion']
                                label = EMOTION_MAP.get(raw, "Thinking")
                        else:
                            label = "Thinking"
                    except Exception:
                        label = "Distracted"

                    # Update current status
                    active_student_sessions[username]['status']    = label
                    active_student_sessions[username]['last_seen'] = time.time()

                    # ── Only log to DB when emotion CHANGES ───────────────
                    last_logged = active_student_sessions[username].get('last_logged')
                    if label != last_logged:
                        sid = current_session["id"] if current_session["active"] else None
                        log_emotion(username, label, session_id=sid)
                        active_student_sessions[username]['last_logged'] = label

                # Draw status on frame
                my_status = active_student_sessions.get(username, {}).get('status', "Thinking")
                color = (0, 255, 0) if my_status in ["Engaged", "Thinking"] else (0, 0, 255)
                cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 0), -1)
                cv2.putText(frame, f"Status: {my_status}", (10, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # ── Teacher: show active student count ────────────────────────
            else:
                count = len([s for s in active_student_sessions.values()
                             if s['status'] != "Camera Off"])
                cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 0), -1)
                cv2.putText(frame, f"Active Students: {count}", (10, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.04)

    except GeneratorExit:
        # ── Clean up only this student's session ──────────────────────────
        if user_role == 'student' and username in active_student_sessions:
            del active_student_sessions[username]


@video_bp.route('/video_feed')
def video_feed():
    role = session.get('role', 'guest')
    user = session.get('user', 'guest')
    if user not in camera_states:
        camera_states[user] = [True]
    return Response(
        stream_with_context(generate_feed(role, camera_states[user], username=user)),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


def generate_teacher_frames():
    """
    Lightweight MJPEG stream of the teacher's camera for the student PiP.
    No emotion detection — just raw frames at a gentle rate.
    """
    while True:
        frame = global_camera.get_frame()
        # Stamp a small "TEACHER LIVE" label so students know it's the teacher
        cv2.rectangle(frame, (0, 0), (640, 36), (21, 101, 192), -1)
        cv2.putText(frame, "  TEACHER  LIVE", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.05)   # ~20 fps is plenty for PiP


@video_bp.route('/teacher_feed')
def teacher_feed():
    """Serve the teacher's camera stream to students as a PiP feed."""
    # Only authenticated users may access this
    if not session.get('user'):
        return Response("Unauthorized", status=403)
    return Response(
        stream_with_context(generate_teacher_frames()),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
