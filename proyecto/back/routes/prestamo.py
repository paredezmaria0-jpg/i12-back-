from typing import Annotated
from fastapi import APIRouter, Depends
from models.insumo import Insumo
from models.prestamo import Prestamo
from models.usuario import Usuario 
from repositores.prestamo_db import obtener_todos_prestamos, crear_prestamo, eliminar_prestamo, obtener_prestamo_id, obtener_prestamo_usuario, obtener_todos_prestamos_morosos
from services.user_services import get_current_user 


router = APIRouter()

#TODOS LOS PRESTAMOS
@router.get("/prestamos/")
async def obtenerPrestamos(current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamos = obtener_todos_prestamos()
    #for prestamo in prestamos:
        #print(prestamo) flag para ver que onda
    return(prestamos)

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
    return obtener_todos_prestamos(prestamo)

#Obtener prestamos por id de usuario
@router.get("/prestamos/usuario/{nom_usuario}")
async def obtenerPrestamosUsuario(nom_usuario: str, current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamo = obtener_prestamo_usuario(nom_usuario)
    return prestamo

#obtener prestamos morosos
@router.get("/prestamos/morosos/")
async def obtenerPrestamosMorosos(current_user: Annotated[Usuario, Depends(get_current_user)]):
    prestamos = obtener_todos_prestamos_morosos()
    return prestamos

