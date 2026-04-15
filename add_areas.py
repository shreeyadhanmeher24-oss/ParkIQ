import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS parking_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_name TEXT,
    total_slots INTEGER,
    available_slots INTEGER
)
""")

cursor.execute("DELETE FROM parking_areas")

areas = [
    ("Andheri West", 20, 8),
    ("Bandra", 15, 5),
    ("Powai", 25, 12),
    ("Dadar", 18, 7),
    ("Thane", 30, 15)
]

cursor.executemany(
    "INSERT INTO parking_areas (area_name, total_slots, available_slots) VALUES (?, ?, ?)",
    areas
)

conn.commit()
conn.close()

print("Parking areas added successfully!")