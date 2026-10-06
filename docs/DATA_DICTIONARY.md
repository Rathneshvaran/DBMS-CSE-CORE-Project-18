# Data Dictionary — Airline Reservation System

| Table | Purpose | Primary Key | Key attributes |
|---|---|---|---|
| airport | Airport master | airport_id | code, name, city, country |
| route | Airport-to-airport route | route_id | origin_airport_id, destination_airport_id, distance_km |
| aircraft | Aircraft master | aircraft_id | registration, model, capacity |
| seat | Seats belonging to aircraft | seat_id | aircraft_id, seat_number, seat_class |
| flight | Scheduled flight operation | flight_id | flight_number, route_id, aircraft_id, departure_time, status |
| passenger | Passenger master | passenger_id | full_name, email, phone, passport_no |
| fare | Fare options for a flight | fare_id | flight_id, fare_class, base_fare, tax |
| booking | Reservation record | booking_id | pnr, passenger_id, flight_id, fare_id, status |
| ticket | Issued travel document | ticket_id | ticket_number, booking_id, seat_id |
| checkin | Check-in event | checkin_id | ticket_id, checkin_time, status |
| baggage | Baggage record | baggage_id | ticket_id, bag_count, total_weight_kg, baggage_fee |
| cancellation | Cancellation/refund record | cancellation_id | booking_id, reason, refund_amount |
| payment | Financial transaction | payment_id | booking_id, amount, method, payment_status |

## Main constraints
- Airport code, aircraft registration, passenger email/passport, PNR and ticket number are unique.
- A seat is unique within an aircraft.
- A fare class is unique per flight.
- A booking can have one ticket; a ticket can have one check-in.
- Baggage count, weight, fees, fares and refunds cannot be negative.
- Booking status is controlled by CHECK constraints.
- Seat allocation is validated transactionally before ticket issue.
- Aircraft capacity is checked before confirmation.
