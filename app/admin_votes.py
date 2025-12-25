from flask import Blueprint, render_template, redirect, url_for
from .database import get_db
from .auth_helpers import admin_required

admin_votes = Blueprint('admin_votes', __name__)


# -------------------------------------------------
# Manage Votes Page
# -------------------------------------------------
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


# -------------------------------------------------
# Activate Vote
# -------------------------------------------------
@admin_votes.route('/admin/votes/<int:vote_id>/activate')
@admin_required
def activate_vote(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    # Deactivate all votes (if you want only one active at a time)
    cursor.execute("UPDATE votes SET is_active = 0")

    # Activate selected vote
    cursor.execute("UPDATE votes SET is_active = 1 WHERE id = ?", (vote_id,))
    conn.commit()

    return redirect(url_for('admin_votes.manage_votes'))


# -------------------------------------------------
# Deactivate Vote
# -------------------------------------------------
@admin_votes.route('/admin/votes/<int:vote_id>/deactivate')
@admin_required
def deactivate_vote(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE votes SET is_active = 0 WHERE id = ?", (vote_id,))
    conn.commit()

    return redirect(url_for('admin_votes.manage_votes'))



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

