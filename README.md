# Cinema Seat Booking System

A strong portfolio-ready cinema ticket reservation application built with Python, Streamlit and SQLite.

## Features

- Movie catalog and show selection
- 96-seat interactive seat map (8 rows × 12 seats)
- Real-time booked-seat protection using SQLite constraints
- Customer details and payment-method selection
- Unique booking confirmation codes
- Booking history with search
- Ticket cancellation
- Revenue and booking analytics
- Persistent local SQLite database
- Responsive Streamlit dashboard
- Clean project structure

## Tech Stack

- Python 3.10+
- Streamlit
- SQLite
- Pandas

## Project Structure

```text
Cinema_Seat_Booking_System/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── cinema.db              # created automatically
└── src/
    ├── __init__.py
    ├── database.py
    ├── services.py
    └── ui.py
```

## Run on Windows

```powershell
cd "Cinema_Seat_Booking_System"
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit, normally:
`http://localhost:8501`

## Reset Demo Data

Stop Streamlit and delete:

```text
data/cinema.db
```

Then start the app again. The sample movies and shows will be recreated.

## Portfolio Highlights

This project demonstrates CRUD-style workflows, relational database design, transaction handling, unique constraints, interactive UI state, validation, analytics, and dashboard development.
