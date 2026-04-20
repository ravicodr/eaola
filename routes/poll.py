from flask import Blueprint, request, session, redirect, render_template, jsonify

from models import poll_state

poll_bp = Blueprint('poll', __name__)


@poll_bp.route('/create_poll')
def create_poll():
    if session.get('role') != 'teacher':
        return redirect('/')
    return render_template('poll_form.html')


@poll_bp.route('/launch_poll', methods=['POST'])
def launch_poll():
    if session.get('role') != 'teacher':
        return redirect('/')
    q = request.form['question']
    opts = []
    for key in ['opt1', 'opt2', 'opt3', 'opt4']:
        val = request.form.get(key, '').strip()
        if val:
            opts.append(val)

    poll_state['question'] = q
    poll_state['options'] = {opt: 0 for opt in opts}
    poll_state['active'] = True
    poll_state['voted_users'] = []
    return redirect('/teacher')


@poll_bp.route('/close_poll')
def close_poll():
    if session.get('role') != 'teacher':
        return redirect('/')
    poll_state['active'] = False
    return redirect('/teacher')


@poll_bp.route('/submit_vote', methods=['POST'])
def submit_vote():
    data = request.json
    user = session.get('user')
    choice = data.get('choice')

    if not poll_state['active']:
        return jsonify({"status": "closed"})
    if user in poll_state['voted_users']:
        return jsonify({"status": "already_voted"})
    if choice in poll_state['options']:
        poll_state['options'][choice] += 1
        poll_state['voted_users'].append(user)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})
