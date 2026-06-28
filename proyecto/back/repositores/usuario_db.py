from sqlmodel import select
from sqlalchemy.exc import IntegrityError

#from repositores.usuario_db import crear_usuario, obtener_todos_usuario, eliminar_usuario, modificar_usuario, obtener_usuario_dni
#FALTA HACER EN REPOSITORES 

from models.usuario import Usuario 
from database.database import get_session


def crear_usuario(usuario: Usuario): 
    with get_session() as session: 
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario

def obtener_todos_usuario(): 
    with get_session() as session: 
        statement = select(Usuario) 
        return session.exec(statement).all() 
    
#username es dni, nuestro modelo usa username como dni, por eso la pongo asi en la funcion de eliminar y modificar usuario.
def obtener_usuario_username(username: str): 
    with get_session() as session: 
        statement = select(Usuario).where(Usuario.username == username)
        return session.exec(statement).first() 

def eliminar_usuario(username: str): 
    with get_session() as session: 

        statement = select(Usuario).where(Usuario.username == username)
        usuario = session.exec(statement). first() 

        if not usuario: 
            return {"message":"Usuario no encontrado"} 
        
        session.delete(usuario)
        session.commit()
        return {"ok": True}
    
#esta funcion estaba sin terminar, no se si estara bien, hay que probarla
def modificar_usuario(username: str, usuario: Usuario): 
    with get_session() as session: 
        statement = select(Usuario).where(Usuario.username == username)
        usuario_db = session.exec(statement).first()
        if not usuario_db:
            return {"message":"Usuario no encontrado"}
        # o podria ser asi, nose:
        #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado") 
        update_data = usuario.model_dump(exclude_unset=True)
        usuario_db.sqlmodel_update(update_data)
        try: 
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError("El mail ya esta en uso por otro usuario")
        session.refresh(usuario_db)
        return usuario_db



