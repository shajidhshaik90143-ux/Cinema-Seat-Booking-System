import streamlit as st
from src.database import init_db, seed_data
from src.services import (
    get_movies, get_shows, get_show, get_booked_seats, create_booking,
    get_bookings, cancel_booking, get_dashboard_stats
)
from src.ui import render_seat_map, poster_placeholder

st.set_page_config(page_title="CineBook | Cinema Seat Booking", page_icon="🎬", layout="wide")

init_db()
seed_data()

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "selected_show" not in st.session_state:
    st.session_state.selected_show = None
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = []

st.markdown("""
<style>
.main {background:#0b1020;}
.block-container {padding-top:1.5rem; padding-bottom:3rem;}
.hero {padding:28px; border-radius:22px; background:linear-gradient(135deg,#161b33,#252a52);
        border:1px solid #353b68; margin-bottom:20px;}
.hero h1 {font-size:42px; margin:0;}
.card {padding:18px; border-radius:18px; background:#151a2e; border:1px solid #2c3356; margin-bottom:12px;}
.metric {font-size:28px; font-weight:700;}
.small {color:#9da7c7;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🎬 CineBook")
    page = st.radio("Navigation", ["🎟️ Book Tickets", "📋 My Bookings", "📊 Admin Dashboard"], index=0)
    st.divider()
    st.caption("Cinema Seat Booking System")
    st.caption("SQLite-powered • Responsive seat map • Booking management")

if page == "🎟️ Book Tickets":
    st.markdown("""
    <div class="hero">
      <h1>🎬 CineBook</h1>
      <p>Choose a movie, select a show, reserve your seats and get an instant booking confirmation.</p>
    </div>
    """, unsafe_allow_html=True)

    movies = get_movies()
    movie_names = [m["title"] for m in movies]
    selected_title = st.selectbox("Select Movie", movie_names)
    movie = next(m for m in movies if m["title"] == selected_title)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(poster_placeholder(movie["title"], movie["genre"]), unsafe_allow_html=True)
    with c2:
        st.subheader(movie["title"])
        st.write(movie["description"])
        st.write(f"**Genre:** {movie['genre']}  •  **Duration:** {movie['duration']} min  •  **Language:** {movie['language']}")

        shows = get_shows(movie["id"])
        if not shows:
            st.warning("No shows available.")
            st.stop()

        show_labels = [f"{s['show_date']} • {s['show_time']} • {s['screen_name']} • ₹{s['price']:.0f}" for s in shows]
        idx = st.selectbox("Select Show", range(len(shows)), format_func=lambda i: show_labels[i])
        show = shows[idx]

    st.divider()
    booked = get_booked_seats(show["id"])
    st.subheader("Choose Your Seats")
    st.caption("🟢 Available   🔴 Booked   🔵 Selected")

    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    cols = list(range(1, 13))
    selected = render_seat_map(rows, cols, booked, st.session_state.selected_seats)

    st.session_state.selected_seats = selected
    total = len(selected) * show["price"]

    a, b, c = st.columns(3)
    a.metric("Selected Seats", len(selected))
    b.metric("Price / Seat", f"₹{show['price']:.0f}")
    c.metric("Total", f"₹{total:.0f}")

    with st.expander("Customer Details", expanded=True):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        payment = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Cash at Counter"])

    if st.button("🎟️ Confirm Booking", type="primary", use_container_width=True):
        if not selected:
            st.error("Please select at least one seat.")
        elif not name.strip() or not email.strip() or not phone.strip():
            st.error("Please complete all customer details.")
        elif "@" not in email:
            st.error("Please enter a valid email address.")
        else:
            try:
                code = create_booking(show["id"], selected, name.strip(), email.strip(), phone.strip(), payment)
                st.session_state.selected_seats = []
                st.success(f"Booking confirmed! Your booking ID is **{code}**.")
                st.balloons()
                st.info(f"Seats: {', '.join(selected)} • Total paid: ₹{total:.0f}")
            except ValueError as e:
                st.error(str(e))

elif page == "📋 My Bookings":
    st.title("📋 Booking History")
    bookings = get_bookings()

    if not bookings:
        st.info("No bookings found yet.")
    else:
        search = st.text_input("Search by booking ID, name, email or phone")
        if search:
            q = search.lower()
            bookings = [b for b in bookings if any(q in str(b[k]).lower() for k in ["booking_code","customer_name","email","phone"])]

        for b in bookings:
            with st.container(border=True):
                left, mid, right = st.columns([2, 3, 1])
                with left:
                    st.subheader(f"🎟️ {b['booking_code']}")
                    st.write(f"**{b['customer_name']}**")
                    st.caption(b["email"])
                with mid:
                    st.write(f"**{b['movie_title']}**")
                    st.write(f"{b['show_date']} • {b['show_time']} • {b['screen_name']}")
                    st.write(f"Seats: **{b['seats']}**")
                    st.write(f"Payment: {b['payment_method']} • ₹{b['total_amount']:.0f}")
                    st.caption(f"Status: {b['status']} • Booked at {b['created_at']}")
                with right:
                    if b["status"] == "CONFIRMED":
                        if st.button("Cancel", key=f"cancel_{b['id']}"):
                            cancel_booking(b["id"])
                            st.rerun()

else:
    st.title("📊 Admin Dashboard")
    stats = get_dashboard_stats()

    a,b,c,d = st.columns(4)
    a.metric("Total Bookings", stats["bookings"])
    b.metric("Confirmed", stats["confirmed"])
    c.metric("Seats Sold", stats["seats_sold"])
    d.metric("Revenue", f"₹{stats['revenue']:.0f}")

    st.divider()
    st.subheader("Revenue & Booking Overview")
    if stats["daily"]:
        import pandas as pd
        df = pd.DataFrame(stats["daily"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        st.line_chart(df[["revenue"]])
        st.bar_chart(df[["bookings"]])
    else:
        st.info("No analytics data yet.")

    st.subheader("Current Shows")
    for s in get_shows():
        st.write(f"**{s['movie_title']}** — {s['show_date']} {s['show_time']} — {s['screen_name']} — ₹{s['price']:.0f}")
