"""
Database connection setup.
Works with PostgreSQL (production) or SQLite (quick local start, no setup needed).

Set DATABASE_URL in .env, e.g.:
  Postgres: postgresql+psycopg2://complaint_user:complaint_pass@localhost:5432/complaint_db
  SQLite (zero setup):  sqlite:///./complaints.db
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load backend/.env explicitly by path, so this works no matter which
# directory uvicorn/python is launched from.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./complaints.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
