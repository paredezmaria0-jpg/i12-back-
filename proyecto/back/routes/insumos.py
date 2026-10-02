from typing import Annotated
from fastapi import APIRouter, Depends
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
    if datos.cantidad < 1:
        return {"mensaje": "La cantidad debe ser mayor a 0"}

    # Si no se indica numeración, comenzar después
    # de la última numeración existente.
    if datos.numeracion is None:
        numeracion_actual = obtener_ultima_numeracion() + 1
    else:
        numeracion_actual = datos.numeracion

    numeraciones_nuevas = []

    while len(numeraciones_nuevas) < datos.cantidad:

        if not existe_numeracion(
            datos.nombre,
            numeracion_actual
        ):
            numeraciones_nuevas.append(numeracion_actual)

        numeracion_actual += 1

    # Obtener el último código INS-XXXX
    ultimo_codigo = obtener_ultimo_codigo()

    insumos = []

    for i, numeracion in enumerate(numeraciones_nuevas):

        codigo = f"INS-{ultimo_codigo + i + 1:04d}"

        nuevo_insumo = Insumo(
            codigo=codigo,
            numero_inventario=datos.numero_inventario,
            numeracion=numeracion,
            nombre=datos.nombre,
            ubicacion=datos.observacion or "",
            id_estado=1,
        )

        insumos.append(nuevo_insumo)

    crear_insumos(insumos)

    return {
        "mensaje": f"Se crearon {datos.cantidad} insumo(s) correctamente",
        "insumos": insumos,
    }

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
async def modificarInsumo(id: int, ins: InsumoUpdate, current_user: Annotated[Usuario, Depends(get_current_user)]):
    insumo = obtener_insumo_id(id)
    if insumo:
        return modificar_insumo(ins, insumo)
    return {"mensaje": "NO encontrado"}