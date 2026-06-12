from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL

# SQLAlchemy uses the psycopg (v3) dialect when the URL scheme is postgresql+psycopg
_db_url = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(_db_url, echo=False)


def create_db_tables() -> None:
    SQLModel.metadata.create_all(engine)
