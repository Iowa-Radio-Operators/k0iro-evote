from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_db

auth = Blueprint('auth', __name__)


# -------------------------------------------------
# Registration (Call Sign + Email)
# -------------------------------------------------
# Add this route to your app/auth.py to redirect old registration to apply

@auth.route('/register')
def register_redirect():
    """Redirect old register route to apply page"""
    return redirect(url_for('member.apply'))

# -------------------------------------------------
# Login (Call Sign Based)
# -------------------------------------------------
@auth.route('/login')
def login():
    """Redirect to SSO login"""
    from .client_auth import redirect_to_login
    return redirect_to_login()


# -------------------------------------------------
# Logout
# -------------------------------------------------
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))