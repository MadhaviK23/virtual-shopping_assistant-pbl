import sqlite3

conn = sqlite3.connect("shopping.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    name TEXT PRIMARY KEY,
    price REAL
)
""")

# sample products
cursor.execute("INSERT OR IGNORE INTO products VALUES ('apple', 40)")
cursor.execute("INSERT OR IGNORE INTO products VALUES ('banana', 20)")
cursor.execute("INSERT OR IGNORE INTO products VALUES ('bottle', 30)")
cursor.execute("INSERT OR IGNORE INTO products VALUES ('cup', 15)")

conn.commit()
conn.close()

print("Database created!")
