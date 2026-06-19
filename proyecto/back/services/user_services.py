# crear obtener_password_hash, verificar_password, crear_token_acceso, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import EmailStr
from sqlmodel import Session, select
import bcrypt

from models.usuario import Usuario
from database.database import get_db


# --Creando  nuestros datos secretos-- 
SECRET_KEY = "Argentina" 
ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token") 

# Funciones de utilidad (seguridad y hash nativo)

def obtener_password_hash(password:str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt() 
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")  

def verificar_password(plain_password: str, hashed_password: str) -> bool: 
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )

def crear_token_acceso(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY, 
        algorithm=ALGORITHM
    )
    return encoded_jwt

# Dependencias de autenticacion 

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], 
        db: Annotated[Session, Depends(get_db)], 
) -> Usuario: 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="No se puedieron validar", 
        headers= {"WWW-Authenticate": "Bearer"}, 
    )
    try: 
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: 
            raise credentials_exception 
    except jwt.PyJWTError: 
        raise credentials_exception
    
    # Buscar usuario en la base de datos real
    statement = select(Usuario).where(Usuario.username == username)
    usuario = db.exec(statement).first()

    if usuario is None:
        raise credentials_exception
    if usuario.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )
    
    return usuario

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes aura suficiente. Te vigilo."
            )
        return current_user