def validar_cabecalho(cabecalho, campos_obrigatorios):

    colunas_reais = {str(col).strip().upper() for col in cabecalho}

    campos_faltantes = [
        campo
        for campo in campos_obrigatorios
        if str(campo).strip().upper() not in colunas_reais
    ]

    return campos_faltantes
