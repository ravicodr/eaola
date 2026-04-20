import datetime
from flask import Blueprint, request, session, redirect, url_for, render_template

from models import attendance_log, camera_states
from user_db import get_user_by_username, get_user_by_email, create_user
from email_service import send_password_email

auth_bp = Blueprint('auth', __name__)


# ── Splash screen (root redirect) ────────────────────────────────────────────
@auth_bp.route('/')
def root():
    """Redirect root to splash screen."""
    return redirect(url_for('auth.splash'))


@auth_bp.route('/splash')
def splash():
    return render_template('splash.html')


# ── Login ────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u    = request.form['username'].strip()
        p    = request.form['password']
        user = get_user_by_username(u)
        if user and user['password'] == p:
            session['user'] = user['username']
            session['role'] = user['role']
            camera_states[u] = [True]
            attendance_log[u] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if user['role'] == 'teacher':
                return redirect(url_for('teacher.teacher_dashboard'))
            else:
                return redirect(url_for('student.student_dashboard'))
        return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html', error="")


# ── Sign Up ───────────────────────────────────────────────────────────────────
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm  = request.form.get('confirm_password', '').strip()
        email    = request.form.get('email', '').strip()
        role     = request.form.get('role', 'student')

        if not username or not password or not email:
            return render_template('signup.html', error="All fields are required.")
        if len(username) < 3:
            return render_template('signup.html', error="Username must be at least 3 characters.")
        if len(password) < 4:
            return render_template('signup.html', error="Password must be at least 4 characters.")
        if password != confirm:
            return render_template('signup.html', error="Passwords do not match.")
        if '@' not in email or '.' not in email:
            return render_template('signup.html', error="Please enter a valid email address.")

        success, msg = create_user(username, password, email, role)
        if success:
            return render_template('login.html',
                                   error=f"✅ Account created for '{username}'! Please login.")
        return render_template('signup.html', error=msg)

    return render_template('signup.html', error="")


# ── Forgot Password ───────────────────────────────────────────────────────────
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email or '@' not in email:
            return render_template('forgot.html', error="Please enter a valid email address.", success="")
        user = get_user_by_email(email)
        if not user:
            return render_template('forgot.html', error="",
                                   success="If that email is registered, a recovery email has been sent.")
        ok, msg = send_password_email(email, user['username'], user['password'])
        if ok:
            return render_template('forgot.html', error="",
                                   success=f"✅ Password sent to {email}. Check your inbox.")
        return render_template('forgot.html', error=f"⚠️ Could not send email: {msg}", success="")
    return render_template('forgot.html', error="", success="")


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.splash'))
