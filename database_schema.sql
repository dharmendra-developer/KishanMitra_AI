CREATE TABLE users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 email TEXT UNIQUE NOT NULL,
 password_hash TEXT NOT NULL,
 location TEXT,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE recommendations (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL,
 nitrogen REAL, phosphorus REAL, potassium REAL,
 temperature REAL, humidity REAL, ph REAL, rainfall REAL,
 crop TEXT, irrigation TEXT, fertilizer TEXT,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(id)
);
