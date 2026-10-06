# Airline Reservation & Flight Operations Management System — Review 3

## Stack
- Python 3
- Flask
- MySQL 9.x (Homebrew or standalone MySQL Server)
- HTML/CSS/JavaScript

## Run on macOS with your installed MySQL
1. Make sure MySQL is running:
   `brew services start mysql`
2. Extract this folder.
3. Open Terminal in this folder.
4. Run:
   `chmod +x start_mac.command`
5. Run:
   `./start_mac.command`
6. Enter your MySQL root password when prompted.
7. Open http://127.0.0.1:5000

The application automatically creates the `airline_reservation` database, creates all tables, indexes and constraints, and inserts realistic demo data on first run.

## Manual run
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set MYSQL_PASSWORD
python run.py
```

## Database
Database: `airline_reservation`

Main tables:
`airport`, `route`, `aircraft`, `seat`, `flight`, `passenger`, `fare`, `booking`, `ticket`, `checkin`, `baggage`, `cancellation`, `payment`.

## Demo flow
1. Dashboard
2. Search flights
3. Book a flight and allocate a seat
4. Show generated PNR, ticket and payment
5. Booking lookup
6. Check-in
7. Add baggage
8. Cancel booking and show refund
9. Reports: manifest, occupancy, route demand, baggage, cancellations, revenue

## DBMS deliverables
- `schema.sql`: MySQL DDL
- `docs/mysql_schema.sql`: concise schema reference
- `docs/SQL_REPORTS.sql`: joins, subqueries, aggregates and views
- `docs/NORMALIZATION.md`: 1NF → 2NF → 3NF and functional dependencies
- `docs/DATA_DICTIONARY.md`: data dictionary
- `docs/TEST_CASES.md`: systematic test cases


## Final Presentation — Passenger CRUD Demo

Open **Passengers** from the navigation bar.

### INSERT
1. Enter a new passenger (for example `Demo Passenger`, `demo@gmail.com`, `9876543210`).
2. Click **Add Passenger**.
3. The passenger appears in the UI and is inserted into MySQL.

### VIEW
The Passenger Records table is loaded directly from the MySQL `passenger` table.

### DELETE
1. Delete the newly-created demo passenger.
2. The passenger disappears from the UI and is deleted from MySQL.
3. In the MySQL terminal verify with:
   `SELECT * FROM passenger;`

Passengers with existing bookings are intentionally protected from deletion to preserve foreign-key/data integrity.
