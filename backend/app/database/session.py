from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Postgresql%40123@localhost:5432/textile_waste_db")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():

    db=SessionLocal()

    try:
        yield db

    finally:
        db.close()