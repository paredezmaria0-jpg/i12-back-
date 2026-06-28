from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta

# Importa tus modelos y configuración desde su ubicación real
from models.usuario import Usuario, UserCreate, UserPublic, UserUpdate, PasswordUpdate
from repositores.usuario_db import crear_usuario, obtener_todos_usuario, eliminar_usuario, modificar_usuario, obtener_usuario_username

from database.database import get_db

#FALTA HACER EL SERVICE
from services.user_services import (
    obtener_password_hash,
    verificar_password,
    crear_token_acceso,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["Users"])

# End points publicos (sin autorizacion)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    usuario_in: UserCreate,
    db: Annotated[Session, Depends(get_db)]
):
    #verificar que el username no exista
    statement_username = select(Usuario).where(Usuario.username == usuario_in.username)
    if db.exec(statement_username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya esta registrado",
        )
    #validar el gmail
    statement_email = select(Usuario).where(Usuario.email == usuario_in.email)
    if db.exec(statement_email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El gmail ya esta registrado",
        )
    
    # Encriptar el nuevo usuario
    nuevo_user = Usuario(
        username = usuario_in.username,
        email= usuario_in.email,
        nombre= usuario_in.nombre,
        apellido=usuario_in.apellido,
        password_hashed=obtener_password_hash(usuario_in.password),
        disabled=False,
    )
    db.add(nuevo_user)
    db.commit()
    db.refresh(nuevo_user)
    
    return {"mensaje" : "usuario registrado"}

@router.post("/token")
async def login_para_obtener_token(
    form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    #Endpoint para autenticarse e intercambiar credenciales por un JWT.
    statement = select(Usuario).where(Usuario.username == form_data.username)
    user = db.exec(statement).first()
    
    if not user or not verificar_password(form_data.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasenia incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_token_acceso(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token,
            "token_type":"bearer"
    }

    #JWT (Json Web Token) contiene informacion codificada

# ----- Ver datos

@router.get("/me", response_model=UserPublic) 
async def obtener_mi_datos(
    current_user: Annotated[Usuario, Depends(get_current_user)] 
): 
    return current_user


# ---- Modificar datos

@router.put("/me", response_model=UserPublic)
async def modificar_mi_datos(
    datos: UserUpdate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
): 
    if datos.nombre is not None:
        current_user.nombre = datos.nombre
    
    if datos.apellido is not None:
        current_user.apellido = datos.apellido
    
    if datos.email is not None:
        current_user.email = datos.email

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user 

# ---- Cambiar contraseña 

@router.put("/change-password") 
async def cambiar_password( 
    datos: PasswordUpdate, 
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
): 
    if not verificar_password(
        datos.old_password,
        current_user.password_hashed,
    ): 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La contraseña actual es incorrecta", 
        )
        
    current_user.password_hashed = (obtener_password_hash(
        datos.new_password))  
    
    db.add(current_user)
    db.commit() 

    return {"mensaje": "Contraseña actualizada correctamente"} 

# ----- Administración de usuarios

@router.get("/", response_model=list[UserPublic])
async def obtener_usuarios(
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    return obtener_todos_usuario()


@router.get("/{username}", response_model=UserPublic)
async def obtener_usuario(
    username: str,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    usuario = obtener_usuario_username(username)
    if usuario:
        return usuario
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )


@router.put("/{username}", response_model=UserPublic)
async def modificar_usuario_admin(
    username: str,
    datos: UserUpdate,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    try:
        usuario = modificar_usuario(username, datos)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if usuario:
        return usuario
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado",
    )


@router.delete("/{username}")
async def eliminar_usuario_admin(
    username: str,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    return eliminar_usuario(username)