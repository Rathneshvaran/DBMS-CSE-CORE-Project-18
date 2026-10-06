from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os, uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "airline-review3-demo-secret")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "airline_reservation"),
}

class Row(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

class CursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = cursor.lastrowid
    def fetchone(self):
        row = self.cursor.fetchone()
        return Row(row) if row else None
    def fetchall(self):
        return [Row(r) for r in self.cursor.fetchall()]
    def __iter__(self):
        # Allow normal Python constructs such as list(conn.execute(...))
        # with MySQL dictionary cursors.
        for row in self.cursor:
            yield Row(row)

class DBConnection:
    def __init__(self):
        self.conn = mysql.connector.connect(**MYSQL_CONFIG)
        self._lastrowid = None
    def execute(self, sql, params=()):
        sql = sql.replace("?", "%s")
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql, params)
        self._lastrowid = cur.lastrowid
        return CursorWrapper(cur)
    def executemany(self, sql, seq):
        sql = sql.replace("?", "%s")
        cur = self.conn.cursor(dictionary=True)
        cur.executemany(sql, seq)
        self._lastrowid = cur.lastrowid
        return CursorWrapper(cur)
    def commit(self): self.conn.commit()
    def rollback(self): self.conn.rollback()
    def close(self): self.conn.close()

def get_db():
    return DBConnection()

def ensure_database():
    cfg = MYSQL_CONFIG.copy(); db = cfg.pop("database")
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit(); cur.close(); conn.close()


def init_db():
    ensure_database()
    conn = get_db()
    schema = open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8").read()
    # schema.sql contains DDL only; execute each statement separately for MySQL.
    for statement in schema.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        # Index DDL is handled below so re-running the application against an
        # already-created database never fails with MySQL error 1061.
        if statement.upper().startswith("CREATE INDEX"):
            continue
        conn.execute(statement)
    conn.commit()
    ensure_indexes(conn)
    conn.commit()
    seed(conn)
    conn.close()



def ensure_indexes(conn):
    """Create frequently-used indexes only when they do not already exist."""
    indexes = [
        ("flight", "idx_flight_departure", "departure_time"),
        ("flight", "idx_flight_route", "route_id"),
        ("booking", "idx_booking_flight", "flight_id"),
        ("booking", "idx_booking_passenger", "passenger_id"),
        ("ticket", "idx_ticket_seat", "seat_id"),
    ]
    for table, name, column in indexes:
        exists = conn.execute(
            "SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name=? AND index_name=? LIMIT 1",
            (table, name)
        ).fetchone()
        if not exists:
            conn.execute(f"CREATE INDEX {name} ON {table} ({column})")


