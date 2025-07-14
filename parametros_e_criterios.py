CRITERIOS = {
    "IRI": {
        "unidade": "mm/m",
        "estados": ["Bom", "Regular", "Péssimo"],
        "limites": [0, 1.90, 2.70, float("inf")]
    },
    "D0": {
        "unidade": "x0,01 mm",
        "estados": ["Bom", "Regular", "Péssimo"],
        "limites": [0, 18.00, 36.00, float("inf")]
    },
    "SCI": {
        "unidade": "x0,01 mm",
        "estados": ["Bom", "Regular", "Péssimo"],
        "limites": [0, 8.00, 25.00, float("inf")]
    },
    "BDI": {
        "unidade": "x0,01 mm",
        "estados": ["Bom", "Regular", "Péssimo"],
        "limites": [0, 4.00, 8.00, float("inf")]
    },
    "BCI": {
        "unidade": "x0,01 mm",
        "estados": ["Bom", "Regular", "Péssimo"],
        "limites": [0, 3.00, 6.00, float("inf")]
    }
}

def classificar_valor(valor, limites, estados):
    for i in range(len(estados)):
        if limites[i] <= valor < limites[i+1]:
            return estados[i]
    return estados[-1]
