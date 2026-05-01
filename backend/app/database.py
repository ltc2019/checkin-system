import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "checkin.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nickname TEXT NOT NULL DEFAULT '',
            avatar TEXT DEFAULT '',
            role TEXT NOT NULL DEFAULT 'member',
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            checkin_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            notes TEXT DEFAULT '',
            audio_url TEXT DEFAULT '',
            video_url TEXT DEFAULT '',
            photo_urls TEXT DEFAULT '[]',
            steps INTEGER DEFAULT 0,
            reading_duration INTEGER DEFAULT 0,
            sport_type TEXT DEFAULT '',
            calories INTEGER DEFAULT 0,
            book_id INTEGER DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT DEFAULT '',
            cover_url TEXT DEFAULT '',
            total_pages INTEGER DEFAULT 0,
            current_page INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'reading',
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL UNIQUE,
            start_time TEXT DEFAULT '05:30',
            end_time TEXT DEFAULT '08:30',
            min_steps INTEGER DEFAULT 0,
            required_media TEXT DEFAULT '',
            points INTEGER DEFAULT 1,
            enabled INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            total INTEGER DEFAULT 0,
            weekly INTEGER DEFAULT 0,
            monthly INTEGER DEFAULT 0,
            yearly INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM rules")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO rules (type, start_time, end_time, required_media, points) VALUES (?, ?, ?, ?, ?)",
            [
                ("early", "05:30", "08:30", "", 2),
                ("reading", "00:00", "23:59", "audio", 3),
                ("sport", "00:00", "23:59", "photo", 3),
            ]
        )

    cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash, nickname, role) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, "管理员", "admin")
        )

    conn.commit()
    conn.close()