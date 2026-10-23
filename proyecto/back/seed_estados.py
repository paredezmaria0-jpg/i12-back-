from sqlmodel import SQLModel, Session

from database.database import engine

# Registrar todos los modelos.
from models.carrera import Carrera
from models.destinatario import Destinatario
from models.insumo import Insumo, EstadoInsumo
from models.usuario import Usuario, Rol
from models.prestamo import Prestamo, EstadoPrestamo


def cargar_datos_iniciales():
    with Session(engine) as session:

        estados_insumo = [
            (1, "Disponible", "Disponible para préstamo"),
            (2, "No Disponible", "No disponible para préstamo"),
            (3, "Prestado", "Entregado en préstamo")
        ]

        for identificador, nombre, observacion in estados_insumo:
            existente = session.get(
                EstadoInsumo,
                identificador
            )

            if existente is None:
                session.add(
                    EstadoInsumo(
                        id=identificador,
                        nombre=nombre,
                        observacion=observacion
                    )
                )

            elif existente.nombre != nombre:
                raise ValueError(
                    f"EstadoInsumo {identificador}: "
                    f"se esperaba '{nombre}' y existe "
                    f"'{existente.nombre}'."
                )

        estados_prestamo = [
            (1, "Activo"),
            (2, "Moroso"),
            (3, "Devuelto")
        ]

        for identificador, nombre in estados_prestamo:
            existente = session.get(
                EstadoPrestamo,
                identificador
            )

            if existente is None:
                session.add(
                    EstadoPrestamo(
                        id=identificador,
                        nombre=nombre
                    )
                )

            elif existente.nombre != nombre:
                raise ValueError(
                    f"EstadoPrestamo {identificador}: "
                    f"se esperaba '{nombre}' y existe "
                    f"'{existente.nombre}'."
                )

        roles = [
            (1, "Administrador"),
            (2, "Bibliotecario"),
            (3, "Secretario")
        ]

        for identificador, nombre in roles:
            existente = session.get(
                Rol,
                identificador
            )

            if existente is None:
                session.add(
                    Rol(
                        id=identificador,
                        nombre=nombre
                    )
                )

            elif existente.nombre != nombre:
                raise ValueError(
                    f"Rol {identificador}: "
                    f"se esperaba '{nombre}' y existe "
                    f"'{existente.nombre}'."
                )

        session.commit()

    print("Estados y roles inicializados.")


if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
    cargar_datos_iniciales()