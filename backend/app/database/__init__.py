"""
This file was empty before, which is why `from app.database import init_db`
in main.py was failing. It now re-exports everything main.py and the routes
need from the database package, and defines init_db().
"""
from app.database.base import Base
from app.database.session import engine, SessionLocal, get_db


def init_db():
    """Create all tables registered on Base. Safe to call multiple times."""
    # Import model modules so their classes are registered on Base.metadata
    # before create_all runs. Add new model modules here as they're created.
    import app.models  # noqa: F401 (existing User/Waste/Prediction/Recommendation)
    import app.models.textile_analysis  # noqa: F401 (new Milestone 2 models)

    Base.metadata.create_all(bind=engine)
