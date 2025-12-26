from flask import Flask
from .database import init_db
from dotenv import load_dotenv

def create_app():
    load_dotenv()  # Load .env file

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')


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