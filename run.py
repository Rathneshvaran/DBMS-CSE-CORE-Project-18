from app import init_db, app
init_db()
print('\nAirline Reservation System is ready!')
print('Open: http://127.0.0.1:5000\n')
app.run(debug=True, host='127.0.0.1', port=5000)
