from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from models.insumo import Insumo, InsumoUpdate, InsumoAlta
from models.usuario import Usuario 
from repositores.insumo_db import (
    crear_insumo,
    crear_insumos,
    obtener_todos_insumos,
    eliminar_insumo,
    modificar_insumo,
    obtener_insumo_id,
    obtener_ultima_numeracion,
    obtener_ultimo_codigo,
    existe_numeracion,
    registrar_insumos
)

from services.user_services import get_current_user 




router = APIRouter()



@router.get("/insumos/")
async def obtenerInsumos(current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumos = obtener_todos_insumos()
    #for insumo in insumos:
        #print(insumo) flag para ver que onda
    return(insumos)


@router.post("/insumos/")
async def agregarInsumos(
    datos: InsumoAlta,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    insumos = registrar_insumos(datos)

    return {
        "mensaje": f"Se crearon {len(insumos)} insumo(s) correctamente.",
        "insumos": insumos
    }


@router.delete("/insumos/{id}")
async def eliminarInsumo(
    id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    resultado = eliminar_insumo(id)

    if not resultado["ok"]:
        motivo = resultado["motivo"]

        if motivo == "no_encontrado":
            raise HTTPException(
                status_code=404,
                detail="El insumo no existe."
            )

        if motivo == "ya_inhabilitado":
            raise HTTPException(
                status_code=409,
                detail="El insumo ya está inhabilitado."
            )

        if motivo == "prestado":
            raise HTTPException(
                status_code=409,
                detail="No se puede inhabilitar un insumo prestado."
            )

    return {
        "mensaje": "Insumo inhabilitado correctamente."
    }


@router.get("/insumos/siguiente-numeracion/")
async def siguienteNumeracion(
    nombre: str,
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    if not nombre.strip():
        raise HTTPException(
            status_code=400,
            detail="Ingresá el nombre del insumo."
        )

    ultima = obtener_ultima_numeracion(nombre)

    return {
        "nombre": nombre,
        "numeracion_sugerida": ultima + 1
    }


@router.get("/insumos/{id}")
async def obtenerInsumoId(id:int, current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumo = obtener_insumo_id(id)
    if insumo:
        return insumo
    return {"mensaje": "insumo NO encontrado"}

@router.put("/insumos/{id}")
async def modificarInsumo(id: int, ins: InsumoUpdate, current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumo = obtener_insumo_id(id)
    if insumo:
        return modificar_insumo(ins, insumo)
    return {"mensaje": "NO encontrado"}