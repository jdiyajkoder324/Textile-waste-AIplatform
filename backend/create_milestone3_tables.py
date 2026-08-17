r"""
create_milestone3_tables.py

Run this ONCE from the backend/ folder (venv activated) to create the five
new Milestone 3 tables in PostgreSQL:

    sustainability_metrics
    environmental_impact
    waste_scores
    circularity_analysis
    recommendation_reports

Usage (from backend/ directory):

    .\venv\Scripts\Activate.ps1
    python create_milestone3_tables.py

This mirrors the pattern used for the Milestone 1 migration script --
it does NOT touch existing tables, it only creates the new ones (checkfirst
protects against re-running it accidentally).
"""

from app.database.base import Base
from app.database.session import engine  # if this fails, check session.py for the actual engine variable name
# Importing the models module registers the tables on Base.metadata
import app.models.sustainability_models  # noqa: F401


def run_migration():
    print("Creating Milestone 3 tables (if they do not already exist)...")
    Base.metadata.create_all(
        bind=engine,
        tables=[
            Base.metadata.tables["sustainability_metrics"],
            Base.metadata.tables["environmental_impact"],
            Base.metadata.tables["waste_scores"],
            Base.metadata.tables["circularity_analysis"],
            Base.metadata.tables["recommendation_reports"],
        ],
        checkfirst=True,
    )
    print("Done. Tables created (or already existed):")
    print(" - sustainability_metrics")
    print(" - environmental_impact")
    print(" - waste_scores")
    print(" - circularity_analysis")
    print(" - recommendation_reports")


if __name__ == "__main__":
    run_migration()
