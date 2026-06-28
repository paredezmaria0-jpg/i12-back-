from typing import Annotated
from fastapi import APIRouter, Depends
from models.insumo import Insumo
from models.usuario import Usuario 
from repositores.insumo_db import crear_insumo, obtener_todos_insumos, eliminar_insumo, modificar_insumo, obtener_insumo_id

from services.user_services import get_current_user 




router = APIRouter()



@router.get("/insumos/")
async def obtenerInsumos(current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumos = obtener_todos_insumos()
    #for insumo in insumos:
        #print(insumo) flag para ver que onda
    return(insumos)

@router.post("/insumos/")
async def agregarInsumos(ins : Insumo, current_user: Annotated[Usuario, Depends(get_current_user)]):
    crear_insumo(ins)
    return {"mensaje": "insumo agregado"}
#  return {f"Se esta agregando {ins}"} es un flag para ver que onda 

@router.delete("/insumos/{id}")
async def eliminarInsumo(id : int, current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumo = obtener_insumo_id(id)
    if insumo:
        eliminar_insumo(id)
        return {"mensaje": "insumo eliminado"}
    return {"mensaje": "insumo NO encontrado"}

@router.get("/insumos/{id}")
async def obtenerInsumoId(id:int, current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumo = obtener_insumo_id(id)
    if insumo:
        return insumo
    return {"mensaje": "insumo NO encontrado"}

@router.put("/insumos/{id}")
async def modificarInsumo(id : int, ins : Insumo, current_user: Annotated[Usuario, Depends(get_current_user)]):  
    insumo = obtener_insumo_id(id) 
    if insumo :
        modificar_insumo(id, ins)
        return {"mensaje": "insumo modificado"}
    return {"mensaje": "insumo NO encontrado"}