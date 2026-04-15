import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

cursor.execute("UPDATE parking_slots SET status='Available'")

conn.commit()
conn.close()

print("All parking slots are now available!")