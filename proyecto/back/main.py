from fastapi import FastAPI
from routes import insumos, usuario, prestamo

from sqlmodel import SQLModel, Session

from database.database import engine

from models.carrera import Carrera
from models.destinatario import Destinatario
from models.insumo import Insumo, EstadoInsumo
from models.usuario import Usuario, Rol
from models.prestamo import Prestamo, EstadoPrestamo

app = FastAPI() 
#instancia de la clase de FastApi (esto nos va a dar todas las funcionalidades)

app.include_router(insumos.router)
app.include_router(usuario.router)
app.include_router(prestamo.router)

@app.get("/")
async def root():
    return{"message": "Estamos con Argentina"}


def crear_bd():
    SQLModel.metadata.create_all(engine)

def cargar_datos_prueba():
    with Session(engine) as session:

        
        rol = Rol(nombre="Administrador")
        session.add(rol)
        session.commit()
        session.refresh(rol)  # para obtener el id generado

        
        usuario = Usuario(
            nombre="Paula",
            apellido="García",
            dni="12345678",
            clave="1234",
            id_rol=rol.id
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        
        carrera = Carrera(nombre="Informática")
        session.add(carrera)
        session.commit()
        session.refresh(carrera)

    
        destinatario = Destinatario(
            nombre="Juan",
            apellido="López",
            dni="87654321",
            telefono="2215550000",
            correo="juan@mail.com",
            id_carrera=carrera.id
        )
        session.add(destinatario)
        session.commit()
        session.refresh(destinatario)

        
        estado_insumo = EstadoInsumo(
            nombre="Disponible",
            observacion="En buen estado"
        )
        session.add(estado_insumo)
        session.commit()
        session.refresh(estado_insumo)

        
        insumo = Insumo(
            codigo="PROY-001",
            nombre="Proyector",
            ubicacion="Aula 3",
            id_estado=estado_insumo.id
        )
        session.add(insumo)
        session.commit()
        session.refresh(insumo)

        
        estado_prestamo = EstadoPrestamo(nombre="Activo")
        session.add(estado_prestamo)
        session.commit()
        session.refresh(estado_prestamo)

        
        from datetime import date
        prestamo = Prestamo(
            fecha_entrega=date.today(),
            fecha_devolucion=date(2026, 6, 1),
            obs="Sin observaciones",
            id_estadoPrestamo=estado_prestamo.id,
            id_destinatario=destinatario.id,
            id_insumo=insumo.id,
            id_usuario=usuario.id
        )
        session.add(prestamo)
        session.commit()

        print("Todos los datos de prueba cargados correctamente")


crear_bd()
    #cargar_datos_prueba()
