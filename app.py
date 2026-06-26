import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import io

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Conversor Layout MG",
    page_icon="📊",
    layout="centered",
)

# ── Estilo ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { max-width: 780px; padding-top: 2rem; }

    h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 0; }
    .subtitulo { color: #6b7280; font-size: 0.9rem; margin-bottom: 2rem; }

    .card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }
    .card h3 { margin: 0 0 0.3rem 0; font-size: 1rem; color: #111827; }
    .card p  { margin: 0; font-size: 0.85rem; color: #6b7280; }

    .stat-row { display: flex; gap: 1rem; margin: 1rem 0; }
    .stat {
        flex: 1;
        background: #fff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .stat .num { font-size: 1.5rem; font-weight: 700; color: #111827; }
    .stat .lbl { font-size: 0.75rem; color: #6b7280; margin-top: 2px; }

    .alerta {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 0.6rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #92400e;
        margin-bottom: 0.5rem;
    }
    .ok {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 0.6rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #065f46;
        margin-bottom: 0.5rem;
    }
    .divider { border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown("# 📊 Conversor Layout MG")
st.markdown('<p class="subtitulo">Atualiza a planilha Controller com os dados fiscais enviados pela MG.</p>', unsafe_allow_html=True)

# ── Uploads ─────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📁 Planilha Controller</h3>
        <p>Arquivo base com todos os produtos do cliente.</p>
    </div>
    """, unsafe_allow_html=True)
    file_controller = st.file_uploader("controller.xlsx", type=["xlsx"], key="controller", label_visibility="collapsed")

with col2:
    st.markdown("""
    <div class="card">
        <h3>📁 Planilha MG</h3>
        <p>Arquivo enviado pela contabilidade com as atualizações fiscais.<br>
        <strong>Lembre-se:</strong> ajuste o cabeçalho manualmente antes de fazer upload.</p>
    </div>
    """, unsafe_allow_html=True)
    file_mg = st.file_uploader("mg.xlsx", type=["xlsx"], key="mg", label_visibility="collapsed")

# ── Processamento ────────────────────────────────────────────────────────────
if file_controller and file_mg:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.spinner("Processando..."):
        try:
            # 1. Leitura
            controller = pd.read_excel(file_controller)
            mg = pd.read_excel(file_mg)

            # 1.1 Validação do cabeçalho da MG
            colunas_esperadas_mg = {
                "EAN", "NCM_Valido", "EX", "% do IVA",
                "ALIQUOTA_ICMS", "REDUCAO_ICMS", "CST_ICMS",
                "ALIQUOTA_PIS", "CST_PIS", "ALIQUOTA_COFINS",
                "CST_COFINS", "NATUREZA RECEITA",
            }
            # Normaliza o cabeçalho recebido (remove espaços/tabs/newlines)
            colunas_mg_norm = set(
                mg.columns.str.strip()
                .str.replace("\t", "", regex=False)
                .str.replace("\n", "", regex=False)
            )
            faltando = colunas_esperadas_mg - colunas_mg_norm
            if faltando:
                colunas_fmt = "\n".join(f"- `{c}`" for c in sorted(faltando))
                st.error(
                    "❌ **Cabeçalho da planilha MG inválido.**\n\n"
                    "As seguintes colunas esperadas não foram encontradas:\n\n"
                    f"{colunas_fmt}\n\n"
                    "Verifique se o cabeçalho foi ajustado manualmente antes do upload."
                )
                st.stop()

            # 1.2 Validação do cabeçalho da Controller
            colunas_esperadas_ctrl = {"EAN", "PRODUTO_ATIVO", "PR_NOME"}
            faltando_ctrl = colunas_esperadas_ctrl - set(controller.columns)
            if faltando_ctrl:
                colunas_fmt = "\n".join(f"- `{c}`" for c in sorted(faltando_ctrl))
                st.error(
                    "❌ **Cabeçalho da planilha Controller inválido.**\n\n"
                    "As seguintes colunas esperadas não foram encontradas:\n\n"
                    f"{colunas_fmt}\n\n"
                    "Verifique se o arquivo correto foi enviado."
                )
                st.stop()

            # 2. Duplicados na MG
            duplicados = mg[mg["EAN"].duplicated(keep=False)]

            # 3. EAN_CHAVE
            controller["EAN_CHAVE"] = (
                controller["EAN"].astype(str).str.strip().str.zfill(14)
            )
            mg["EAN_CHAVE"] = (
                mg["EAN"].astype(str)
                .str.replace(".0", "", regex=False)
                .str.strip()
                .str.zfill(14)
            )

            # 4. Produtos da MG não encontrados na Controller
            nao_encontrados = mg[~mg["EAN_CHAVE"].isin(controller["EAN_CHAVE"])]

            # 5. Mapa de colunas + rename
            mapa_colunas = {
                "NCM_Valido": "NCM",
                "EX": "NCM_EX",
                "% do IVA": "MVA",
                "ALIQUOTA_ICMS": "SNC_ALQ",
                "REDUCAO_ICMS": "SNC_RBC",
                "CST_ICMS": "SNC_CST",
                "ALIQUOTA_PIS": "PIS_ALQ_S",
                "CST_PIS": "PIS_CST_S",
                "ALIQUOTA_COFINS": "COFINS_ALQ_S",
                "CST_COFINS": "COFINS_CST_S",
                "NATUREZA RECEITA": "COD_NATUREZA_RECEITA",
            }
            mg.columns = (
                mg.columns.str.strip()
                .str.replace("\t", "", regex=False)
                .str.replace("\n", "", regex=False)
            )
            mg = mg.rename(columns=mapa_colunas)

            # 6. Merge
            df_final = controller.merge(
                mg,
                on="EAN_CHAVE",
                how="left",
                suffixes=("", "_NOVO"),
                indicator=True,
            )

            # 7. Não alterados
            nao_alterados = df_final.loc[
                df_final["_merge"] != "both",
                ["PRODUTO_ATIVO", "EAN", "PR_NOME", "EI_CST", "EI_ALQ", "EI_RBC",
                 "MVA_PAUTA", "MVA", "SNC_CST", "SNC_ALQ", "SNC_RBC", "NCM",
                 "NCM_EX", "PIS_CST_E", "PIS_ALQ_E", "COFINS_CST_E", "COFINS_ALQ_E",
                 "PIS_CST_S", "PIS_ALQ_S", "COFINS_CST_S", "COFINS_ALQ_S",
                 "COD_NATUREZA_CREDITO", "COD_NATUREZA_RECEITA", "IPI_VALOR",
                 "UF_FCP", "ALQ_FCP", "ALQ_FCPST"],
            ].copy()
            nao_alterados["NCM"] = (
                nao_alterados["NCM"].astype(str)
                .str.replace(".0", "", regex=False).str.zfill(8)
            )
            nao_alterados["EAN"] = (
                nao_alterados["EAN"].astype(str)
                .str.replace(".0", "", regex=False).str.zfill(14)
            )
            ativos_nao_alterados = (nao_alterados["PRODUTO_ATIVO"] == "S").sum()

            # 8. Serão alterados (para validação)
            alterados_excel = df_final.loc[
                df_final["_merge"] == "both",
                ["PRODUTO_ATIVO", "EAN_CHAVE", "PR_NOME",
                 "MVA", "MVA_NOVO", "SNC_CST", "SNC_CST_NOVO",
                 "SNC_ALQ", "SNC_ALQ_NOVO", "SNC_RBC", "SNC_RBC_NOVO",
                 "NCM", "NCM_NOVO", "NCM_EX", "NCM_EX_NOVO",
                 "PIS_CST_S", "PIS_CST_S_NOVO", "PIS_ALQ_S", "PIS_ALQ_S_NOVO",
                 "COFINS_CST_S", "COFINS_CST_S_NOVO", "COFINS_ALQ_S", "COFINS_ALQ_S_NOVO",
                 "COD_NATUREZA_RECEITA", "COD_NATUREZA_RECEITA_NOVO"],
            ].copy()
            alterados_excel["NCM"] = (
                alterados_excel["NCM"].astype(str)
                .str.replace(".0", "", regex=False).str.zfill(8)
            )
            alterados_excel["NCM_NOVO"] = (
                alterados_excel["NCM_NOVO"].astype(str)
                .str.replace(".0", "", regex=False).str.zfill(8)
            )

            # 9. Atualização dos campos
            campos_atualizar = list(mapa_colunas.values())
            for campo in campos_atualizar:
                col_novo = f"{campo}_NOVO"
                if col_novo in df_final.columns:
                    df_final[campo] = df_final[col_novo].fillna(df_final[campo])

            # 10. Arquivo final
            colunas_temp = [c for c in df_final.columns if c.endswith("_NOVO")]
            arquivo_final = df_final.loc[df_final["_merge"] == "both"].copy()
            arquivo_final.drop(columns=["EAN_CHAVE", "NCM_antigo", "DESCRIÇÃO", "_merge"] + colunas_temp,
                               inplace=True, errors="ignore")

            campos_8 = ["NCM"]
            campos_2 = ["NCM_EX", "SNC_CST", "PIS_CST_S", "COFINS_CST_S"]
            for campo in campos_8:
                if campo in arquivo_final.columns:
                    arquivo_final[campo] = (
                        arquivo_final[campo].astype(str)
                        .str.replace(".0", "", regex=False).str.zfill(8)
                    )
            for campo in campos_2:
                if campo in arquivo_final.columns:
                    arquivo_final[campo] = (
                        arquivo_final[campo].astype(str)
                        .str.replace(".0", "", regex=False).str.zfill(2)
                    )
            arquivo_final["EAN"] = (
                arquivo_final["EAN"].astype(str)
                .str.replace(".0", "", regex=False).str.zfill(14)
            )

            # ── Resultados ──────────────────────────────────────────────────
            st.markdown("## Resultado")

            total_mg   = len(mg)
            total_ctrl = len(controller)
            total_alt  = len(alterados_excel)
            total_nalt = len(nao_alterados)

            st.markdown(f"""
            <div class="stat-row">
                <div class="stat"><div class="num">{total_ctrl:,}</div><div class="lbl">Produtos na Controller</div></div>
                <div class="stat"><div class="num">{total_mg:,}</div><div class="lbl">Enviados pela MG</div></div>
                <div class="stat"><div class="num">{total_alt:,}</div><div class="lbl">Serão atualizados</div></div>
                <div class="stat"><div class="num">{total_nalt:,}</div><div class="lbl">Sem atualização</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Alertas
            if len(duplicados) > 0:
                st.markdown(f'<div class="alerta">⚠️ <strong>{len(duplicados)} EANs duplicados</strong> encontrados na planilha MG.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ok">✅ Nenhum EAN duplicado na planilha MG.</div>', unsafe_allow_html=True)

            if len(nao_encontrados) > 0:
                st.markdown(f'<div class="alerta">⚠️ <strong>{len(nao_encontrados)} produto(s)</strong> da MG não encontrados na Controller.</div>', unsafe_allow_html=True)
                with st.expander("Ver produtos não encontrados"):
                    st.dataframe(nao_encontrados[["EAN", "DESCRIÇÃO"]].reset_index(drop=True), use_container_width=True)
            else:
                st.markdown('<div class="ok">✅ Todos os produtos da MG foram encontrados na Controller.</div>', unsafe_allow_html=True)

            if ativos_nao_alterados > 0:
                st.markdown(f'<div class="alerta">⚠️ <strong>{ativos_nao_alterados} produto(s) ativo(s)</strong> não terão atualização fiscal.</div>', unsafe_allow_html=True)

            # ── Downloads ───────────────────────────────────────────────────
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("## Downloads")

            def to_excel_bytes(df):
                buf = io.BytesIO()
                df.to_excel(buf, index=False)
                return buf.getvalue()

            def to_csv_bytes(df):
                return df.to_csv(sep=";", index=False).encode("utf-8")

            data_hoje = datetime.now().strftime("%d%m%Y")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.download_button(
                    "📥 Cadastro Atualizado (.xlsx)",
                    data=to_excel_bytes(arquivo_final),
                    file_name=f"cadastro_atualizado_{data_hoje}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
                st.download_button(
                    "📥 Cadastro Atualizado (.csv)",
                    data=to_csv_bytes(arquivo_final),
                    file_name=f"cadastro_atualizado_{data_hoje}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col_b:
                st.download_button(
                    "📥 Para Validar (.xlsx)",
                    data=to_excel_bytes(alterados_excel),
                    file_name=f"serao_alterados_{data_hoje}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            with col_c:
                st.download_button(
                    "📥 Não Atualizados (.xlsx)",
                    data=to_excel_bytes(nao_alterados),
                    file_name=f"nao_alterados_{data_hoje}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        except KeyError as e:
            st.error(f"❌ Coluna não encontrada: **{e}**. Verifique se o cabeçalho da planilha MG foi ajustado corretamente antes do upload.")
        except Exception as e:
            st.error(f"❌ Erro ao processar: {e}")

else:
    st.info("📂 Faça o upload das duas planilhas para iniciar o processamento.")
