from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import insumos, usuario, prestamo

from sqlmodel import SQLModel, Session, select
from services.user_services import obtener_password_hash

from database.database import engine

from models.carrera import Carrera
from models.destinatario import Destinatario
from models.insumo import Insumo, EstadoInsumo
from models.usuario import Usuario, Rol
from models.prestamo import Prestamo, EstadoPrestamo

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(insumos.router)
app.include_router(usuario.router)
app.include_router(prestamo.router)

@app.get("/")
async def root():
    return{"message": "Estamos con Argentina"}


def crear_bd():
    print(SQLModel.metadata.tables.keys())
    SQLModel.metadata.create_all(engine)

def cargar_usuario_admin():
    with Session(engine) as session:

        usuario_existente = session.exec(
            select(Usuario).where(Usuario.username == "admin")
        ).first()

        if usuario_existente:
            print("El usuario admin ya existe.")
            return

        usuario_admin = Usuario(
            username="admin",
            email="admin@example.com",
            nombre="Admin",
            apellido="",
            password_hashed=obtener_password_hash("1234"),
            disabled=False
        )

        session.add(usuario_admin)
        session.commit()
        session.refresh(usuario_admin)

        print("Usuario admin creado correctamente.")

crear_bd()

#cargar_usuario_admin()