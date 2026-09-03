from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException
import pandas as pd

from services.validador import validar_cabecalho
from layouts.layouts import (
    CAMPOS_OBRIGATORIOS_MG,
    CAMPOS_OBRIGATORIOS_CONTROLLER
)

router = APIRouter()


@router.post("/validar_layout")
async def validar_layout(
    arquivo_mg: UploadFile = File(...),
    arquivo_controller: UploadFile = File(...)
):

    df_mg = pd.read_excel(arquivo_mg.file, nrows=0)
    df_controller = pd.read_excel(arquivo_controller.file, nrows=0)

    faltantes_mg = validar_cabecalho(
        df_mg.columns,
        CAMPOS_OBRIGATORIOS_MG
    )

    faltantes_controller = validar_cabecalho(
        df_controller.columns,
        CAMPOS_OBRIGATORIOS_CONTROLLER
    )

    if faltantes_mg or faltantes_controller:
        raise HTTPException (
            status_code = 422,
            detail= {"mg": faltantes_mg, "controller": faltantes_controller}
        )   

    return {
        "sucesso": True,
        "mensagem": "Layout das duas planilhas validado com sucesso."
    }