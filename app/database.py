import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "evote.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            callsign TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        );
    """)

    # Votes table (one active vote at a time)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            is_released INTEGER DEFAULT 0
        );
    """)

    # Vote options
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vote_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vote_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            FOREIGN KEY (vote_id) REFERENCES votes(id)
        );
    """)

    # Ballots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ballots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vote_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (vote_id) REFERENCES votes(id),
            FOREIGN KEY (option_id) REFERENCES vote_options(id)
        );
    """)

    conn.commit()
    conn.close()