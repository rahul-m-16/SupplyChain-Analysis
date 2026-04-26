"""
Run this script FIRST if you see column errors.
It prints every real column name in your supplychain table
so you can verify what SQL Server actually stored.

Usage:  python check_columns.py
"""
import pyodbc

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=.\SQLEXPRESS;'
    'DATABASE=SupplyChain;'
    'Trusted_Connection=yes;'
)

conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()
cur.execute("SELECT TOP 0 * FROM supplychain")
print(f"\n{'#':<5} {'Real Column Name':<45} {'Normalised Key'}")
print("-" * 75)
import re
for i, d in enumerate(cur.description, 1):
    name = d[0]
    key  = re.sub(r'[^a-z0-9]', '', name.lower())
    print(f"{i:<5} {name:<45} {key}")
conn.close()
print("\nTotal columns:", i)
