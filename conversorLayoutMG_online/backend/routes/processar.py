from fastapi import APIRouter, UploadFile, File
import pandas as pd

from services.validador import validar_cabecalho
from layouts.layouts import (
    CAMPOS_OBRIGATORIOS_MG,
    CAMPOS_OBRIGATORIOS_CONTROLLER
)

router = APIRouter()


@router.post("/processar")
async def processar(
    arquivo_mg: UploadFile = File(...),
    arquivo_controller: UploadFile = File(...)
):

    df_mg = pd.read_excel(arquivo_mg.file)
    df_controller = pd.read_excel(arquivo_controller.file)

    faltantes_mg = validar_cabecalho(
        df_mg.columns.str.strip(),
        CAMPOS_OBRIGATORIOS_MG
    )

    faltantes_controller = validar_cabecalho(
        df_controller.columns.str.strip(),
        CAMPOS_OBRIGATORIOS_CONTROLLER
    )

    if faltantes_mg or faltantes_controller:

        return {
            "sucesso": False,
            "erros": {
                "mg": faltantes_mg,
                "controller": faltantes_controller
            }
        }

    return {
        "sucesso": True,
        "mensagem": "Layout das duas planilhas validado com sucesso."
    }