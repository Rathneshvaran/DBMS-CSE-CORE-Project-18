CREATE TABLE IF NOT EXISTS airport (
    airport_id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(80) NOT NULL,
    country VARCHAR(80) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS route (
    route_id INT PRIMARY KEY AUTO_INCREMENT,
    origin_airport_id INT NOT NULL,
    destination_airport_id INT NOT NULL,
    distance_km INT NOT NULL CHECK (distance_km > 0),
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0),
    UNIQUE KEY uq_route (origin_airport_id, destination_airport_id),
    CONSTRAINT fk_route_origin FOREIGN KEY (origin_airport_id) REFERENCES airport(airport_id),
    CONSTRAINT fk_route_destination FOREIGN KEY (destination_airport_id) REFERENCES airport(airport_id),
    CHECK (origin_airport_id <> destination_airport_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INT PRIMARY KEY AUTO_INCREMENT,
    registration VARCHAR(30) NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS seat (
    seat_id INT PRIMARY KEY AUTO_INCREMENT,
    aircraft_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    seat_class ENUM('Economy','Business','First') NOT NULL,
    UNIQUE KEY uq_aircraft_seat (aircraft_id, seat_number),
    CONSTRAINT fk_seat_aircraft FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS flight (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(20) NOT NULL,
    route_id INT NOT NULL,
    aircraft_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    status ENUM('Scheduled','Boarding','Departed','Arrived','Delayed','Cancelled') NOT NULL DEFAULT 'Scheduled',
    UNIQUE KEY uq_flight (flight_number, departure_time),
    CONSTRAINT fk_flight_route FOREIGN KEY (route_id) REFERENCES route(route_id),
    CONSTRAINT fk_flight_aircraft FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS passenger (
    passenger_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    passport_no VARCHAR(40) UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fare (
    fare_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT NOT NULL,
    fare_class ENUM('Economy','Business','First') NOT NULL,
    base_fare DECIMAL(10,2) NOT NULL CHECK (base_fare >= 0),
    tax DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (tax >= 0),
    UNIQUE KEY uq_fare (flight_id, fare_class),
    CONSTRAINT fk_fare_flight FOREIGN KEY (flight_id) REFERENCES flight(flight_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS booking (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    pnr VARCHAR(20) NOT NULL UNIQUE,
    passenger_id INT NOT NULL,
    flight_id INT NOT NULL,
    fare_id INT NOT NULL,
    booking_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Confirmed','Cancelled','Completed') NOT NULL DEFAULT 'Confirmed',
    CONSTRAINT fk_booking_passenger FOREIGN KEY (passenger_id) REFERENCES passenger(passenger_id),
    CONSTRAINT fk_booking_flight FOREIGN KEY (flight_id) REFERENCES flight(flight_id),
    CONSTRAINT fk_booking_fare FOREIGN KEY (fare_id) REFERENCES fare(fare_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    booking_id INT NOT NULL UNIQUE,
    seat_id INT NOT NULL,
    issued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_booking FOREIGN KEY (booking_id) REFERENCES booking(booking_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_seat FOREIGN KEY (seat_id) REFERENCES seat(seat_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS checkin (
    checkin_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL UNIQUE,
    checkin_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Checked-in') NOT NULL DEFAULT 'Checked-in',
    CONSTRAINT fk_checkin_ticket FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS baggage (
    baggage_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    bag_count INT NOT NULL CHECK (bag_count >= 0),
    total_weight_kg DECIMAL(8,2) NOT NULL CHECK (total_weight_kg >= 0),
    baggage_fee DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (baggage_fee >= 0),
    CONSTRAINT fk_baggage_ticket FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cancellation (
    cancellation_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL UNIQUE,
    cancelled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255) NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (refund_amount >= 0),
    CONSTRAINT fk_cancel_booking FOREIGN KEY (booking_id) REFERENCES booking(booking_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    method ENUM('Card','UPI','Cash','Net Banking') NOT NULL,
    payment_status ENUM('Paid','Refunded','Pending','Failed') NOT NULL DEFAULT 'Paid',
    transaction_ref VARCHAR(40) NOT NULL UNIQUE,
    paid_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
) ENGINE=InnoDB;

CREATE INDEX idx_flight_departure ON flight(departure_time);
CREATE INDEX idx_flight_route ON flight(route_id);
CREATE INDEX idx_booking_flight ON booking(flight_id);
CREATE INDEX idx_booking_passenger ON booking(passenger_id);
CREATE INDEX idx_ticket_seat ON ticket(seat_id);
