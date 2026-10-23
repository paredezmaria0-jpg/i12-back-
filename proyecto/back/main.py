import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select

from database.database import engine
from services.user_services import obtener_password_hash

from models.carrera import Carrera
from models.destinatario import Destinatario
from models.insumo import Insumo, EstadoInsumo
from models.usuario import Usuario, Rol
from models.prestamo import Prestamo, EstadoPrestamo

from routes import insumos, usuario, prestamo
from seed_estados import cargar_datos_iniciales


def cargar_usuario_admin():
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD")

    with Session(engine) as session:
        existente = session.exec(
            select(Usuario).where(
                Usuario.username == username
            )
        ).first()

        if existente:
            print("El administrador ya existe.")
            return

        if not password:
            print(
                "No se creó el administrador: "
                "falta configurar ADMIN_PASSWORD."
            )
            return

        administrador = Usuario(
            username=username,
            email="admin@example.com",
            nombre="Administrador",
            apellido="Demo",
            password_hashed=obtener_password_hash(password),
            disabled=False,
            id_rol=1
        )

        session.add(administrador)
        session.commit()

    print("Administrador de la demo creado.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    cargar_datos_iniciales()
    cargar_usuario_admin()

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rainbow-creponne-a6f7ba.netlify.app",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(insumos.router)
app.include_router(usuario.router)
app.include_router(prestamo.router)


@app.get("/")
async def root():
    return {
        "message": "API de Biblioteca ISFT Nº 12",
        "modo": "demo"
    }