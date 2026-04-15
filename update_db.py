import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

# Create bookings table safely
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    slot_number TEXT,
    payment_id TEXT
)
""")

conn.commit()
conn.close()

print("Bookings table added successfully!")