from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .carrera import Carrera
    from .prestamo import Prestamo

class Destinatario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=20)
    apellido: str = Field(max_length=20)
    dni: str = Field(index=True, unique=True)
    telefono: str = Field(max_length=15)
    correo: str = Field(max_length=20)

    id_carrera: int = Field(foreign_key="carrera.id")

    carrera: Optional["Carrera"] = Relationship(
    back_populates="destinatarios")

    prestamos: list["Prestamo"] = Relationship(
        back_populates="destinatario")