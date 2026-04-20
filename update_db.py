import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

# ---------------- USERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    wallet INTEGER DEFAULT 0,
    pass_expiry TEXT,
    vehicle_number TEXT,
    vehicle_type TEXT
)
""")

# ---------------- BOOKINGS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    slot_number TEXT,
    payment_id TEXT,
    date TEXT,
    time TEXT
)
""")

# ---------------- SAFE COLUMN ADD (IF ALREADY EXISTS) ----------------
try:
    cursor.execute("ALTER TABLE users ADD COLUMN wallet INTEGER DEFAULT 0")
except:
    pass

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

try:
    cursor.execute("ALTER TABLE bookings ADD COLUMN date TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE bookings ADD COLUMN time TEXT")
except:
    pass

conn.commit()
conn.close()

print("Database fully updated ✅")