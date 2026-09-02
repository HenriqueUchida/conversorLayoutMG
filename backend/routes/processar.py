from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException
import pandas as pd

router = APIRouter()

@router.post("/processar")
async def validar_ean(
    arquivo_mg: UploadFile = File(...),
    arquivo_controller: UploadFile = File(...)
):
    return {
        "sucesso": True
    }