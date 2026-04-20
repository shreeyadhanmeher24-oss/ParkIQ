import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN pass_expiry TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN vehicle_number TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN vehicle_type TEXT")
except:
    pass

conn.commit()
conn.close()

print("Subscription fields added ✅")