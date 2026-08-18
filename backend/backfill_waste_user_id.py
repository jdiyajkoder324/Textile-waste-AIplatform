"""
One-time fix: link existing waste_batches rows (user_id = NULL, created
before create_waste was wired to the authenticated user) to a specific
account, so they show up on the role dashboards (Manufacturer/Recycler/
Admin), which filter by user_id.

Run once: python backfill_waste_user_id.py
Then enter the email you log in with when prompted.
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Postgresql%40123@localhost:5432/textile_waste_db"

engine = create_engine(DATABASE_URL)

email = input("Email to link orphaned batches to: ").strip()

with engine.begin() as conn:
    user_row = conn.execute(
        text("SELECT id FROM users WHERE email = :email"), {"email": email}
    ).first()

    if not user_row:
        print(f"No user found with email '{email}'. Nothing changed.")
    else:
        user_id = user_row[0]
        result = conn.execute(
            text("UPDATE waste_batches SET user_id = :uid WHERE user_id IS NULL"),
            {"uid": user_id},
        )
        print(f"Linked {result.rowcount} orphaned batch(es) to user_id={user_id} ({email}).")