import pandas as pd
import numpy as np

def diferenca_acumulada(df, parametro, delta_x):
    df = df.copy()
    
    # Cálculo da deflexão média
    df["di_anterior"] = df[parametro].shift(1)
    df["di_medio"] = (df["di_anterior"] + df[parametro]) / 2
    df["di_medio"].fillna(df[parametro], inplace=True)

    # Área = deflexão média * delta x
    df["Área"] = df["di_medio"] * delta_x

    # Área acumulada
    df["Área Acumulada"] = df["Área"].cumsum()

    # X acumulado (iniciando em 0 e somando delta_x)
    df["X Acumulado"] = [i * delta_x for i in range(len(df))]

    # Cálculo correto da tangente de alpha
    soma_area = df["Área"].sum()
    soma_x = delta_x * len(df)
    tg_alpha = soma_area / soma_x if soma_x != 0 else 0

    # Zx = Área acumulada - tg_alpha * X acumulado
    df["Zx"] = df["Área Acumulada"] - tg_alpha * df["X Acumulado"]

    return df  # 🔁 Retorna o DataFrame completo, sem segmentação


def soma_acumulada(df, parametro):
    df = df.copy()
    media = df[parametro].mean()
    soma = []
    s = 0
    for val in df[parametro]:
        s += (val - media)
        soma.append(s)
    df["Soma Acumulada"] = soma
    return df  # 🔁 Retorna o DataFrame completo, sem segmentação
