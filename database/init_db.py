import sqlite3

import razorpay

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS parking_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot TEXT,
    status TEXT
)
""")

slots = [
    ("A1", "Available"),
    ("A2", "Occupied"),
    ("A3", "Available"),
    ("B1", "Occupied"),
    ("B2", "Available"),
    ("B3", "Available")
]

cursor.executemany("INSERT INTO parking_slots (slot, status) VALUES (?, ?)", slots)

conn.commit()
conn.close()

print("Database Created Successfully")

client = razorpay.Client(auth=("rzp_test_SdKGlUxPjul9Ng", "NrDgM59WF8HE4rIVjHZOgJUG"))