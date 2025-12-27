from flask import Flask
from dotenv import load_dotenv
import os
from .database import init_db

def create_app():
    load_dotenv()  # Load .env file

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')

    app.config['PERMANENT_SESSION_LIFETIME'] = 14400  # 4 hours

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