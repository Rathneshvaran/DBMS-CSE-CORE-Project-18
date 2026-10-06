# Normalization to Third Normal Form (3NF)

## 1NF
All attributes are atomic. Repeating groups such as multiple seats, baggage items and payments are separated into their own relations rather than stored as comma-separated values.

## 2NF
Each relation has a single-column surrogate primary key. Non-key attributes depend on the whole primary key. Seat properties depend on `seat_id`; flight properties depend on `flight_id`; passenger properties depend on `passenger_id`.

## 3NF
Transitive dependencies are removed. Airport details are stored only in `airport`; aircraft details only in `aircraft`; route details reference airports; fare details reference flights; passenger details are not repeated in bookings; payment details are not stored inside booking.

## Representative functional dependencies
- `airport_id -> code, name, city, country`
- `route_id -> origin_airport_id, destination_airport_id, distance_km, duration_minutes`
- `aircraft_id -> registration, model, capacity`
- `(aircraft_id, seat_number) -> seat_class`
- `flight_id -> flight_number, route_id, aircraft_id, departure_time, arrival_time, status`
- `passenger_id -> full_name, email, phone, passport_no`
- `fare_id -> flight_id, fare_class, base_fare, tax`
- `booking_id -> pnr, passenger_id, flight_id, fare_id, booking_date, status`
- `ticket_id -> ticket_number, booking_id, seat_id, issued_at`
- `checkin_id -> ticket_id, checkin_time, status`
- `baggage_id -> ticket_id, bag_count, total_weight_kg, baggage_fee`
- `cancellation_id -> booking_id, cancelled_at, reason, refund_amount`
- `payment_id -> booking_id, amount, method, payment_status, transaction_ref, paid_at`

This decomposition avoids update, insertion and deletion anomalies and satisfies 3NF for the operational schema.
