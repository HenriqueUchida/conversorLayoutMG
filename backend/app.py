from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.validaCabecalho import router as validar_router
from routes.processar import router as processamento


app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em desenvolvimento local, '*' libera todas as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(validar_router)
app.include_router(processamento)