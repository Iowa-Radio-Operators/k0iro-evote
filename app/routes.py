from flask import Blueprint, render_template, redirect, url_for, request
from .database import get_db
from .auth_helpers import admin_required

# -------------------------------------------------
# Main Site Blueprint
# -------------------------------------------------
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', title="Home")


# -------------------------------------------------
# Admin Vote Management Blueprint
# -------------------------------------------------
admin_votes = Blueprint('admin_votes', __name__)


# -------------------------
# Admin Dashboard
# -------------------------
@admin_votes.route('/admin')
@admin_required
def admin_home():
    return render_template('admin_home.html', title="Admin Dashboard")


# -------------------------
# Create New Vote (Form)
# -------------------------
@admin_votes.route('/admin/votes/create')
@admin_required
def create_vote_form():
    return render_template('admin_create_vote.html', title="Create New Vote")


# -------------------------
# Create New Vote (Submit)
# -------------------------
@admin_votes.route('/admin/votes/create', methods=['POST'])
@admin_required
def create_vote():
    title = request.form.get('title', '').strip()

    if not title:
        return render_template(
            'admin_create_vote.html',
            title="Create New Vote",
            error="Title is required."
        )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO votes (title, is_active, is_released) VALUES (?, 0, 0)", (title,))
    conn.commit()

    new_vote_id = cursor.lastrowid

    return redirect(url_for('admin_votes.edit_options', vote_id=new_vote_id))


# -------------------------
# Manage Votes
# -------------------------
@admin_votes.route('/admin/votes')
@admin_required
def manage_votes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM votes ORDER BY id DESC")
    votes = cursor.fetchall()

    return render_template(
        'admin_votes.html',
        title="Manage Votes",
        votes=votes
    )


