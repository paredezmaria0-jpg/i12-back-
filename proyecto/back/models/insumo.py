from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index, func

if TYPE_CHECKING:
    from .prestamo import Prestamo


class EstadoInsumo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=20)
    observacion: str = Field(max_length=50)

    insumos: list["Insumo"] = Relationship(
        back_populates="estado"
    )


class Insumo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, max_length=10, index=True)
    numero_inventario: str | None = Field(max_length=10)
    numeracion: int | None = Field(default=None)
    nombre: str = Field(max_length=50)
    ubicacion: str = Field(max_length=50)

    id_estado: int = Field(foreign_key="estadoinsumo.id")
    activo: bool = Field(default=True)

    estado: Optional["EstadoInsumo"] = Relationship(
        back_populates="insumos"
    )

    prestamos: list["Prestamo"] = Relationship(
        back_populates="insumo"
    )

    def nombre_completo(self) -> str:
        return f"{self.codigo} {self.nombre}"

Index(
    "uq_insumo_nombre_numeracion_activo",
    func.lower(func.trim(Insumo.__table__.c.nombre)),
    Insumo.__table__.c.numeracion,
    unique=True,
    sqlite_where=Insumo.__table__.c.activo == True
)

class InsumoUpdate(SQLModel):
    nombre: str | None = None
    numero_inventario: str | None = None
    numeracion: int | None = None
    ubicacion: str | None = None
    id_estado: int | None = None


class InsumoAlta(SQLModel):
    nombre: str
    numero_inventario: str
    cantidad: int
    numeracion: int | None = None
    observacion: str | None = None