def seed(conn):
    if conn.execute('SELECT COUNT(*) FROM airport').fetchone()[0] > 0:
        return
    airports = [
        ('MAA','Chennai International Airport','Chennai','India'),
        ('HYD','Rajiv Gandhi International Airport','Hyderabad','India'),
        ('DEL','Indira Gandhi International Airport','Delhi','India'),
        ('BOM','Chhatrapati Shivaji Maharaj International Airport','Mumbai','India'),
        ('BLR','Kempegowda International Airport','Bengaluru','India'),
        ('COK','Cochin International Airport','Kochi','India')]
    conn.executemany('INSERT INTO airport(code,name,city,country) VALUES (?,?,?,?)', airports)
    aid = {r['code']: r['airport_id'] for r in conn.execute('SELECT * FROM airport').fetchall()}
    routes = [('MAA','HYD',520,85),('HYD','DEL',1260,145),('MAA','DEL',1760,170),('BOM','BLR',840,105),('HYD','BOM',620,95),('BLR','COK',365,70),('DEL','BOM',1150,135)]
    conn.executemany('INSERT INTO route(origin_airport_id,destination_airport_id,distance_km,duration_minutes) VALUES (?,?,?,?)', [(aid[a],aid[b],d,t) for a,b,d,t in routes])
    aircraft = [('VT-ANA','Airbus A320',180),('VT-BNB','Boeing 737-800',189),('VT-CNC','Airbus A321',220)]
    conn.executemany('INSERT INTO aircraft(registration,model,capacity) VALUES (?,?,?)', aircraft)
    aircraft_rows = list(conn.execute('SELECT * FROM aircraft'))
    for ac in aircraft_rows:
        n = ac['capacity']
        # keep seed compact while preserving realistic capacities
        for i in range(1, n+1):
            row = (ac['aircraft_id'], f'{i}{chr(65 + ((i-1)%6))}', 'Economy' if i > 18 else ('Business' if i > 6 else 'First'))
            conn.execute('INSERT INTO seat(aircraft_id,seat_number,seat_class) VALUES (?,?,?)', row)
    route_rows = { (r['origin_airport_id'],r['destination_airport_id']): r['route_id'] for r in conn.execute('SELECT * FROM route').fetchall() }
    acrows = conn.execute('SELECT * FROM aircraft').fetchall()
    flights = [
        ('AI101',route_rows[(aid['MAA'],aid['HYD'])],acrows[0]['aircraft_id'],'2026-10-06 09:30','2026-10-06 10:55','Scheduled'),
        ('AI202',route_rows[(aid['HYD'],aid['DEL'])],acrows[1]['aircraft_id'],'2026-10-06 12:15','2026-10-06 14:40','Scheduled'),
        ('6E303',route_rows[(aid['MAA'],aid['DEL'])],acrows[2]['aircraft_id'],'2026-10-07 08:00','2026-10-07 10:50','Scheduled'),
        ('6E404',route_rows[(aid['BOM'],aid['BLR'])],acrows[0]['aircraft_id'],'2026-10-07 15:00','2026-10-07 16:45','Scheduled'),
        ('UK505',route_rows[(aid['HYD'],aid['BOM'])],acrows[1]['aircraft_id'],'2026-10-08 18:30','2026-10-08 20:05','Scheduled'),
        ('AI606',route_rows[(aid['BLR'],aid['COK'])],acrows[0]['aircraft_id'],'2026-10-09 07:30','2026-10-09 08:40','Arrived')]
    conn.executemany('INSERT INTO flight(flight_number,route_id,aircraft_id,departure_time,arrival_time,status) VALUES (?,?,?,?,?,?)', flights)
    for f in conn.execute('SELECT flight_id FROM flight').fetchall():
        conn.executemany('INSERT INTO fare(flight_id,fare_class,base_fare,tax) VALUES (?,?,?,?)', [(f['flight_id'],'Economy',4200,756),(f['flight_id'],'Business',8500,1530),(f['flight_id'],'First',14000,2520)])
    passengers = [('Rathnesh Ilangovan','rathnesh@example.com','9876543210','P1234567'),('Aarav Sharma','aarav@example.com','9876501234','P2345678'),('Priya Nair','priya@example.com','9876512345','P3456789'),('Karan Rao','karan@example.com','9876523456','P4567890'),('Meera Iyer','meera@example.com','9876534567','P5678901')]
    conn.executemany('INSERT INTO passenger(full_name,email,phone,passport_no) VALUES (?,?,?,?)', passengers)
    # seed a few confirmed bookings with tickets and payments
    f1 = conn.execute("SELECT * FROM flight WHERE flight_number='AI101'").fetchone()
    fare1 = conn.execute("SELECT * FROM fare WHERE flight_id=? AND fare_class='Economy'",(f1['flight_id'],)).fetchone()
    for idx, email in enumerate(['rathnesh@example.com','aarav@example.com','priya@example.com']):
        p = conn.execute('SELECT * FROM passenger WHERE email=?',(email,)).fetchone()
        pnr = f'DEM{idx+1:03d}'
        conn.execute('INSERT INTO booking(pnr,passenger_id,flight_id,fare_id,status) VALUES (?,?,?,?,?)',(pnr,p['passenger_id'],f1['flight_id'],fare1['fare_id'],'Confirmed'))
        bid = conn._lastrowid
        seat = conn.execute("SELECT seat_id FROM seat WHERE aircraft_id=? ORDER BY seat_id LIMIT 1 OFFSET ?",(f1['aircraft_id'],idx)).fetchone()
        if seat is None:
            raise RuntimeError('Demo seat allocation failed during database seeding')
        conn.execute('INSERT INTO ticket(ticket_number,booking_id,seat_id) VALUES (?,?,?)',(f'TKT{10001+idx}',bid,seat['seat_id']))
        total = fare1['base_fare'] + fare1['tax']
        conn.execute('INSERT INTO payment(booking_id,amount,method,transaction_ref) VALUES (?,?,?,?)',(bid,total,'UPI',f'TXN{50001+idx}'))
    conn.commit()


