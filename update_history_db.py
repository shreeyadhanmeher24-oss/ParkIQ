import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

# Add date column
try:
    cursor.execute("ALTER TABLE bookings ADD COLUMN date TEXT")
except:
    pass

# Add time column
try:
    cursor.execute("ALTER TABLE bookings ADD COLUMN time TEXT")
except:
    pass

conn.commit()
conn.close()

print("Bookings table updated!")