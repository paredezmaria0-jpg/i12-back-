from sqlmodel import select 

from models.prestamo import Prestamo, EstadoPrestamo, PrestamoUpdate
from models.destinatario import Destinatario
from database.database import get_session
from models.insumo import Insumo
from datetime import datetime, date
from fastapi import HTTPException
from zoneinfo import ZoneInfo


#obtener_todos_prestamos, eliminar_prestamo, obtener_prestamo_id, obtener_prestamo_usuario, obtener_todos_prestamos_morosos

#crear prestamo y cambiar el estado del insumo a "Activo" (prestado)

def crear_prestamo(prestamo: Prestamo):

    with get_session() as session:

        insumo = session.get(Insumo, prestamo.id_insumo)

        if insumo is None:
            raise ValueError("El insumo no existe.")

        if not insumo.activo:
            raise ValueError("No se puede prestar un insumo inhabilitado.")

        if insumo.id_estado != 1:
            raise ValueError("El insumo no está disponible para préstamo.")

        if isinstance(prestamo.fecha_entrega, str):
            prestamo.fecha_entrega = datetime.strptime(
                prestamo.fecha_entrega,
                "%Y-%m-%d"
            ).date()

        # El insumo pasa a Prestado
        insumo.id_estado = 3

        # El préstamo comienza como Activo
        prestamo.id_estadoPrestamo = 1

        session.add(insumo)
        session.add(prestamo)

        session.commit()
        session.refresh(prestamo)

        return prestamo
    
def obtener_todos_prestamos():

    with get_session() as session:

        prestamos = session.exec(
            select(Prestamo)
        ).all()

        activos = []
        morosos = []
        devueltos = []

        for prestamo in prestamos:

            insumo = session.get(Insumo, prestamo.id_insumo)
            estado = session.get(
                EstadoPrestamo,
                prestamo.id_estadoPrestamo
            )

            datos = {
                "idTransaccion": prestamo.id,

                # DATOS DEL INSUMO
                "codigoInsumo": insumo.codigo if insumo else "",
                "insumo": insumo.nombre if insumo else "",
                "numeracion": insumo.numeracion if insumo else None,

                # DATOS DEL DESTINATARIO
                "destinatario": prestamo.id_destinatario,
                "tipo_destinatario": prestamo.tipo_destinatario,

                # DATOS ACADÉMICOS
                "carrera": prestamo.carrera,
                "anio": prestamo.anio,
                "curso": prestamo.curso,
                "a_cargo": prestamo.a_cargo,

                # DATOS DEL PRÉSTAMO
                "fecha": str(prestamo.fecha_entrega),

                "fecha_devolucion": (
                    str(prestamo.fecha_devolucion)
                    if prestamo.fecha_devolucion is not None
                    else None
                ),

                "observacion": prestamo.obs,
                "estado": estado.nombre if estado else ""
            }

            if estado and estado.nombre == "Activo":
                activos.append(datos)

            elif estado and estado.nombre == "Moroso":
                morosos.append(datos)

            elif estado and estado.nombre == "Devuelto":
                devueltos.append(datos)

        return {
            "activos": activos,
            "morosos": morosos,
            "devueltos": devueltos
        }
    
def obtener_prestamo_id(id: int): 
    with get_session() as session:
        statement = select(Prestamo).where(Prestamo.id == id)
        return session.exec(statement).first()
    
def obtener_prestamo_destinatario(nom_destinatario: str):
    with get_session() as session:
        statement = (
            select(Prestamo)
            .join(Destinatario)
            .where(Destinatario.nombre == nom_destinatario)
        )
        return session.exec(statement).all()

def obtener_todos_prestamos_morosos():
    with get_session() as session:
        statement = (
            select(Prestamo)
            .join(EstadoPrestamo)
            .where(EstadoPrestamo.nombre == "Moroso")
        )
        return session.exec(statement).all()

def eliminar_prestamo(id: int):
    prestamo = obtener_prestamo_id(id)
    with get_session() as session:
        session.delete(prestamo)
        session.commit()
        #session.refresh(prestamo) creo que noo, porque no se puede refrescar algo que ya eliminamos.
        return {"ok": True} 

def modificar_prestamo(
    prestamo_update: PrestamoUpdate,
    prestamo_db: Prestamo
):
    with get_session() as session:

        prestamo = session.get(Prestamo, prestamo_db.id)

        if prestamo is None:
            raise HTTPException(
                status_code=404,
                detail="El préstamo no existe."
            )

        update_data = prestamo_update.model_dump(
            exclude_unset=True
        )

        if "fecha_entrega" in update_data:
            if update_data["fecha_entrega"] is None:
                raise HTTPException(
                    status_code=422,
                    detail="La fecha del préstamo es obligatoria."
                )

        if "obs" in update_data:
            update_data["obs"] = update_data["obs"] or ""

        prestamo.sqlmodel_update(update_data)

        session.add(prestamo)
        session.commit()
        session.refresh(prestamo)

        return prestamo
