import random
import string
from datetime import datetime
from .database import get_connection

def get_movies():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM movies ORDER BY title").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_shows(movie_id=None):
    conn = get_connection()
    if movie_id:
        rows = conn.execute("""
            SELECT s.*, m.title AS movie_title
            FROM shows s JOIN movies m ON m.id=s.movie_id
            WHERE movie_id=? ORDER BY show_date, show_time
        """, (movie_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT s.*, m.title AS movie_title
            FROM shows s JOIN movies m ON m.id=s.movie_id
            ORDER BY show_date, show_time
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_show(show_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT s.*, m.title AS movie_title
        FROM shows s JOIN movies m ON m.id=s.movie_id WHERE s.id=?
    """, (show_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_booked_seats(show_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT bs.seat_code FROM booking_seats bs
        JOIN bookings b ON b.id=bs.booking_id
        WHERE bs.show_id=? AND b.status='CONFIRMED'
    """, (show_id,)).fetchall()
    conn.close()
    return {r["seat_code"] for r in rows}

def _code():
    conn = get_connection()
    while True:
        code = "CB-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        if not conn.execute("SELECT 1 FROM bookings WHERE booking_code=?", (code,)).fetchone():
            conn.close()
            return code

def create_booking(show_id, seats, name, email, phone, payment):
    conn = get_connection()
    try:
        show = conn.execute("SELECT price FROM shows WHERE id=?", (show_id,)).fetchone()
        if not show:
            raise ValueError("Show not found.")
        seats = sorted(set(seats))
        placeholders = ",".join("?" for _ in seats)
        if conn.execute(f"SELECT seat_code FROM booking_seats WHERE show_id=? AND seat_code IN ({placeholders})",
                        [show_id, *seats]).fetchone():
            raise ValueError("One or more selected seats were just booked. Please refresh and select again.")

        code = _code()
        cur = conn.execute("""
            INSERT INTO bookings(booking_code,show_id,customer_name,email,phone,payment_method,total_amount,status,created_at)
            VALUES(?,?,?,?,?,?,?,?,?)
        """, (code, show_id, name, email, phone, payment, len(seats)*show["price"], "CONFIRMED",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        booking_id = cur.lastrowid
        conn.executemany("INSERT INTO booking_seats(booking_id,show_id,seat_code) VALUES(?,?,?)",
                         [(booking_id, show_id, s) for s in seats])
        conn.commit()
        return code
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_bookings():
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, s.show_date, s.show_time, s.screen_name, m.title AS movie_title,
               GROUP_CONCAT(bs.seat_code, ', ') AS seats
        FROM bookings b
        JOIN shows s ON s.id=b.show_id
        JOIN movies m ON m.id=s.movie_id
        LEFT JOIN booking_seats bs ON bs.booking_id=b.id
        GROUP BY b.id ORDER BY b.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def cancel_booking(booking_id):
    conn = get_connection()
    conn.execute("UPDATE bookings SET status='CANCELLED' WHERE id=? AND status='CONFIRMED'", (booking_id,))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_connection()
    bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    confirmed = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='CONFIRMED'").fetchone()[0]
    seats_sold = conn.execute("""
        SELECT COUNT(*) FROM booking_seats bs JOIN bookings b ON b.id=bs.booking_id
        WHERE b.status='CONFIRMED'
    """).fetchone()[0]
    revenue = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM bookings WHERE status='CONFIRMED'").fetchone()[0]
    daily = conn.execute("""
        SELECT substr(created_at,1,10) AS date,
               COUNT(*) AS bookings,
               COALESCE(SUM(total_amount),0) AS revenue
        FROM bookings WHERE status='CONFIRMED'
        GROUP BY substr(created_at,1,10) ORDER BY date
    """).fetchall()
    conn.close()
    return {"bookings": bookings, "confirmed": confirmed, "seats_sold": seats_sold,
            "revenue": revenue, "daily": [dict(x) for x in daily]}
