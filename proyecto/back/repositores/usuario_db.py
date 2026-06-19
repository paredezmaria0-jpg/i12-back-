from sqlmodel import select

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
    

def obtener_usuario_dni(dni: str): 
    with get_session() as session: 
        statement = select(Usuario).where(Usuario.dni == dni)
        return session.exec(statement).first() 

def eliminar_usuario(dni: str): 
    with get_session() as session: 

        statement = select(Usuario).where(Usuario.dni == dni)
        usuario = session.exec(statement). first() 

        if not usuario: 
            return {"message":"Usuario no encontrado"} 
        
        session.delete(usuario)
        session.commit()
        return {"ok": True}
    
def modificar_usuario(dni: str, usuario: Usuario): 
    with get_session() as session: 
        statement = select(Usuario).where(Usuario.dni == dni)

