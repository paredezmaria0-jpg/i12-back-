from sqlmodel import select 

from models.prestamo import Prestamo, EstadoPrestamo
from models.destinatario import Destinatario
from database.database import get_session
from models.insumo import Insumo
from datetime import datetime, date

#obtener_todos_prestamos, eliminar_prestamo, obtener_prestamo_id, obtener_prestamo_usuario, obtener_todos_prestamos_morosos

#crear prestamo y cambiar el estado del insumo a "Activo" (prestado)

def crear_prestamo(prestamo: Prestamo):
    with get_session() as session:
        insumo = session.get(Insumo, prestamo.id_insumo)

        if insumo is None:
            raise ValueError("El insumo no existe")

        # Convertir fecha_entrega de string a Python date object si es necesario
        if isinstance(prestamo.fecha_entrega, str):
            prestamo.fecha_entrega = datetime.strptime(prestamo.fecha_entrega, "%Y-%m-%d").date()

        # El insumo pasa a "Prestado" (id_estado = 3)
        insumo.id_estado = 3

        # El préstamo comienza como "Activo" (id_estadoPrestamo = 1)
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
            estado = session.get(EstadoPrestamo, prestamo.id_estadoPrestamo)

            datos = {
                "idTransaccion": prestamo.id,
                "codigoInsumo": insumo.codigo if insumo else "",
                "insumo": insumo.nombre if insumo else "",
                "destinatario": prestamo.id_destinatario,
                "fecha": str(prestamo.fecha_entrega),
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

def modificar_prestamo(prestamo_update: Prestamo, prestamo_db: Prestamo): 
    #pass 
    #terminar despues 
    with get_session() as session: 
        update_data = prestamo_update.model_dump(exclude_unset=True)
        prestamo_db.sqlmodel_update(update_data)
        session.add(prestamo_db)
        session.commit() 
        session.refresh(prestamo_db) 

        return prestamo_db 