# -------------------------
# Activate / Deactivate Vote
# -------------------------
@admin_votes.route('/admin/votes/<int:vote_id>/activate')
@admin_required
def activate_vote(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE votes SET is_active = 0")
    cursor.execute("UPDATE votes SET is_active = 1 WHERE id = ?", (vote_id,))
    conn.commit()

    return redirect(url_for('admin_votes.manage_votes'))


@admin_votes.route('/admin/votes/<int:vote_id>/deactivate')
@admin_required
def deactivate_vote(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE votes SET is_active = 0 WHERE id = ?", (vote_id,))
    conn.commit()

    return redirect(url_for('admin_votes.manage_votes'))


# -------------------------
# Edit Options for a Vote
# -------------------------
@admin_votes.route('/admin/votes/<int:vote_id>/options')
@admin_required
def edit_options(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM votes WHERE id = ?", (vote_id,))
    vote = cursor.fetchone()

    if not vote:
        return "Vote not found", 404

    cursor.execute("SELECT * FROM vote_options WHERE vote_id = ?", (vote_id,))
    options = cursor.fetchall()

    return render_template(
        'admin_edit_options.html',
        title=f"Edit Options for {vote['title']}",
        vote=vote,
        options=options
    )


# -------------------------
# Add Option
# -------------------------
@admin_votes.route('/admin/votes/<int:vote_id>/options/add', methods=['POST'])
@admin_required
def add_option(vote_id):
    label = request.form.get('label', '').strip()

    if not label:
        return redirect(url_for('admin_votes.edit_options', vote_id=vote_id))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO vote_options (vote_id, label) VALUES (?, ?)",
        (vote_id, label)
    )
    conn.commit()

    return redirect(url_for('admin_votes.edit_options', vote_id=vote_id))


# -------------------------
# Delete Option
# -------------------------
@admin_votes.route('/admin/options/<int:option_id>/delete')
@admin_required
def delete_option(option_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT vote_id FROM vote_options WHERE id = ?", (option_id,))
    row = cursor.fetchone()

    if not row:
        return "Option not found", 404

    vote_id = row['vote_id']

    cursor.execute("DELETE FROM vote_options WHERE id = ?", (option_id,))
    conn.commit()

    return redirect(url_for('admin_votes.edit_options', vote_id=vote_id))


# -------------------------------------------------
# Public Results
# -------------------------------------------------
@main.route('/results')
def public_results():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM votes WHERE is_released = 1 ORDER BY id DESC")
    votes = cursor.fetchall()

    return render_template('public_results.html', votes=votes, title="Results")


@main.route('/results/<int:vote_id>')
def public_results_detail(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM votes WHERE id = ? AND is_released = 1", (vote_id,))
    vote = cursor.fetchone()

    if not vote:
        return "Results not available", 404

    cursor.execute("""
        SELECT vo.label, COUNT(b.id) AS count
        FROM vote_options vo
        LEFT JOIN ballots b ON b.option_id = vo.id
        WHERE vo.vote_id = ?
        GROUP BY vo.id
        ORDER BY count DESC
    """, (vote_id,))
    options = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM ballots WHERE vote_id = ?", (vote_id,))
    total_votes = cursor.fetchone()['total']

    return render_template(
        'public_results_detail.html',
        vote=vote,
        options=options,
        total_votes=total_votes,
        title=f"Results for {vote['title']}"
    )


# -------------------------------------------------
# Admin Results Control
# -------------------------------------------------
@admin_votes.route('/admin/results')
@admin_required
def admin_results():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM votes ORDER BY id DESC")
    votes = cursor.fetchall()

    return render_template('admin_results.html', votes=votes, title="Admin Results Control")


@admin_votes.route('/admin/results/<int:vote_id>/release')
@admin_required
def release_results(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE votes SET is_released = 1 WHERE id = ?", (vote_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_results'))


@admin_votes.route('/admin/results/<int:vote_id>/unrelease')
@admin_required
def unrelease_results(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE votes SET is_released = 0 WHERE id = ?", (vote_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_results'))


# -------------------------------------------------
# User Management (Admin Only)
# -------------------------------------------------
@admin_votes.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, callsign, email, is_admin, is_active FROM users ORDER BY callsign ASC")
    users = cursor.fetchall()

    return render_template('admin_users.html', users=users, title="User Management")


@admin_votes.route('/admin/users/<int:user_id>/activate')
@admin_required
def activate_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_users'))


@admin_votes.route('/admin/users/<int:user_id>/deactivate')
@admin_required
def deactivate_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_users'))


@admin_votes.route('/admin/users/<int:user_id>/promote')
@admin_required
def promote_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_users'))


@admin_votes.route('/admin/users/<int:user_id>/demote')
@admin_required
def demote_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET is_admin = 0 WHERE id = ?", (user_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_users'))


@admin_votes.route('/admin/users/<int:user_id>/delete')
@admin_required
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

    return redirect(url_for('admin_votes.admin_users'))

@admin_votes.route('/admin/votes/<int:vote_id>/ballots')
@admin_required
def view_ballots(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    # Get vote info
    cursor.execute("SELECT * FROM votes WHERE id = ?", (vote_id,))
    vote = cursor.fetchone()
    if not vote:
        return "Vote not found", 404

    # Get ballots with user + option labels
    cursor.execute("""
        SELECT b.id AS ballot_id, u.callsign, vo.label
        FROM ballots b
        JOIN users u ON b.user_id = u.id
        JOIN vote_options vo ON b.option_id = vo.id
        WHERE b.vote_id = ?
        ORDER BY u.callsign ASC
    """, (vote_id,))
    ballots = cursor.fetchall()

    return render_template(
        'admin_ballots.html',
        vote=vote,
        ballots=ballots,
        title=f"Ballots for {vote['title']}"
    )

@admin_votes.route('/admin/ballots/<int:ballot_id>/delete')
@admin_required
def delete_ballot(ballot_id):
    conn = get_db()
    cursor = conn.cursor()

    # Get vote_id before deleting so we can redirect back
    cursor.execute("SELECT vote_id FROM ballots WHERE id = ?", (ballot_id,))
    row = cursor.fetchone()

    if not row:
        return "Ballot not found", 404

    vote_id = row['vote_id']

    cursor.execute("DELETE FROM ballots WHERE id = ?", (ballot_id,))
    conn.commit()

    return redirect(url_for('admin_votes.view_ballots', vote_id=vote_id))