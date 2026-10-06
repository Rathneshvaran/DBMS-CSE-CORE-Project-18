# SkyOps – Airline Reservation & Flight Operations Management System

## DBMS Course Project – Project 18

SkyOps is a database-driven Airline Reservation and Flight Operations Management System developed as part of the Database Management Systems (DBMS) course project.

The system manages airline operations including airports, aircraft, routes, flights, passengers, seats, bookings, tickets, payments, check-in, baggage and cancellations.

The project uses a **Flask web application** connected to a **MySQL relational database**.

---

## Project Objectives

- Design and implement a relational database for airline reservation and flight operations.
- Convert the ER model into a relational schema.
- Normalize the database up to Third Normal Form (3NF).
- Maintain data integrity using primary keys, foreign keys and constraints.
- Provide flight search functionality.
- Manage passenger records.
- Support flight booking and seat allocation.
- Manage ticket and payment information.
- Provide passenger check-in functionality.
- Manage baggage information and baggage charges.
- Support booking cancellation and refund processing.
- Generate reports using SQL queries.
- Demonstrate CRUD operations through a web interface connected to MySQL.

---

## Key Features

### Flight Search
Search flights based on:

- Origin
- Destination
- Travel date

### Passenger Management
- Add passengers
- View passenger records
- Delete eligible passenger records
- Store passenger name, email, phone and passport details

### Flight Booking
- Select a flight
- Select a passenger
- Select an available seat
- Create a booking
- Generate PNR
- Process payment
- Issue ticket

### Seat Allocation
The system checks existing confirmed bookings before allocating a seat and prevents duplicate seat allocation for the same flight.

### Check-in
Check-in is allowed only for valid confirmed bookings and duplicate check-in is prevented.

### Baggage Management
The system records:

- Number of bags
- Total baggage weight
- Baggage fee

Negative baggage values are rejected through validation.

### Cancellation
Confirmed bookings can be cancelled. The system records the cancellation reason, refund amount and cancellation time.

### Reports
The system provides reports using SQL operations such as:

- JOIN
- COUNT
- SUM
- GROUP BY
- Filtering
- Aggregation

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Application development |
| Flask | Web application framework |
| MySQL | Relational database |
| HTML | Web page structure |
| CSS | User interface design |
| JavaScript | Client-side functionality |
| Jinja2 | Template rendering |
| MySQL Connector/Python | Database connectivity |
| Git | Version control |
| GitHub | Repository and project submission |

---

## Database Design

The SkyOps database contains 13 tables:

1. `airport`
2. `aircraft`
3. `route`
4. `seat`
5. `flight`
6. `passenger`
7. `fare`
8. `booking`
9. `ticket`
10. `payment`
11. `checkin`
12. `baggage`
13. `cancellation`

### Major Relationships

- Airport → Route : 1:N
- Aircraft → Seat : 1:N
- Route → Flight : 1:N
- Aircraft → Flight : 1:N
- Passenger → Booking : 1:N
- Flight → Booking : 1:N
- Fare → Booking : 1:N
- Booking → Ticket : 1:1
- Booking → Payment : 1:1
- Ticket → Check-in : 1:1
- Ticket → Baggage : 1:N
- Booking → Cancellation : 1:0..1

---

## Normalization

The database is normalized up to **Third Normal Form (3NF)**.

### 1NF
All attributes contain atomic values and repeating groups are eliminated.

### 2NF
Partial dependencies are removed after satisfying 1NF.

### 3NF
Transitive dependencies are removed after satisfying 2NF.

Normalization reduces redundancy and prevents insertion, update and deletion anomalies.

---

## Database Integrity

### Database Constraints

The system uses:

- Primary Keys
- Foreign Keys
- UNIQUE constraints
- NOT NULL constraints
- Referential integrity

### Business Rules

- A seat cannot be assigned to multiple confirmed bookings for the same flight.
- Aircraft capacity cannot be exceeded.
- Baggage count and weight cannot be negative.
- Check-in is allowed only for confirmed bookings.
- Cancelled bookings cannot be checked in.
- Only confirmed bookings can be cancelled.

---

**Localhost:** http://127.0.0.1:5000
