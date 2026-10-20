# seed_estados.py
# Correr UNA SOLA VEZ desde la carpeta proyecto/back, con:  python seed_estados.py
# Carga los estados de insumo que usa el modal de edición del front
# (public/paginas/insumos.html -> select#editEstado: "Disponible" y "No Disponible").
#
# Quedan con id=1 y id=2 porque la tabla está vacía. api.js del front asume esos IDs
# (ver ESTADOS_INSUMO en api.js). Si ya tenés datos cargados o corres esto dos veces,
# revisá antes para no duplicar.

from sqlmodel import Session, select
from database.database import engine

# Hay que importar TODOS los modelos (no solo Insumo) antes de tocar la base.
# Insumo tiene una relación a Prestamo, y SQLAlchemy necesita que esa clase
# ya esté registrada para poder resolverla, aunque acá no la usemos directamente.
from models.carrera import Carrera
from models.destinatario import Destinatario
from models.insumo import Insumo, EstadoInsumo
from models.usuario import Usuario, Rol
from models.prestamo import Prestamo, EstadoPrestamo

with Session(engine) as session:
    existentes = session.exec(select(EstadoInsumo)).all()
    if existentes:
        print("Ya hay estados cargados, no se hizo nada:", [(e.id, e.nombre) for e in existentes])
    else:
        disponible = EstadoInsumo(nombre="Disponible", observacion="Insumo disponible para prestamo")
        no_disponible = EstadoInsumo(nombre="No Disponible", observacion="Insumo no disponible (prestado u otro motivo)")
        session.add(disponible)
        session.add(no_disponible)
        session.commit()
        session.refresh(disponible)
        session.refresh(no_disponible)
        print(f"Cargados: {disponible.id} -> {disponible.nombre}, {no_disponible.id} -> {no_disponible.nombre}")