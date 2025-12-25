from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db

auth = Blueprint('auth', __name__)


# -------------------------------------------------
# Registration (Call Sign Based)
# -------------------------------------------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        callsign = request.form.get('callsign', '').strip().upper()
        password = request.form.get('password', '')

        if not callsign or not password:
            error = "Call sign and password are required"
            return render_template('register.html', title="Register", error=error)

        conn = get_db()
        cursor = conn.cursor()

        # Check if call sign already exists
        cursor.execute("SELECT id FROM users WHERE callsign = ?", (callsign,))
        existing = cursor.fetchone()

        if existing:
            error = "That call sign is already registered"
            return render_template('register.html', title="Register", error=error)

        # Create user with hashed password
        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (callsign, password_hash, is_admin) VALUES (?, ?, 0)",
            (callsign, password_hash)
        )
        conn.commit()

        # NEW: get the new user ID
        new_user_id = cursor.lastrowid

        # Auto-login after registration
        session['user'] = callsign
        session['user_id'] = new_user_id          # <-- ADD THIS
        session['user_is_admin'] = False

        return redirect(url_for('main.index'))

    return render_template('register.html', title="Register", error=error)


# -------------------------------------------------
# Login (Call Sign Based)
# -------------------------------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        # NOTE: your form uses "username", so this is correct for your current HTML
        callsign = request.form.get('username', '').strip().upper()
        password = request.form.get('password', '')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE callsign = ?", (callsign,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user['callsign']
            session['user_id'] = user['id']              # <-- ADD THIS
            session['user_is_admin'] = bool(user['is_admin'])
            return redirect(url_for('main.index'))
        else:
            error = "Invalid call sign or password"

    return render_template('login.html', title="Login", error=error)


# -------------------------------------------------
# Logout
# -------------------------------------------------
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))