def flight_query():
    return '''SELECT f.*, r.distance_km, oa.code origin_code, oa.city origin_city, da.code destination_code, da.city destination_city,
                     a.model, a.capacity,
                     (SELECT COUNT(*) FROM booking b WHERE b.flight_id=f.flight_id AND b.status='Confirmed') booked
              FROM flight f JOIN route r ON f.route_id=r.route_id
              JOIN airport oa ON r.origin_airport_id=oa.airport_id
              JOIN airport da ON r.destination_airport_id=da.airport_id
              JOIN aircraft a ON f.aircraft_id=a.aircraft_id'''

@app.route('/')
def index():
    conn=get_db(); flights=conn.execute(flight_query()+' ORDER BY f.departure_time').fetchall()
    stats={
        'flights': conn.execute('SELECT COUNT(*) FROM flight').fetchone()[0],
        'passengers': conn.execute('SELECT COUNT(*) FROM passenger').fetchone()[0],
        'bookings': conn.execute("SELECT COUNT(*) FROM booking WHERE status='Confirmed'").fetchone()[0],
        'revenue': conn.execute("SELECT COALESCE(SUM(amount),0) FROM payment WHERE payment_status='Paid'").fetchone()[0]
    }; conn.close(); return render_template('index.html',flights=flights,stats=stats)

@app.route('/search', methods=['GET','POST'])
def search():
    conn=get_db(); airports=conn.execute('SELECT * FROM airport ORDER BY city').fetchall()
    origin=request.values.get('origin',''); destination=request.values.get('destination',''); date=request.values.get('date','')
    q=flight_query()+' WHERE 1=1'; params=[]
    if origin: q+=' AND oa.code=?'; params.append(origin)
    if destination: q+=' AND da.code=?'; params.append(destination)
    if date: q+=' AND date(f.departure_time)=?'; params.append(date)
    q+=' ORDER BY f.departure_time'; flights=conn.execute(q,params).fetchall(); conn.close()
    return render_template('search.html',flights=flights,airports=airports,origin=origin,destination=destination,date=date)

