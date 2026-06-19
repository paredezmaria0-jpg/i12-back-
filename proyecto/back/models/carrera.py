from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .destinatario import Destinatario


class Carrera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

    destinatarios: list["Destinatario"] = Relationship(
        back_populates="carrera"
    )