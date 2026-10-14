from sqlmodel import select
import re

from models.insumo import Insumo, InsumoUpdate
from database.database import get_session
from fastapi import HTTPException


def crear_insumo(insumo: Insumo):
    with get_session() as session:
        session.add(insumo)
        session.commit()
        session.refresh(insumo)
        return insumo


def crear_insumos(insumos: list[Insumo]):
    with get_session() as session:
        for insumo in insumos:
            session.add(insumo)

        session.commit()

        for insumo in insumos:
            session.refresh(insumo)

        return insumos


def obtener_todos_insumos():
    with get_session() as session:
        statement = select(Insumo).order_by(
            Insumo.activo.desc(),
            Insumo.id.asc()
        )

        return session.exec(statement).all()


def obtener_insumo_id(id: int):
    with get_session() as session:
        statement = select(Insumo).where(Insumo.id == id)
        return session.exec(statement).first()


def eliminar_insumo(id: int):
    with get_session() as session:
        insumo = session.get(Insumo, id)

        if insumo is None:
            return {"ok": False, "motivo": "no_encontrado"}

        if not insumo.activo:
            return {"ok": False, "motivo": "ya_inhabilitado"}

        if insumo.id_estado == 3:
            return {"ok": False, "motivo": "prestado"}

        # Baja lógica: NO eliminar de la base de datos
        insumo.activo = False

        session.add(insumo)
        session.commit()

        return {"ok": True}




def modificar_insumo(insumo_update: InsumoUpdate, insumo_db: Insumo):
    with get_session() as session:
        insumo = session.get(Insumo, insumo_db.id)

        if insumo is None:
            raise HTTPException(
                status_code=404,
                detail="El insumo no existe."
            )

        if not insumo.activo:
            raise HTTPException(
                status_code=403,
                detail="El insumo está inhabilitado y no puede modificarse."
            )

        update_data = insumo_update.model_dump(exclude_unset=True)

        # Evitar modificaciones de habilitación desde edición normal
        update_data.pop("activo", None)

        insumo.sqlmodel_update(update_data)

        session.add(insumo)
        session.commit()
        session.refresh(insumo)

        return insumo


def obtener_ultimo_codigo() -> int:
    with get_session() as session:
        statement = select(Insumo)
        insumos = session.exec(statement).all()

        maximo = 0

        for insumo in insumos:
            match = re.match(r"^INS-(\d+)$", insumo.codigo or "")

            if match:
                numero = int(match.group(1))

                if numero > maximo:
                    maximo = numero

        return maximo


def obtener_ultima_numeracion() -> int:
    with get_session() as session:
        statement = select(Insumo)
        insumos = session.exec(statement).all()

        numeraciones = [
            insumo.numeracion
            for insumo in insumos
            if insumo.numeracion is not None
        ]

        return max(numeraciones) if numeraciones else 0


def existe_numeracion(nombre: str, numeracion: int) -> bool:
    with get_session() as session:
        statement = select(Insumo).where(
            Insumo.nombre == nombre,
            Insumo.numeracion == numeracion
        )

        return session.exec(statement).first() is not None