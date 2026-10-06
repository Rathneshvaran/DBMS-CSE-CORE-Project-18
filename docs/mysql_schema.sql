-- MySQL 8.x adaptation guide
CREATE DATABASE IF NOT EXISTS airline_db;
USE airline_db;
-- The Flask application uses SQLite for zero-configuration execution.
-- This file documents the principal DDL mapping for a MySQL deployment.
-- Replace INTEGER PRIMARY KEY AUTOINCREMENT with INT AUTO_INCREMENT PRIMARY KEY.
-- Replace TEXT with VARCHAR/TEXT as appropriate; CURRENT_TIMESTAMP is supported.
-- Apply the same PK, FK, UNIQUE and CHECK constraints shown in app.py.
