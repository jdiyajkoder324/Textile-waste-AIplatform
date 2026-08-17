"""
One-time migration: adds the new Inventory columns to the existing
waste_batches table in Postgres, without touching existing rows/data.

Run this ONCE from your backend/ folder (same place you run main.py from):

    python migrate_add_inventory_columns.py

Safe to run more than once — uses IF NOT EXISTS so it won't error out
if a column is already there.
"""

from sqlalchemy import text
from app.database.session import engine

STATEMENTS = [
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);",
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS title VARCHAR;",
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS description TEXT;",
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS material VARCHAR;",
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS color VARCHAR;",
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS location VARCHAR;",
    "ALTER TABLE waste_batches ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;",
]

def run_migration():
    with engine.begin() as conn:
        for stmt in STATEMENTS:
            print(f"Running: {stmt}")
            conn.execute(text(stmt))
    print("\n✅ Migration complete. waste_batches table is now up to date.")

if __name__ == "__main__":
    run_migration()