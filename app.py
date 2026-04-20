import os
from flask import Flask

from config import SECRET_KEY
from background import start_background_workers
from emotion_logger import init_db
from user_db import init_users_table

from routes.auth import auth_bp
from routes.video import video_bp
from routes.api import api_bp
from routes.poll import poll_bp
from routes.teacher import teacher_bp
from routes.student import student_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", SECRET_KEY)

app.register_blueprint(auth_bp)
app.register_blueprint(video_bp)
app.register_blueprint(api_bp)
app.register_blueprint(poll_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

init_db()
init_users_table()
start_background_workers()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("=" * 55)
    print(f"  EAOLA - Starting on http://localhost:{port}")
    print(f"  Login: teacher/123  or  student/123")
    print("=" * 55)
    app.run(host='0.0.0.0', port=port, debug=False,
            use_reloader=False, threaded=True)