@app.route('/book/<int:flight_id>', methods=['GET','POST'])
def book(flight_id):
    conn=get_db(); flight=conn.execute(flight_query()+' WHERE f.flight_id=?',(flight_id,)).fetchone()
    fares=conn.execute('SELECT * FROM fare WHERE flight_id=? ORDER BY base_fare',(flight_id,)).fetchall()
    seats=conn.execute("SELECT s.* FROM seat s WHERE s.aircraft_id=? AND NOT EXISTS (SELECT 1 FROM ticket t JOIN booking b ON b.booking_id=t.booking_id WHERE t.seat_id=s.seat_id AND b.flight_id=? AND b.status='Confirmed') ORDER BY s.seat_id",(flight['aircraft_id'],flight_id)).fetchall()
    if request.method=='POST':
        name,email,phone,passport=request.form['name'].strip(),request.form['email'].strip(),request.form['phone'].strip(),request.form.get('passport','').strip()
        fare_id=int(request.form['fare_id']); seat_id=int(request.form['seat_id']); method=request.form['method']
        try:
            conn.execute('START TRANSACTION')
            p=conn.execute('SELECT * FROM passenger WHERE email=?',(email,)).fetchone()
            if p: pid=p['passenger_id']; conn.execute('UPDATE passenger SET full_name=?,phone=?,passport_no=? WHERE passenger_id=?',(name,phone,passport or None,pid))
            else:
                conn.execute('INSERT INTO passenger(full_name,email,phone,passport_no) VALUES (?,?,?,?)',(name,email,phone,passport or None)); pid=conn._lastrowid
            fare=conn.execute('SELECT * FROM fare WHERE fare_id=? AND flight_id=?',(fare_id,flight_id)).fetchone()
            if not fare: raise ValueError('Invalid fare selection.')
            available=conn.execute("SELECT 1 FROM seat s WHERE s.seat_id=? AND s.aircraft_id=? AND NOT EXISTS (SELECT 1 FROM ticket t JOIN booking b ON b.booking_id=t.booking_id WHERE t.seat_id=s.seat_id AND b.flight_id=? AND b.status='Confirmed')",(seat_id,flight['aircraft_id'],flight_id)).fetchone()
            if not available: raise ValueError('Selected seat is no longer available.')
            booked=conn.execute("SELECT COUNT(*) FROM booking WHERE flight_id=? AND status='Confirmed'",(flight_id,)).fetchone()[0]
            if booked >= flight['capacity']: raise ValueError('Aircraft capacity reached.')
            pnr=''.join(uuid.uuid4().hex[:6].upper()); conn.execute('INSERT INTO booking(pnr,passenger_id,flight_id,fare_id,status) VALUES (?,?,?,?,?)',(pnr,pid,flight_id,fare_id,'Confirmed')); bid=conn._lastrowid
            conn.execute('INSERT INTO ticket(ticket_number,booking_id,seat_id) VALUES (?,?,?)',(f'TKT{uuid.uuid4().hex[:8].upper()}',bid,seat_id))
            amount=fare['base_fare']+fare['tax']; conn.execute('INSERT INTO payment(booking_id,amount,method,transaction_ref) VALUES (?,?,?,?)',(bid,amount,method,f'TXN{uuid.uuid4().hex[:10].upper()}'))
            conn.commit(); flash(f'Booking confirmed. PNR: {pnr}', 'success'); return redirect(url_for('booking',pnr=pnr))
        except Exception as e:
            conn.rollback(); flash(str(e),'error')
    conn.close(); return render_template('book.html',flight=flight,fares=fares,seats=seats)

@app.route('/booking', methods=['GET','POST'])
def booking():
    pnr=request.values.get('pnr','').strip().upper(); conn=get_db(); row=None
    if pnr:
        row=conn.execute('''SELECT b.*, p.full_name,p.email,p.phone,f.flight_number,f.departure_time,f.arrival_time,oa.city origin_city,da.city destination_city,
                            t.ticket_number,t.ticket_id,s.seat_number,fa.fare_class,fa.base_fare,fa.tax,py.amount,py.method,py.payment_status
                            FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id JOIN flight f ON f.flight_id=b.flight_id
                            JOIN route r ON r.route_id=f.route_id JOIN airport oa ON oa.airport_id=r.origin_airport_id JOIN airport da ON da.airport_id=r.destination_airport_id
                            JOIN ticket t ON t.booking_id=b.booking_id JOIN seat s ON s.seat_id=t.seat_id JOIN fare fa ON fa.fare_id=b.fare_id
                            LEFT JOIN payment py ON py.booking_id=b.booking_id WHERE b.pnr=?''',(pnr,)).fetchone()
    conn.close(); return render_template('booking.html',row=row,pnr=pnr)

