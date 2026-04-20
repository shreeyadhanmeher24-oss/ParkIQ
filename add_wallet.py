import sqlite3

conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN wallet REAL DEFAULT 500")
except:
    pass

conn.commit()
conn.close()

print("Wallet added ✅")