from typing import Annotated
from fastapi import APIRouter, Depends
from models.insumo import Insumo
from models.prestamo import Prestamo
from models.usuario import Usuario 
from repositores.prestamo_db import obtener_todos_prestamos, crear_prestamo, eliminar_prestamo, obtener_prestamo_id, obtener_prestamo_destinatario, obtener_todos_prestamos_morosos, modificar_prestamo
from services.user_services import get_current_user 


router = APIRouter()

#TODOS LOS PRESTAMOS
@router.get("/prestamos/")
async def obtenerPrestamos(current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamos = obtener_todos_prestamos()
    #for prestamo in prestamos:
        #print(prestamo) flag para ver que onda
    if prestamos:
        return prestamos
    return {"mensaje": "No se encontraron prestamos"}

#Agregar un prestamo
@router.post("/prestamos/")
async def agregarPrestamos(prestamo: Prestamo, current_user: Annotated[Usuario, Depends(get_current_user)]):
    crear_prestamo(prestamo)
    return {"mensaje": "prestamo agregado"}

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


