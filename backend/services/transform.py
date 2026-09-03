#função para validar EAN's e NCM's
def validar_dados_criticos_mg(df_mg: pd.DataFrame, coluna_ean: str = "EAN", coluna_ncm: str = "NCM"):

    df = df_mg.copy()

