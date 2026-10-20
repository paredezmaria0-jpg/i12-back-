from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from models.usuario import Usuario
from database.database import get_session
from services.user_services import obtener_password_hash


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


def obtener_usuario_username(username: str):
    with get_session() as session:
        statement = select(Usuario).where(Usuario.username == username)
        return session.exec(statement).first()


def eliminar_usuario(username: str):
    with get_session() as session:

        statement = select(Usuario).where(Usuario.username == username)
        usuario = session.exec(statement).first()

        if not usuario:
            return {"message": "Usuario no encontrado"}

        session.delete(usuario)
        session.commit()

        return {"ok": True}


def modificar_usuario(username: str, datos):
    with get_session() as session:

        statement = select(Usuario).where(
            Usuario.username == username
        )

        usuario_db = session.exec(statement).first()

        if not usuario_db:
            return None

        update_data = datos.model_dump(
            exclude_unset=True,
            exclude={"new_password"}
        )

        # Modificar nombre, apellido, email, rol, etc.
        if update_data:
            usuario_db.sqlmodel_update(update_data)

        # Modificar contraseña
        if datos.new_password is not None:
            usuario_db.password_hashed = obtener_password_hash(
                datos.new_password
            )

        try:
            session.commit()

        except IntegrityError:
            session.rollback()

            raise ValueError(
                "El mail ya está en uso por otro usuario"
            )

        session.refresh(usuario_db)

        return usuario_db