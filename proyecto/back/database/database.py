from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "sqlite:///biblioteca.db"

engine = create_engine(DATABASE_URL, echo= True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)

def get_db() -> Generator[Session, None, None]:
    """Dependencia para obtener la sesion de la base de datos."""
    with Session(engine) as session:
        yield session