@app.route('/checkin', methods=['GET','POST'])
def checkin():
    pnr=request.values.get('pnr','').strip().upper(); msg=None; row=None; conn=get_db()
    if pnr:
        row=conn.execute('''SELECT b.*,p.full_name,f.flight_number,f.departure_time,f.status,t.ticket_id,t.ticket_number,s.seat_number
                            FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id JOIN flight f ON f.flight_id=b.flight_id
                            JOIN ticket t ON t.booking_id=b.booking_id JOIN seat s ON s.seat_id=t.seat_id WHERE b.pnr=?''',(pnr,)).fetchone()
    if request.method=='POST' and row:
        if row['status']!='Confirmed': flash('Check-in allowed only for confirmed bookings.','error')
        elif row['status']=='Cancelled': flash('Cancelled booking cannot be checked in.','error')
        elif conn.execute('SELECT 1 FROM checkin WHERE ticket_id=?',(row['ticket_id'],)).fetchone(): flash('Passenger is already checked in.','error')
        else:
            conn.execute('INSERT INTO checkin(ticket_id) VALUES (?)',(row['ticket_id'],)); conn.commit(); flash('Check-in completed successfully.','success')
    conn.close(); return render_template('checkin.html',row=row,pnr=pnr)

@app.route('/baggage', methods=['GET','POST'])
def baggage():
    pnr=request.values.get('pnr','').strip().upper(); row=None; conn=get_db()
    if pnr: row=conn.execute('''SELECT b.pnr,b.status,p.full_name,t.ticket_id,f.flight_number,s.seat_number FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id JOIN ticket t ON t.booking_id=b.booking_id JOIN flight f ON f.flight_id=b.flight_id JOIN seat s ON s.seat_id=t.seat_id WHERE b.pnr=?''',(pnr,)).fetchone()
    if request.method=='POST' and row:
        try:
            count=int(request.form['bag_count']); weight=float(request.form['weight']); fee=max(0,weight-15)*300
            if count<0 or weight<0: raise ValueError('Baggage values cannot be negative.')
            conn.execute('INSERT INTO baggage(ticket_id,bag_count,total_weight_kg,baggage_fee) VALUES (?,?,?,?)',(row['ticket_id'],count,weight,fee)); conn.commit(); flash(f'Baggage recorded. Fee: ₹{fee:.2f}','success')
        except Exception as e: flash(str(e),'error')
    conn.close(); return render_template('baggage.html',row=row,pnr=pnr)

@app.route('/cancel', methods=['GET','POST'])
def cancel():
    pnr=request.values.get('pnr','').strip().upper(); row=None; conn=get_db()
    if pnr: row=conn.execute('''SELECT b.*,p.full_name,f.departure_time,fa.base_fare,fa.tax,py.payment_id,py.amount FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id JOIN fare fa ON fa.fare_id=b.fare_id LEFT JOIN payment py ON py.booking_id=b.booking_id JOIN flight f ON f.flight_id=b.flight_id WHERE b.pnr=?''',(pnr,)).fetchone()
    if request.method=='POST' and row:
        if row['status']!='Confirmed': flash('Only confirmed bookings can be cancelled.','error')
        else:
            refund = round(float(row['amount'] or 0) * 0.80, 2)
            conn.execute('BEGIN'); conn.execute("UPDATE booking SET status='Cancelled' WHERE booking_id=?",(row['booking_id'],)); conn.execute('INSERT INTO cancellation(booking_id,reason,refund_amount) VALUES (?,?,?)',(row['booking_id'],request.form.get('reason','Customer request'),refund));
            if row['payment_id']: conn.execute("UPDATE payment SET payment_status='Refunded' WHERE payment_id=?",(row['payment_id'],))
            conn.commit(); flash(f'Booking cancelled. Refund: ₹{refund:.2f}','success'); row=conn.execute('''SELECT b.*,p.full_name,f.departure_time,fa.base_fare,fa.tax,py.amount FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id JOIN fare fa ON fa.fare_id=b.fare_id LEFT JOIN payment py ON py.booking_id=b.booking_id JOIN flight f ON f.flight_id=b.flight_id WHERE b.pnr=?''',(pnr,)).fetchone()
    conn.close(); return render_template('cancel.html',row=row,pnr=pnr)

