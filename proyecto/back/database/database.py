import os
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

# En tu PC conserva biblioteca.db.
# En Render configuraremos otro archivo para la demo.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///biblioteca.db"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session