import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# Create parking slots table
cursor.execute("""
CREATE TABLE IF NOT EXISTS parking_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_number TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    slot_number TEXT,
    payment_id TEXT
)
""")

# Clear old slots
cursor.execute("DELETE FROM parking_slots")

# Insert fresh slots
slots = [
    ("A1", "Available"),
    ("A2", "Available"),
    ("A3", "Available"),
    ("B1", "Available"),
    ("B2", "Available"),
    ("B3", "Available")
]

cursor.executemany(
    "INSERT INTO parking_slots (slot_number, status) VALUES (?, ?)",
    slots
)

conn.commit()
conn.close()

print("Database created successfully!")