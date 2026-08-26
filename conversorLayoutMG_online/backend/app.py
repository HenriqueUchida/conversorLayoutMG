from pathlib import Path
from backend.services.validador import carregarPlanilhas


dtypeMG = {
    "EAN": str,
    "DESCRIÇÃO" : str,
    "NCM_antigo" : str,
    "NCM_Valido" : str,
    "EX" : str,
    "% do IVA" : float,
    "ALIQUOTA_ICMS": float,
    "REDUCAO_ICMS": float,
    "CST_ICMS": str,
    "ALIQUOTA_PIS": float,
    "CST_PIS": str,
    "ALIQUOTA_COFINS": float,
    "CST_COFINS": str,
    "NATUREZA RECEITA": str,

}

dtypeController = {
    "PRODUTO_ATIVO": str,
    "EAN": str,
    "PR_NOME": str,
    "EI_CST": str,
    "EI_ALQ": float,
    "EI_RBC": float,
    "MVA_PAUTA": float,
    "MVA": float,
    "SNC_CST": str,
    "SNC_ALQ": float,
    "SNC_RBC": float,
    "NCM": str,
    "NCM_EX": str,
    "PIS_CST_E": str,
    "PIS_ALQ_E": float,
    "COFINS_CST_E": str,
    "COFINS_ALQ_E": float,
    "PIS_CST_S": str,
    "PIS_ALQ_S": float,
    "COFINS_CST_S": str,
    "COFINS_ALQ_S": float,
    "COD_NATUREZA_CREDITO": str,
    "COD_NATUREZA_RECEITA": str,
    "IPI_VALOR": str,
    "UF_FCP": str,
    "ALQ_FCP": float,
    "ALQ_FCPST": float,
    "CEST_E": str,
    "EI_CBENEF": str,
    "CEST_S": str,
    "SNC_CBENEF": str,
}

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_ARQUIVO_MG = BASE_DIR / "arquivo_temp" / "mg.xlsx"
CAMINHO_ARQUIVO_CONTROLLER = BASE_DIR / "arquivo_temp" / "controller.xlsx"
CAMINHO_SAIDA_FINAL = BASE_DIR / "arquivo_temp" / "resultado.xlsx"

def main():
    df_mg = carregarPlanilhas(CAMINHO_ARQUIVO_MG, dtypes=dtypeMG)
    df_controller = carregarPlanilhas(CAMINHO_ARQUIVO_CONTROLLER, dtypes=dtypeController)

    print(f"Base MG carregada: {len(df_mg)} registros.")
    print(f"Base Controller carregada: {len(df_controller)} registros.")


if __name__ == "__main__":
    main()