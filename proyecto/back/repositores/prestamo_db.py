from sqlmodel import select 

from models.prestamo import Prestamo, EstadoPrestamo
from models.destinatario import Destinatario
from database.database import get_session
from models.insumo import Insumo
#obtener_todos_prestamos, eliminar_prestamo, obtener_prestamo_id, obtener_prestamo_usuario, obtener_todos_prestamos_morosos

def crear_prestamo(prestamo: Prestamo):
    with get_session() as session:
        session.add(prestamo)
        session.commit()
        session.refresh(prestamo)
        return prestamo
    
def obtener_todos_prestamos(): 
    with get_session() as session: 
        statement = select(Prestamo)
        return session.exec(statement).all() 
    
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
