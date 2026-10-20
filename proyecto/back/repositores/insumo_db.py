from sqlmodel import select
import re

from models.insumo import Insumo, InsumoUpdate
from database.database import get_session
from fastapi import HTTPException

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError



def registrar_insumos(datos):
    with get_session() as session:

        nombre = datos.nombre.strip()

        if not nombre:
            raise HTTPException(
                status_code=400,
                detail="El nombre es obligatorio."
            )

        if datos.cantidad < 1:
            raise HTTPException(
                status_code=400,
                detail="La cantidad debe ser mayor a cero."
            )

        # Buscar todos los insumos con ese nombre
        statement = select(Insumo).where(
            func.lower(func.trim(Insumo.nombre)) == nombre.lower()
        )

        existentes = session.exec(statement).all()

        # Calcular la última numeración
        ultima = 0

        for insumo in existentes:
            if insumo.numeracion is not None:
                if insumo.numeracion > ultima:
                    ultima = insumo.numeracion

        # El bibliotecario puede indicar una numeración
        if datos.numeracion is None:
            inicial = ultima + 1
        else:
            inicial = datos.numeracion

        if inicial < 1:
            raise HTTPException(
                status_code=400,
                detail="La numeración debe ser mayor a cero."
            )

        # Validar TODAS las numeraciones solicitadas
        ocupadas = {
            insumo.numeracion
            for insumo in existentes
        }

        for i in range(datos.cantidad):
            numero = inicial + i

            if numero in ocupadas:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Ya existe {nombre} Nº {numero}. "
                        "Elegí otra numeración inicial."
                    )
                )

        # Buscar último código INS-XXXX
        todos = session.exec(select(Insumo)).all()

        ultimo_codigo = 0

        for insumo in todos:
            match = re.match(
                r"^INS-(\d+)$",
                insumo.codigo or ""
            )

            if match:
                numero = int(match.group(1))
                if numero > ultimo_codigo:
                    ultimo_codigo = numero

        nuevos = []

        for i in range(datos.cantidad):

            nuevo = Insumo(
                codigo=f"INS-{ultimo_codigo + i + 1:04d}",
                nombre=nombre,
                numeracion=inicial + i,
                numero_inventario=datos.numero_inventario,
                ubicacion=datos.observacion or "",
                id_estado=1,
                activo=True
            )

            session.add(nuevo)
            nuevos.append(nuevo)

        try:
            session.commit()

        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se pudieron registrar los insumos. "
                    "Puede existir una numeración o código duplicado."
                )
            )

        for insumo in nuevos:
            session.refresh(insumo)

        return nuevos


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



def obtener_ultima_numeracion(nombre: str) -> int:
    with get_session() as session:
        insumos = session.exec(select(Insumo)).all()

        maximo = 0

        for insumo in insumos:
            if insumo.nombre.strip().lower() == nombre.strip().lower():
                if insumo.numeracion is not None:
                    if insumo.numeracion > maximo:
                        maximo = insumo.numeracion

        return maximo



def existe_numeracion(nombre: str, numeracion: int) -> bool:
    with get_session() as session:
        statement = select(Insumo)
        insumos = session.exec(statement).all()

        for insumo in insumos:
            if insumo.nombre.strip().lower() == nombre.strip().lower():
                if insumo.numeracion == numeracion:
                    return True

        return False