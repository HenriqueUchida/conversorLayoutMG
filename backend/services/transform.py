#função para validar EAN's e NCM's
def main_transform(df_mg: pd.DataFrame, coluna_ean: str = "EAN", coluna_ncm: str = "NCM"):

    df = df_mg.copy()

    normalizar_ean(df)

    normalizar_ncm(df)

def normalizar_ean(df):
    pass

def normalizar_ncm(df):
    pass