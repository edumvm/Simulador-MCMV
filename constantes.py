"""
Simulador MCMV 2026 — Constantes e Tabelas de Parametros
Extraidas da planilha Simulador_Vendas_Novo_MCMV_2026_Geral.v2.xlsb
"""

# --- Aba "2-Despesa-Renda(IBGE)" — indice despesa/renda por UF ---
IBGE_DESPESA_RENDA: dict[str, float] = {
    "DF":  0.0717, "RJ": -0.0178, "SP":  0.0207, "ES": -0.0510,
    "MG": -0.0568, "PR": -0.0513, "SC":  0.0458, "RS": -0.0109,
    "MS": -0.0349, "MT": -0.0013, "GO": -0.0068, "RO": -0.1000,
    "AC":  0.0344, "AM":  0.0056, "RR": -0.0483, "PA":  0.0545,
    "AP":  0.1000, "TO": -0.0317, "MA":  0.0069, "PI": -0.0813,
    "CE": -0.0787, "RN":  0.0058, "PB": -0.0678, "PE": -0.0531,
    "AL": -0.0814, "SE": -0.0618, "BA": -0.0503,
}

# --- Aba "1-Curva" — parametros da curva de subsidio ---
CURVA = {
    "D_min":            1_900,
    "D_max":           50_000,
    "renda_teto":       1_750,
    "renda_piso":       3_700,
    "dc_maximo":       55_000,
    "dc_maximo_norte": 65_000,
    "dc_minimo":        1_500,
    "renda_max_desc":   4_000,
    "apto_min":            39,
    "apto_max":            59,
    "casa_min":            46,
    "casa_max":            66,
}

# Coeficientes da parabola (calculados a partir dos parametros)
_b = (2 * CURVA["D_max"] * (CURVA["D_min"] / CURVA["D_max"] - 1)) / \
     (CURVA["renda_piso"] - CURVA["renda_teto"])
_a = (-_b) / (2 * (CURVA["renda_piso"] - CURVA["renda_teto"]))
CURVA["a"] = _a
CURVA["b"] = _b

# --- Aba "3-Cap.Fin." — Faixas de renda (colunas U-Z) ---
FAIXAS_RENDA = [
    (    0.00, 2_160),    # G1-A
    (2_160.01, 2_850),    # G1-B
    (2_850.01, 3_200),    # G1-B
    (3_200.01, 3_500),    # G2-A
    (3_500.01, 4_000),    # G2-B
    (4_000.01, 5_000),    # G2-C
    (5_000.01, 9_600),    # G3
    (9_600.01, 13_000),   # G4
]

# Taxas base por regiao (nao-cotista)
TAXAS_BASE: dict[str, list[float]] = {
    "Sul":      [0.0475, 0.0500, 0.0525, 0.0550, 0.0600, 0.0700, 0.0816, 0.10],
    "Sudeste":  [0.0475, 0.0500, 0.0525, 0.0550, 0.0600, 0.0700, 0.0816, 0.10],
    "C.Oeste":  [0.0475, 0.0500, 0.0525, 0.0550, 0.0600, 0.0700, 0.0816, 0.10],
    "Norte":    [0.0450, 0.0475, 0.0500, 0.0525, 0.0600, 0.0700, 0.0816, 0.10],
    "Nordeste": [0.0450, 0.0475, 0.0500, 0.0525, 0.0600, 0.0700, 0.0816, 0.10],
}

# Limites de preco por faixa
LIMITES_PRECO = {
    "fx2_teto":  275_000,
    "fx3_teto":  400_000,
    "fx4_teto":  600_000,
    "renda_fx3":   9_600,
    "renda_fx4":  13_000,
    "taxa_fx3":    0.0816,
    "taxa_fx4":    0.10,
}

# --- Seguro MIP por faixa etaria ---
SEGURO_MIP_FAIXAS: list[tuple[int, int, float]] = [
    (18, 25, 0.000093),
    (26, 30, 0.000096),
    (31, 35, 0.000116),
    (36, 40, 0.000154),
    (41, 45, 0.000252),
    (46, 50, 0.000386),
    (51, 55, 0.000676),
    (56, 60, 0.001533),
    (61, 65, 0.002731),
    (66, 70, 0.003259),
    (71, 75, 0.004894),
    (76, 80, 0.005312),
]

# --- Seguro DFI e Taxa Administrativa ---
TAXA_DFI = 0.000071
TAXA_ADM_TETO_FX1 = 3_200
TAXA_ADM_VALOR = 25

# --- LTV fixo ---
LTV = 0.80

# --- Aba "Teto" — Tetos de imovel por recorte territorial ---
TETO_GERAL: dict[str, dict[int, int]] = {
    "A": {1: 275_000, 2: 270_000, 3: 245_000, 4: 230_000},
    "B": {1: 270_000, 2: 255_000, 3: 240_000, 4: 225_000},
    "C": {1: 260_000, 2: 255_000, 3: 235_000, 4: 220_000},
    "D": {1:       0, 2: 235_000, 3: 225_000, 4: 210_000},
}

# Teto Fx1 = 67.5% do teto geral
TETO_FX1: dict[str, dict[int, int]] = {
    letra: {faixa: int(valor * 0.675) for faixa, valor in faixas.items()}
    for letra, faixas in TETO_GERAL.items()
}

# --- Aba "5 - Rec. Terr." — Multiplicadores territoriais para subsidio ---
REC_TERR_NACIONAL: dict[str, dict[int, float]] = {
    "A": {1: 1.20, 2: 1.15, 3: 1.10, 4: 1.05},
    "B": {1: 1.20, 2: 1.10, 3: 1.05, 4: 1.00},
    "C": {1: 1.10, 2: 1.10, 3: 1.05, 4: 0.90},
    "D": {1: 0.00, 2: 1.05, 3: 1.00, 4: 0.85},
}

REC_TERR_NORTE: dict[str, dict[int, float]] = {
    "A": {1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00},
    "B": {1: 1.63, 2: 1.63, 3: 1.50, 4: 1.50},
    "C": {1: 1.10, 2: 1.63, 3: 1.50, 4: 1.50},
    "D": {1: 0.00, 2: 1.50, 3: 1.44, 4: 1.25},
}
