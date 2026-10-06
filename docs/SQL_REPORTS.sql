-- 1. Flight manifest
SELECT f.flight_number, oa.code origin, da.code destination, p.full_name,
       t.ticket_number, s.seat_number, COALESCE(ci.status,'Not Checked-in') checkin
FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id
JOIN flight f ON f.flight_id=b.flight_id JOIN route r ON r.route_id=f.route_id
JOIN airport oa ON oa.airport_id=r.origin_airport_id JOIN airport da ON da.airport_id=r.destination_airport_id
JOIN ticket t ON t.booking_id=b.booking_id JOIN seat s ON s.seat_id=t.seat_id
LEFT JOIN checkin ci ON ci.ticket_id=t.ticket_id;

-- 2. Occupancy
SELECT f.flight_number, a.capacity,
       COUNT(CASE WHEN b.status='Confirmed' THEN 1 END) booked,
       ROUND(100.0*COUNT(CASE WHEN b.status='Confirmed' THEN 1 END)/a.capacity,2) occupancy_pct
FROM flight f JOIN aircraft a ON a.aircraft_id=f.aircraft_id
LEFT JOIN booking b ON b.flight_id=f.flight_id GROUP BY f.flight_id;

-- 3. Route demand
SELECT oa.city origin, da.city destination, COUNT(b.booking_id) bookings
FROM route r JOIN airport oa ON oa.airport_id=r.origin_airport_id
JOIN airport da ON da.airport_id=r.destination_airport_id
LEFT JOIN flight f ON f.route_id=r.route_id LEFT JOIN booking b ON b.flight_id=f.flight_id
GROUP BY r.route_id ORDER BY bookings DESC;

-- 4. Baggage report
SELECT f.flight_number, SUM(bg.bag_count) bags, SUM(bg.total_weight_kg) total_weight,
       SUM(bg.baggage_fee) fees
FROM baggage bg JOIN ticket t ON t.ticket_id=bg.ticket_id
JOIN booking b ON b.booking_id=t.booking_id JOIN flight f ON f.flight_id=b.flight_id
GROUP BY f.flight_id;

-- 5. Cancellation/refund report
SELECT b.pnr,p.full_name,f.flight_number,c.reason,c.refund_amount
FROM cancellation c JOIN booking b ON b.booking_id=c.booking_id
JOIN passenger p ON p.passenger_id=b.passenger_id JOIN flight f ON f.flight_id=b.flight_id;

-- 6. Revenue
SELECT f.flight_number,
       COALESCE(SUM(CASE WHEN py.payment_status='Paid' THEN py.amount ELSE 0 END),0) revenue,
       COALESCE(SUM(CASE WHEN py.payment_status='Refunded' THEN py.amount ELSE 0 END),0) refunded
FROM flight f LEFT JOIN booking b ON b.flight_id=f.flight_id
LEFT JOIN payment py ON py.booking_id=b.booking_id GROUP BY f.flight_id;

-- 7. Nested query: flights above average fare
SELECT flight_number FROM flight WHERE flight_id IN (
  SELECT flight_id FROM fare GROUP BY flight_id HAVING AVG(base_fare) > (SELECT AVG(base_fare) FROM fare)
);

-- 8. View for flight summary
CREATE VIEW IF NOT EXISTS vw_flight_summary AS
SELECT f.flight_id,f.flight_number,oa.code origin,da.code destination,
       f.departure_time,f.status,a.capacity,
       COUNT(CASE WHEN b.status='Confirmed' THEN 1 END) booked
FROM flight f JOIN route r ON r.route_id=f.route_id
JOIN airport oa ON oa.airport_id=r.origin_airport_id JOIN airport da ON da.airport_id=r.destination_airport_id
JOIN aircraft a ON a.aircraft_id=f.aircraft_id LEFT JOIN booking b ON b.flight_id=f.flight_id
GROUP BY f.flight_id;
