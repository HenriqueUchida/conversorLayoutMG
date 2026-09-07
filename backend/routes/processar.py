from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException
import pandas as pd
from services.transform import main_transform


router = APIRouter()

@router.post("/processar")
async def orquestrador(
    arquivo_mg: UploadFile = File(...),
    arquivo_controller: UploadFile = File(...)
):
    
    return {
        "sucesso": True
    }