from flask import Flask
from .database import init_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Initialize database
    init_db()

    # -----------------------------
    # Import and register blueprints
    # -----------------------------
    from .routes import main          # <-- main blueprint lives in routes.py
    from .auth import auth
    from .voting import voting
    from .routes import admin_votes   # <-- admin_votes also lives in routes.py

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(voting)
    app.register_blueprint(admin_votes)

    return app