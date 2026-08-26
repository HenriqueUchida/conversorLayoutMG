from pathlib import Path
from typing import Union
import io
import pandas as pd


def carregarPlanilhas(origem: Union[str, Path, io.BytesIO], dtypes: dict) -> pd.DataFrame:
    if not origem.exists():
        raise FileNotFoundError(f"Arquivo local não encontrado: {origem.resolve()}")

    return pd.read_excel(origem, dtype=dtypes)