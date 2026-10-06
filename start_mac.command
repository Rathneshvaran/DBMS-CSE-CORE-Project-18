#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=============================================="
echo " Airline Reservation - MySQL Setup"
echo "=============================================="

python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  echo
  read -s -p "Enter your MySQL root password: " MYSQL_PASSWORD
  echo
  cat > .env <<ENV
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_DATABASE=airline_reservation
FLASK_SECRET_KEY=airline-review3-demo-secret
ENV
  chmod 600 .env
fi

echo
python run.py
