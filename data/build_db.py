"""Loads the four CSVs into a SQLite database (ecommerce.db) for SQL analysis."""
import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")
for name in ["customers", "products", "orders", "order_items"]:
    df = pd.read_csv(f"{name}.csv")
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"Loaded {name}: {len(df)} rows")
conn.close()
print("Database built: ecommerce.db")
