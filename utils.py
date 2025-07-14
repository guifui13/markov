import pandas as pd
from segmentacao import diferenca_acumulada, soma_acumulada

def carregar_parametros(file):
    df = pd.read_excel(file, engine="openpyxl")
    parametros = [col for col in df.columns if col.lower() not in ["distancia", "trecho", "ponto"]]
    return df, parametros

def calcular_segmentacao(df, parametro, metodo, delta_x=40):
    if metodo == "Diferença Acumulada":
        segmentos = diferenca_acumulada(df, parametro, delta_x)
    else:
        segmentos = soma_acumulada(df, parametro)
    return segmentos


def preprocessar_fwd(file):
    import pandas as pd

    # Lê a planilha "FWD" pulando as 2 primeiras linhas
    df_raw = pd.read_excel(file, sheet_name="FWD", skiprows=2, engine="openpyxl")

    # Filtrar apenas as colunas de interesse
    df = pd.DataFrame()
    df["Distância"] = pd.to_numeric(df_raw["km"], errors="coerce") * 1000  # de km para metros
    df["D0"] = pd.to_numeric(df_raw["D0(corrigido)"], errors="coerce")
    df["SCI"] = pd.to_numeric(df_raw["SCI = Do-D30"], errors="coerce")
    df["BDI"] = pd.to_numeric(df_raw["BDI = D30 - D60"], errors="coerce")
    df["BCI"] = pd.to_numeric(df_raw["BCI = D60 - D90"], errors="coerce") if "BCI = D60 - D90" in df_raw.columns else None

    # Remove linhas com distância ou D0 nulo
    df.dropna(subset=["Distância", "D0"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def carregar_iri(file):
    import pandas as pd

    # Lê a planilha ""QI-IRI"" pulando as 2 primeiras linhas
    df_raw = pd.read_excel(file, sheet_name="IRI", skiprows=2, engine="openpyxl")

    # Filtrar apenas as colunas de interesse
    df = pd.DataFrame()
    df["Distância"] = pd.to_numeric(df_raw["km inicial"], errors="coerce") * 1000  # de km para metros
    df["IRI"] = pd.to_numeric(df_raw["IRI MÉDIO (m/km)"], errors="coerce")

    # Remove linhas com distância ou IRI nulo
    df.dropna(subset=["Distância", "IRI"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df



