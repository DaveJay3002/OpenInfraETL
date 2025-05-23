import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from db.models import Base

load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init():
    Base.metadata.drop_all(engine)  # Optional: clear existing tables for fresh start
    Base.metadata.create_all(engine)
    print("[✅] Tables created")


if __name__ == "__main__":
    init()
