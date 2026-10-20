from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from models.insumo import Insumo
from models.prestamo import Prestamo, EstadoPrestamo
from models.usuario import Usuario 
from repositores.prestamo_db import obtener_todos_prestamos, crear_prestamo, eliminar_prestamo, obtener_prestamo_id, obtener_prestamo_destinatario, obtener_todos_prestamos_morosos, modificar_prestamo
from services.user_services import get_current_user 

from sqlmodel import Session, select
from database.database import engine
from datetime import date

router = APIRouter()

#TODOS LOS PRESTAMOS
@router.get("/prestamos/")
async def obtenerPrestamos(
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    return obtener_todos_prestamos()

#Agregar un prestamo
from fastapi import APIRouter, Depends, HTTPException

@router.post("/prestamos/")
async def agregarPrestamos(prestamo: Prestamo, current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamo.id_usuario = current_user.id
    try:
        nuevo_prestamo = crear_prestamo(prestamo)
        return {"mensaje": "Préstamo agregado exitosamente", "prestamo": nuevo_prestamo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



#Eliminar un prestamo
@router.delete("/prestamos/{id}")
async def eliminarPrestamo(id: int, current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamo = obtener_prestamo_id(id)
    if prestamo:
        eliminar_prestamo(id)
        return {"mensaje": "prestamo eliminado"}
    return {"mensaje": "prestamo NO encontrado"}

#Obtener un prestamo por id
@router.get("/prestamos/{id}")
async def obtenerPrestamoId(id:int, current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamo = obtener_prestamo_id(id)
    if prestamo:
        return prestamo
    return {"mensaje": "prestamo NO encontrado"}

#Obtener prestamos por nombbre de destinatario
@router.get("/prestamos/destinatario/{nom_destinatario}")
async def obtenerPrestamosDestinatario(nom_destinatario: str, current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamo = obtener_prestamo_destinatario(nom_destinatario)
    if prestamo:
        return prestamo
    return {"mensaje": "prestamo NO encontrado"}

#obtener prestamos morosos
@router.get("/prestamos/morosos/")
async def obtenerPrestamosMorosos(current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamos = obtener_todos_prestamos_morosos()
    if prestamos:
        return prestamos
    return {"mensaje": "No se encontraron prestamos morosos"}

@router.put("/prestamos/{id}")
async def modificarPrestamo(id: int, prestamo: Prestamo, current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamo_db = obtener_prestamo_id(id)
    if prestamo_db:
        prestamo_modificado = modificar_prestamo(prestamo, prestamo_db)
        return prestamo_modificado
    return {"mensaje": "prestamo NO encontrado"}

@router.put("/prestamos/{id}/estado")
async def cambiarEstadoPrestamo(
    id: int,
    estado: str,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    prestamo = obtener_prestamo_id(id)

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Préstamo no encontrado"
        )

    with Session(engine) as session:

        statement = select(EstadoPrestamo).where(
            EstadoPrestamo.nombre == estado.capitalize()
        )

        estado_db = session.exec(statement).first()

        if not estado_db:
            raise HTTPException(
                status_code=400,
                detail="Estado de préstamo no válido"
            )

        prestamo.id_estadoPrestamo = estado_db.id

        session.add(prestamo)
        session.commit()
        session.refresh(prestamo)

        return prestamo

@router.post("/prestamos/{id}/devolver")
async def devolverPrestamo(
    id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    prestamo = obtener_prestamo_id(id)

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail="Préstamo no encontrado"
        )

    with Session(engine) as session:

        insumo = session.get(Insumo, prestamo.id_insumo)

        if insumo:
            insumo.id_estado = 1
            session.add(insumo)

        estado_devuelto = session.exec(
            select(EstadoPrestamo).where(
                EstadoPrestamo.nombre == "Devuelto"
            )
        ).first()

        if not estado_devuelto:
            raise HTTPException(
                status_code=400,
                detail="No existe el estado Devuelto"
            )

        prestamo.id_estadoPrestamo = estado_devuelto.id
        prestamo.fecha_devolucion = date.today()

        session.add(prestamo)
        session.commit()
        session.refresh(prestamo)

        return prestamo