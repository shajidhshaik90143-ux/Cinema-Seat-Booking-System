import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cinema.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        duration INTEGER NOT NULL,
        language TEXT NOT NULL,
        description TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS shows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        show_date TEXT NOT NULL,
        show_time TEXT NOT NULL,
        screen_name TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_code TEXT UNIQUE NOT NULL,
        show_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'CONFIRMED',
        created_at TEXT NOT NULL,
        FOREIGN KEY(show_id) REFERENCES shows(id)
    );

    CREATE TABLE IF NOT EXISTS booking_seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        show_id INTEGER NOT NULL,
        seat_code TEXT NOT NULL,
        FOREIGN KEY(booking_id) REFERENCES bookings(id),
        FOREIGN KEY(show_id) REFERENCES shows(id),
        UNIQUE(show_id, seat_code)
    );
    """)
    conn.commit()
    conn.close()

def seed_data():
    conn = get_connection()
    if conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0] == 0:
        movies = [
            ("Avengers: Endgame", "Action / Sci-Fi", 181, "English", "Earth's heroes assemble for a final battle to restore what was lost."),
            ("Interstellar", "Sci-Fi / Drama", 169, "English", "A team travels through a wormhole searching for a future for humanity."),
            ("RRR", "Action / Drama", 182, "Telugu", "Two legendary revolutionaries form an unexpected friendship."),
            ("Inception", "Sci-Fi / Thriller", 148, "English", "A skilled extractor enters dreams to plant an idea."),
        ]
        conn.executemany("INSERT INTO movies(title,genre,duration,language,description) VALUES(?,?,?,?,?)", movies)

    if conn.execute("SELECT COUNT(*) FROM shows").fetchone()[0] == 0:
        movie_ids = {r["title"]: r["id"] for r in conn.execute("SELECT id,title FROM movies")}
        shows = [
            (movie_ids["Avengers: Endgame"], "2026-10-01", "10:00 AM", "Screen 1", 220),
            (movie_ids["Avengers: Endgame"], "2026-10-01", "02:00 PM", "Screen 1", 250),
            (movie_ids["Avengers: Endgame"], "2026-10-01", "06:30 PM", "Screen 2", 280),
            (movie_ids["Interstellar"], "2026-10-01", "11:00 AM", "Screen 2", 200),
            (movie_ids["Interstellar"], "2026-10-01", "05:00 PM", "Screen 3", 240),
            (movie_ids["RRR"], "2026-10-02", "10:30 AM", "Screen 3", 180),
            (movie_ids["RRR"], "2026-10-02", "07:00 PM", "Screen 1", 240),
            (movie_ids["Inception"], "2026-10-02", "03:00 PM", "Screen 2", 210),
        ]
        conn.executemany("INSERT INTO shows(movie_id,show_date,show_time,screen_name,price) VALUES(?,?,?,?,?)", shows)
    conn.commit()
    conn.close()