@app.route('/reports')
def reports():
    conn=get_db()
    manifest=conn.execute('''SELECT f.flight_number,oa.code origin,da.code destination,p.full_name,t.ticket_number,s.seat_number,COALESCE(ci.status,'Not Checked-in') checkin,b.status booking_status
      FROM booking b JOIN passenger p ON p.passenger_id=b.passenger_id JOIN flight f ON f.flight_id=b.flight_id JOIN route r ON r.route_id=f.route_id JOIN airport oa ON oa.airport_id=r.origin_airport_id JOIN airport da ON da.airport_id=r.destination_airport_id JOIN ticket t ON t.booking_id=b.booking_id JOIN seat s ON s.seat_id=t.seat_id LEFT JOIN checkin ci ON ci.ticket_id=t.ticket_id ORDER BY f.flight_number,s.seat_number''').fetchall()
    occupancy=conn.execute('''SELECT f.flight_number,oa.code origin,da.code destination,a.capacity,COUNT(CASE WHEN b.status='Confirmed' THEN 1 END) booked,ROUND(100.0*COUNT(CASE WHEN b.status='Confirmed' THEN 1 END)/a.capacity,2) occupancy_pct FROM flight f JOIN route r ON r.route_id=f.route_id JOIN airport oa ON oa.airport_id=r.origin_airport_id JOIN airport da ON da.airport_id=r.destination_airport_id JOIN aircraft a ON a.aircraft_id=f.aircraft_id LEFT JOIN booking b ON b.flight_id=f.flight_id GROUP BY f.flight_id''').fetchall()
    demand=conn.execute('''SELECT oa.code origin,da.code destination,COUNT(b.booking_id) bookings FROM route r JOIN airport oa ON oa.airport_id=r.origin_airport_id JOIN airport da ON da.airport_id=r.destination_airport_id LEFT JOIN flight f ON f.route_id=r.route_id LEFT JOIN booking b ON b.flight_id=f.flight_id GROUP BY r.route_id ORDER BY bookings DESC''').fetchall()
    baggage=conn.execute('''SELECT f.flight_number,COUNT(bg.baggage_id) baggage_records,COALESCE(SUM(bg.bag_count),0) bags,COALESCE(SUM(bg.total_weight_kg),0) total_weight,COALESCE(SUM(bg.baggage_fee),0) fees FROM flight f JOIN booking b ON b.flight_id=f.flight_id JOIN ticket t ON t.booking_id=b.booking_id LEFT JOIN baggage bg ON bg.ticket_id=t.ticket_id GROUP BY f.flight_id''').fetchall()
    cancellations=conn.execute('''SELECT b.pnr,p.full_name,f.flight_number,c.reason,c.refund_amount,c.cancelled_at FROM cancellation c JOIN booking b ON b.booking_id=c.booking_id JOIN passenger p ON p.passenger_id=b.passenger_id JOIN flight f ON f.flight_id=b.flight_id ORDER BY c.cancelled_at DESC''').fetchall()
    revenue=conn.execute('''SELECT f.flight_number,COUNT(DISTINCT b.booking_id) bookings,COALESCE(SUM(CASE WHEN py.payment_status='Paid' THEN py.amount ELSE 0 END),0) revenue,COALESCE(SUM(CASE WHEN py.payment_status='Refunded' THEN py.amount ELSE 0 END),0) refunded FROM flight f LEFT JOIN booking b ON b.flight_id=f.flight_id LEFT JOIN payment py ON py.booking_id=b.booking_id GROUP BY f.flight_id ORDER BY revenue DESC''').fetchall()
    conn.close(); return render_template('reports.html',manifest=manifest,occupancy=occupancy,demand=demand,baggage=baggage,cancellations=cancellations,revenue=revenue)


