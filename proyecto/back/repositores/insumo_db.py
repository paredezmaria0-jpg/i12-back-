from sqlmodel import select 

from models.insumo import Insumo, InsumoUpdate
from database.database import get_session

#crear_insumo, obtener_todos_insumos, eliminar_insumo, modificar_insumo, obtener_insumo_id

def crear_insumo(insumo: Insumo): 
    with get_session() as session:
        session.add(insumo)
        session.commit()
        session.refresh(insumo)
        return insumo 
    
def obtener_todos_insumos(): 
    with get_session() as session: 
        statement = select(Insumo)
        return session.exec(statement).all() 
    
def obtener_insumo_id(id: int): 
    with get_session() as session:
        statement = select(Insumo).where(Insumo.id == id)
        return session.exec(statement).first()

def eliminar_insumo(id: int):
    insumo = obtener_insumo_id(id)
    with get_session() as session:
        session.delete(insumo)
        session.commit()
        #session.refresh(insumo) -->porque no se puede refrescar algo que ya eliminamos.
        return {"ok": True} 

def modificar_insumo(insumo_update: InsumoUpdate, insumo_db: Insumo): 
    #pass 
    #terminar despues 
    with get_session() as session: 
        update_data = insumo_update.model_dump(exclude_unset=True)
        insumo_db.sqlmodel_update(update_data)
        session.add(insumo_db)
        session.commit() 
        session.refresh(insumo_db) 

        return insumo_db 


