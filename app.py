import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 👇 Corrija aqui
base_dir = os.path.abspath(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
assets_path = os.path.join(base_dir, "assets")  # <- Essa linha precisa vir ANTES de usar

from utils import calcular_segmentacao, preprocessar_fwd, carregar_iri
from parametros_e_criterios import CRITERIOS, classificar_valor
from segmentacao import diferenca_acumulada, soma_acumulada

st.set_page_config(layout="wide")
st.title("📈 Segmentação Homogênea e Cadeia de Markov")

st.markdown("### 📁 Baixe os arquivos modelo")

col_fwd, col_iri = st.columns(2)


with col_fwd:
    with open(os.path.join(assets_path, "modelo_FWD.xlsx"), "rb") as f:
        st.download_button(
            label="📥 Baixar Modelo FWD",
            data=f,
            file_name="modelo_FWD.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with col_iri:
    with open(os.path.join(assets_path, "modelo_IRI.xlsx"), "rb") as f:
        st.download_button(
            label="📥 Baixar Modelo IRI",
            data=f,
            file_name="modelo_IRI.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ==========================
# 🔁 Upload dos arquivos para Markov
# ==========================
st.markdown("### 📤 Upload dos arquivos dos dois anos para análise de Markov")
col1, col2 = st.columns(2)
with col1:
    file_ano1 = st.file_uploader("Arquivo do Ano 1", type=["xlsx"], key="ano1")
with col2:
    file_ano2 = st.file_uploader("Arquivo do Ano 2", type=["xlsx"], key="ano2")

# ==========================
# 🔁 Cálculo da matriz de transição
# ==========================
if file_ano1 and file_ano2:
    st.markdown("### ⚙️ Parâmetro de Análise")
    parametro = st.selectbox("Selecione o parâmetro para análise de Markov", ["D0", "SCI", "BDI", "BCI", "IRI"])

    if st.button("🚀 Iniciar Cálculo de Markov"):
        if parametro == "IRI":
            df1 = carregar_iri(file_ano1)
            df2 = carregar_iri(file_ano2)
        else:
            df1 = preprocessar_fwd(file_ano1)
            df2 = preprocessar_fwd(file_ano2)

        criterio = CRITERIOS[parametro]
        estados = criterio["estados"]
        limites = criterio["limites"]

        df1["Distância"] = df1["Distância"].round(2)
        df2["Distância"] = df2["Distância"].round(2)
        df1["Estado"] = df1[parametro].apply(lambda x: classificar_valor(x, limites, estados))
        df2["Estado"] = df2[parametro].apply(lambda x: classificar_valor(x, limites, estados))

        df_merge = pd.merge(df1[["Distância", "Estado"]],
                            df2[["Distância", "Estado"]],
                            on="Distância", suffixes=["_ano1", "_ano2"])

        matriz_qtd = pd.crosstab(df_merge["Estado_ano1"], df_merge["Estado_ano2"], rownames=["De"], colnames=["Para"])
        matriz_pct = matriz_qtd.div(matriz_qtd.sum(axis=1), axis=0).round(3)

        # Armazena nos estados
        st.session_state["df_merge"] = df_merge
        st.session_state["matriz_pct"] = matriz_pct
        st.session_state["parametro"] = parametro
        st.session_state["estados"] = estados
        st.session_state["mostrar_projecao"] = True  # Libera projeção

# Se já tiver resultado salvo, mostra o cálculo
if "df_merge" in st.session_state and "matriz_pct" in st.session_state:
    st.markdown("### 🔁 Classificação e Geração da Matriz de Transição")
    st.dataframe(st.session_state["df_merge"])
    st.subheader("📊 Matriz de Transição - Quantidade")
    st.dataframe(pd.crosstab(st.session_state["df_merge"]["Estado_ano1"],
                             st.session_state["df_merge"]["Estado_ano2"],
                             rownames=["De"], colnames=["Para"]))
    st.subheader("📈 Matriz de Transição - Percentual")
    st.dataframe(st.session_state["matriz_pct"])


# ===============================
# 📅 Projeção com Cadeia de Markov
# ===============================
if "mostrar_projecao" in st.session_state:
    st.markdown("### 📆 Projeção de Estados Futuros com Cadeia de Markov")

    col_ini, col_fim, col_passo = st.columns(3)
    with col_ini:
        ano_inicial = st.number_input("Ano inicial", value=2019, key="inicio")
    with col_fim:
        ano_final = st.number_input("Ano final", value=2039, key="fim")
    with col_passo:
        passo_anos = st.number_input("Intervalo (anos)", value=4, key="passo")

    # Projeção sempre que esses dados estiverem definidos
    try:
        df_merge = st.session_state["df_merge"]
        matriz_pct = st.session_state["matriz_pct"]
        parametro = st.session_state["parametro"]
        estados_completos = list(CRITERIOS[parametro]["estados"])

        matriz_pct_completa = matriz_pct.reindex(index=estados_completos, columns=estados_completos, fill_value=0)
        matriz_pct_completa = matriz_pct_completa.div(matriz_pct_completa.sum(axis=1), axis=0).fillna(0)

        dist_inicial = df_merge["Estado_ano1"].value_counts(normalize=True).reindex(estados_completos).fillna(0).values
        anos_proj = list(range(ano_inicial, ano_final + 1, passo_anos))
        resultados = [dist_inicial]

        for _ in range(1, len(anos_proj)):
            nova = resultados[-1] @ matriz_pct_completa.values
            resultados.append(nova)

        df_proj = pd.DataFrame(resultados, columns=estados_completos)
        df_proj["Ano"] = anos_proj
        df_proj.set_index("Ano", inplace=True)

        # Gráfico
        cores = {"Bom": "#55cc55", "Regular": "#f68c1f", "Péssimo": "#d62728"}
        fig = go.Figure()
        for estado in reversed(estados_completos):
            fig.add_trace(go.Bar(
                x=df_proj.index,
                y=df_proj[estado],
                name=estado,
                marker_color=cores.get(estado, None),
                width=[1]*len(df_proj)
            ))

        fig.update_layout(
            barmode='stack',
            yaxis_title="Proporção",
            xaxis_title="Ano",
            title=f"Cadeia de Markov - {parametro} (Projeção)",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabela
        df_tabela = df_proj.copy() * 100
        df_tabela = df_tabela.round(2).astype(str) + "%"
        ordem_estados = list(reversed(estados_completos))
        df_tabela = df_tabela[ordem_estados]

        st.markdown("### 📋 Tabela de Distribuição por Ano")
        st.dataframe(df_tabela.style.set_properties(**{
            'text-align': 'center'
        }).set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }]), use_container_width=True)
    except ValueError as e:
            st.error("❌ Erro: o parâmetro selecionado não é compatível com o conteúdo dos arquivos enviados. Verifique se os arquivos correspondem ao tipo de dado esperado (ex: planilha de FWD para D0/SCI/BDI/BCI ou planilha de IRI para o parâmetro IRI).")
    except Exception as e:
            st.warning(f"Ocorreu um erro inesperado: {e}")
            
# 📉 Segmentação homogênea
st.markdown("### 🟩 Análise de Segmentação Homogênea")
file_segmentacao = st.file_uploader("Arquivo para Segmentação", type=["xlsx"], key="segmentacao")

if file_segmentacao:
    try:
        # Seleção do parâmetro
        parametro_segmentacao = st.selectbox("Selecione o parâmetro para análise de Markov", ["D0", "SCI", "BDI", "BCI", "IRI"], key="segmentacao_param")

        if parametro_segmentacao == "IRI":
            df = carregar_iri(file_segmentacao)
        else:
            df = preprocessar_fwd(file_segmentacao)

        # Escolha do método
        metodo = st.radio("Método de Segmentação", ["Diferença Acumulada", "Soma Acumulada"])

        # Visualizar gráfico
        st.subheader("📊 Gráfico do parâmetro selecionado")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Distância"], y=df[parametro_segmentacao], mode="lines+markers", name=parametro_segmentacao))
        st.plotly_chart(fig, use_container_width=True)

        # Input do delta x
        delta_x = st.number_input("Informe o valor de Δx (intervalo entre medições)", min_value=1, value=40)

        # Cálculo
        if st.button("🚀 Calcular Indicador"):
            if metodo == "Diferença Acumulada":
                df_calc = diferenca_acumulada(df, parametro_segmentacao, delta_x)
                st.line_chart(df_calc.set_index("Distância")[["Zx"]])
            else:
                df_calc = soma_acumulada(df, parametro_segmentacao)
                st.line_chart(df_calc.set_index("Distância")[["Soma Acumulada"]])

            st.success("Indicador calculado com sucesso! Você pode analisar o gráfico e definir manualmente os segmentos.")
            st.dataframe(df_calc)

    except ValueError as e:
        st.error("❌ Erro: o parâmetro selecionado não é compatível com o conteúdo dos arquivos enviados. Verifique se os arquivos correspondem ao tipo de dado esperado (ex: planilha de FWD para D0/SCI/BDI/BCI ou planilha de IRI para o parâmetro IRI).")
    except Exception as e:
        st.warning(f"Ocorreu um erro inesperado: {e}")




            