@app.route('/passengers', methods=['GET', 'POST'])
def passengers():
    """Demo-friendly passenger CRUD page for the final presentation."""
    conn = get_db()
    try:
        if request.method == 'POST':
            action = request.form.get('action', 'add')
            if action == 'add':
                name = request.form.get('full_name', '').strip()
                email = request.form.get('email', '').strip()
                phone = request.form.get('phone', '').strip()
                passport = request.form.get('passport_no', '').strip() or None

                if not name or not email or not phone:
                    raise ValueError('Name, email and phone are required.')

                # Simple input validation for a clean classroom demo.
                if '@' not in email:
                    raise ValueError('Please enter a valid email address.')

                existing = conn.execute(
                    'SELECT passenger_id FROM passenger WHERE email=?',
                    (email,)
                ).fetchone()
                if existing:
                    raise ValueError('A passenger with this email already exists.')

                conn.execute(
                    'INSERT INTO passenger(full_name,email,phone,passport_no) VALUES (?,?,?,?)',
                    (name, email, phone, passport)
                )
                new_id = conn._lastrowid
                conn.commit()
                flash(f'Passenger added successfully. Passenger ID: {new_id}', 'success')

            elif action == 'delete':
                passenger_id = int(request.form.get('passenger_id', '0'))
                passenger = conn.execute(
                    'SELECT * FROM passenger WHERE passenger_id=?',
                    (passenger_id,)
                ).fetchone()

                if not passenger:
                    raise ValueError('Passenger not found.')

                # Keep referential integrity: passengers with bookings cannot
                # be deleted accidentally during the demo.
                booked = conn.execute(
                    'SELECT COUNT(*) FROM booking WHERE passenger_id=?',
                    (passenger_id,)
                ).fetchone()[0]

                if booked:
                    raise ValueError(
                        f"Cannot delete {passenger['full_name']}: "
                        f"the passenger has {booked} booking(s)."
                    )

                conn.execute(
                    'DELETE FROM passenger WHERE passenger_id=?',
                    (passenger_id,)
                )
                conn.commit()
                flash(
                    f"Passenger '{passenger['full_name']}' deleted successfully.",
                    'success'
                )

        passengers_rows = conn.execute(
            'SELECT passenger_id, full_name, email, phone, passport_no '
            'FROM passenger ORDER BY passenger_id DESC'
        ).fetchall()

        # Used only to explain why a delete may be blocked.
        booking_counts = conn.execute(
            'SELECT passenger_id, COUNT(*) AS booking_count '
            'FROM booking GROUP BY passenger_id'
        ).fetchall()
        booking_map = {r['passenger_id']: r['booking_count'] for r in booking_counts}

        return render_template(
            'passengers.html',
            passengers=passengers_rows,
            booking_map=booking_map
        )
    except Exception as e:
        conn.rollback()
        flash(str(e), 'error')
        passengers_rows = conn.execute(
            'SELECT passenger_id, full_name, email, phone, passport_no '
            'FROM passenger ORDER BY passenger_id DESC'
        ).fetchall()
        booking_counts = conn.execute(
            'SELECT passenger_id, COUNT(*) AS booking_count '
            'FROM booking GROUP BY passenger_id'
        ).fetchall()
        booking_map = {r['passenger_id']: r['booking_count'] for r in booking_counts}
        return render_template(
            'passengers.html',
            passengers=passengers_rows,
            booking_map=booking_map
        )
    finally:
        conn.close()

@app.route('/api/flight/<int:flight_id>/seats')
def seats_api(flight_id):
    conn=get_db(); rows=conn.execute('''SELECT s.seat_id,s.seat_number,s.seat_class,CASE WHEN EXISTS(SELECT 1 FROM ticket t JOIN booking b ON b.booking_id=t.booking_id WHERE t.seat_id=s.seat_id AND b.flight_id=? AND b.status='Confirmed') THEN 1 ELSE 0 END occupied FROM seat s JOIN flight f ON f.aircraft_id=s.aircraft_id WHERE f.flight_id=? ORDER BY s.seat_id''',(flight_id,flight_id)).fetchall(); conn.close(); return jsonify([dict(r) for r in rows])

@app.route('/health')
def health(): return jsonify({'status':'ok','database':os.path.basename(DB_PATH)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
