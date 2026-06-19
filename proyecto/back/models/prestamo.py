from typing import List, TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import date

if TYPE_CHECKING:
    from .destinatario import Destinatario
    from .insumo import Insumo
    from .usuario import Usuario


class EstadoPrestamo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    prestamos: List["Prestamo"] = Relationship(back_populates="estadoPrestamo")


class Prestamo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha_entrega: date
    fecha_devolucion: date
    obs: str = Field(max_length=70)
    id_estadoPrestamo: int | None = Field(default=None, foreign_key="estadoprestamo.id")
    id_destinatario: int | None = Field(default=None, foreign_key="destinatario.id")
    id_insumo: int | None = Field(default=None, foreign_key="insumo.id")
    id_usuario: int | None = Field(default=None, foreign_key="usuario.id")
    estadoPrestamo: Optional["EstadoPrestamo"] = Relationship(back_populates="prestamos")
    destinatario: Optional["Destinatario"] = Relationship(back_populates="prestamos")
    insumo: Optional["Insumo"] = Relationship(back_populates="prestamos")
    usuario: Optional["Usuario"] = Relationship(back_populates="prestamos")
