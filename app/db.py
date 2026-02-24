from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

raw_url = os.getenv("DATABASE_URL")
if not raw_url or not raw_url.strip():
    raise ValueError("DATABASE_URL is empty. Set it in your .env file.")

engine = create_engine(raw_url.strip())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from models import *

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    raise RuntimeError(f"Failed to create tables: {exc}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
