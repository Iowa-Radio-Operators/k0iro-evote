from flask import Blueprint, render_template, request, redirect, url_for
from .auth_helpers import admin_required
from .database import get_db

admin = Blueprint('admin', __name__)

# -------------------------------------------------
# Admin Dashboard
# -------------------------------------------------
@admin.route('/admin')
@admin_required
def admin_home():
    return render_template('admin_home.html', title="Admin Dashboard")


# -------------------------------------------------
# Create a New Vote
# -------------------------------------------------
@admin.route('/admin/create_vote', methods=['GET', 'POST'])
@admin_required
def create_vote():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            return render_template(
                'admin_create_vote.html',
                title="Create Vote",
                error="A vote must have a title"
            )

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO votes (title, description, is_active) VALUES (?, ?, 1)",
            (title, description)
        )
        conn.commit()

        vote_id = cursor.lastrowid

        # Redirect to add options for this vote
        return redirect(url_for('admin.add_options', vote_id=vote_id))

    return render_template('admin_create_vote.html', title="Create Vote")


# -------------------------------------------------
# Add Options to a Vote
# -------------------------------------------------
@admin.route('/admin/add_options/<int:vote_id>', methods=['GET', 'POST'])
@admin_required
def add_options(vote_id):
    conn = get_db()
    cursor = conn.cursor()

    # Fetch vote info
    cursor.execute("SELECT * FROM votes WHERE id = ?", (vote_id,))
    vote = cursor.fetchone()

    if not vote:
        return "Vote not found", 404

    # Handle new option submission
    if request.method == 'POST':
        option_text = request.form.get('option_text', '').strip()

        if option_text:
            cursor.execute(
                "INSERT INTO vote_options (vote_id, option_text) VALUES (?, ?)",
                (vote_id, option_text)
            )
            conn.commit()

        return redirect(url_for('admin.add_options', vote_id=vote_id))

    # Fetch existing options
    cursor.execute("SELECT * FROM vote_options WHERE vote_id = ?", (vote_id,))
    options = cursor.fetchall()

    return render_template(
        'admin_add_options.html',
        title="Add Options",
        vote=vote,
        options=options
    )