#!/usr/bin/env python3
import sqlite3

# Read the SQL file
with open('sample_data.sql', 'r') as f:
    sql_script = f.read()

# Create the database and execute the script
conn = sqlite3.connect('sample.db')
cursor = conn.cursor()

# Execute the entire script
cursor.executescript(sql_script)

conn.commit()

# Verify the database was created
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Created database with tables:")
for table in tables:
    print(f"  - {table[0]}")

# Show some stats
cursor.execute("SELECT COUNT(*) FROM employees")
print(f"\nEmployees: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM products")
print(f"Products: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM orders")
print(f"Orders: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM order_items")
print(f"Order items: {cursor.fetchone()[0]}")

conn.close()
print("\nDatabase 'sample.db' created successfully!")
