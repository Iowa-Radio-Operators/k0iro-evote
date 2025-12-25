from flask import Blueprint, render_template, request, redirect, url_for, session
from .database import get_db
from .auth_helpers import login_required

voting = Blueprint('voting', __name__)


# -------------------------------------------------
# Member Voting Page
# -------------------------------------------------
@voting.route('/vote', methods=['GET'])
@login_required
def vote():
    conn = get_db()
    cursor = conn.cursor()

    # Get active vote
    cursor.execute("SELECT * FROM votes WHERE is_active = 1 LIMIT 1")
    vote = cursor.fetchone()

    if not vote:
        return render_template('vote_none.html', title="Vote")

    # Get options for this vote
    cursor.execute("SELECT * FROM vote_options WHERE vote_id = ?", (vote['id'],))
    options = cursor.fetchall()

    # Check if user already voted
    user_id = session.get('user_id')
    cursor.execute(
        "SELECT * FROM ballots WHERE vote_id = ? AND user_id = ?",
        (vote['id'], user_id)
    )
    existing_vote = cursor.fetchone()

    return render_template(
        'vote.html',
        title="Vote",
        vote=vote,
        options=options,
        existing_vote=existing_vote
    )


# -------------------------------------------------
# Submit Vote
# -------------------------------------------------
@voting.route('/vote/submit', methods=['POST'])
@login_required
def submit_vote():
    option_id = request.form.get('option_id')

    if not option_id:
        return "Invalid vote submission", 400

    conn = get_db()
    cursor = conn.cursor()

    # Get option info
    cursor.execute("SELECT * FROM vote_options WHERE id = ?", (option_id,))
    option = cursor.fetchone()

    if not option:
        return "Invalid option", 400

    vote_id = option['vote_id']
    user_id = session.get('user_id')
    callsign = session.get('user')

    # Prevent double voting
    cursor.execute(
        "SELECT * FROM ballots WHERE vote_id = ? AND user_id = ?",
        (vote_id, user_id)
    )
    existing = cursor.fetchone()

    if existing:
        return redirect(url_for('voting.vote'))

    # Record the vote
    cursor.execute(
        "INSERT INTO ballots (vote_id, option_id, user_id, callsign) VALUES (?, ?, ?, ?)",
        (vote_id, option_id, user_id, callsign)
    )
    conn.commit()

    return redirect(url_for('voting.vote_confirmed', option_id=option_id))


# -------------------------------------------------
# Confirmation Page
# -------------------------------------------------
@voting.route('/vote/confirmed')
@login_required
def vote_confirmed():
    option_id = request.args.get('option_id')

    conn = get_db()
    cursor = conn.cursor()

    # Get option info
    cursor.execute("SELECT * FROM vote_options WHERE id = ?", (option_id,))
    option = cursor.fetchone()

    if not option:
        return "Invalid confirmation", 400

    # Get vote info
    cursor.execute("SELECT * FROM votes WHERE id = ?", (option['vote_id'],))
    vote = cursor.fetchone()

    return render_template(
        'vote_confirmed.html',
        title="Vote Submitted",
        vote=vote,
        option=option
    )