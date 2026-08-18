from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Postgresql%40123@localhost:5432/textile_waste_db"

COLUMNS_TO_RELAX = ["source", "collection_date", "batch_id", "user_id"]

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    for col in COLUMNS_TO_RELAX:
        print(f"Dropping NOT NULL on waste_batches.{col} (if present)...")
        conn.execute(text(f"ALTER TABLE waste_batches ALTER COLUMN {col} DROP NOT NULL;"))

print("Done.")
