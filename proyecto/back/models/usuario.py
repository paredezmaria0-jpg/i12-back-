from typing import List, TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .prestamo import Prestamo


class Rol(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    usuarios: List["Usuario"] = Relationship(back_populates="rol")


class Usuario(SQLModel, table=True):
    
    
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    nombre: str
    apellido: str
   # role: str  | None = Field(default="basic")
    password_hashed: str  
    disabled: bool = Field(default=False)
    id_rol: int  | None = Field(foreign_key="rol.id")
    rol: Optional["Rol"] = Relationship(back_populates="usuarios")
    prestamos: List["Prestamo"] = Relationship(back_populates="usuario")

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"
    
class UserCreate(SQLModel):
    username: str
    email: str
    nombre: str
    apellido:str
    #id_rol: int
    password: str

class UserPublic(SQLModel):
    id: int
    username:str
    email:str
    nombre: str
    apellido:str
    id_rol: int | None
    disabled: bool

class UserUpdate(SQLModel):
    email:str | None = None
    nombre: str | None = None
    apellido: str | None = None
    id_rol: int | None = None


class PasswordUpdate(SQLModel):
    """Modelo estricto para la actualización de contraseña."""
    old_password: str  
    new_password: str  

    
