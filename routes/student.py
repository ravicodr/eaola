from flask import Blueprint, session, redirect, render_template

student_bp = Blueprint('student', __name__)


@student_bp.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/')
    return render_template('student.html')
