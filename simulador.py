"""
Simulador MCMV 2026 — Motor de Calculo
Conversao fiel da planilha Simulador_Vendas_Novo_MCMV_2026_Geral.v2.xlsb
"""

from dataclasses import dataclass
import json
import os

from constantes import (
    IBGE_DESPESA_RENDA, CURVA, FAIXAS_RENDA, TAXAS_BASE, LIMITES_PRECO,
    SEGURO_MIP_FAIXAS, TAXA_DFI, TAXA_ADM_TETO_FX1, TAXA_ADM_VALOR,
    TETO_GERAL, TETO_FX1, REC_TERR_NACIONAL, REC_TERR_NORTE, LTV,
)


# ============================================================================
# BASE DE MUNICIPIOS
# ============================================================================

def carregar_municipios() -> dict:
    caminho = os.path.join(os.path.dirname(__file__), "dados", "municipios.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


MUNICIPIOS = carregar_municipios()


# ============================================================================
# MODELOS DE DADOS
# ============================================================================

@dataclass
class InputSimulacao:
    regiao: str
    uf: str
    cidade: str
    idade: int
    fator_social: bool
    cotista_fgts: bool
    renda_bruta: float
    parcela_siric: float
    preco_avaliacao: float
    area_util: float
    tipo_imovel: str        # "APTO" ou "CASA"
    prazo_meses: int
    sistema: str            # "PRICE" ou "SAC"


@dataclass
class ResultadoSimulacao:
    faixa_renda: str
    faixa_preco: str
    teto_fx2: float
    teto_fx3: float
    teto_classe_media: float
    recorte: str
    condicionamento: float
    taxa_juros_anual: float
    taxa_juros_mensal: float
    ltv: float
    seguro_dfi: float
    seguro_mip: float
    taxa_adm: float
    taxa_mip_pct: float
    financiamento: float
    subsidio_complemento: float
    financiamento_mais_subsidio: float
    entrada: float
    limite_cfin: float
    limite_g2: float
    limite_g3: float
    limite_g4: float


# ============================================================================
# FUNCOES AUXILIARES
# ============================================================================

def buscar_municipio(cidade: str, uf: str) -> dict:
    chave = cidade + uf
    if chave not in MUNICIPIOS:
        raise ValueError(f"Municipio '{cidade}/{uf}' nao encontrado na base.")
    return MUNICIPIOS[chave]


def obter_recorte(municipio_data: dict) -> tuple[str, int]:
    recorte = municipio_data["recorte"]
    return recorte[0], int(recorte[-1])


def obter_tetos(municipio_data: dict) -> tuple[float, float, float]:
    return (
        municipio_data["teto_fx2"],
        municipio_data.get("novo_fx3", 400_000),
        municipio_data.get("novo_fx4", 600_000),
    )


def obter_limite_cfin(letra: str, numero: int) -> float:
    """Teto Fx1 (67.5% do geral) — usado no score de capacidade do subsidio."""
    if letra not in TETO_FX1:
        return 0
    return TETO_FX1[letra].get(numero, 0)


def obter_limite_faixa(letra: str, numero: int) -> float:
    """Teto geral por recorte territorial."""
    if letra not in TETO_GERAL:
        return 0
    return TETO_GERAL[letra].get(numero, 0)


def obter_indice_faixa_renda(renda: float) -> int:
    idx = 0
    for i, (inicio, _) in enumerate(FAIXAS_RENDA):
        if renda >= inicio:
            idx = i
    return idx


# ============================================================================
# TAXA DE JUROS — D13 de 'MCMV Novo'
# ============================================================================

def calcular_taxa_juros(
    renda: float, preco: float, regiao: str, cotista_fgts: bool,
) -> float:
    lim = LIMITES_PRECO

    if preco > lim["fx4_teto"]:
        taxa_base = lim["taxa_fx4"]
    elif preco > lim["fx3_teto"]:
        taxa_base = lim["taxa_fx4"]
    elif preco > lim["fx2_teto"]:
        if renda <= lim["renda_fx3"]:
            taxa_base = lim["taxa_fx3"]
        else:
            taxa_base = lim["taxa_fx4"]
    else:
        idx = obter_indice_faixa_renda(renda)
        if regiao not in TAXAS_BASE:
            raise ValueError(f"Regiao '{regiao}' nao reconhecida.")
        taxa_base = TAXAS_BASE[regiao][idx]

    # Desconto cotista FGTS: -0.5% somente se preco <= Fx3
    if cotista_fgts and preco <= lim["fx3_teto"]:
        desconto = 0.005
    else:
        desconto = 0.0

    return taxa_base - desconto


# ============================================================================
# SEGUROS E TAXAS
# ============================================================================

def obter_taxa_mip(idade: int) -> float:
    taxa = SEGURO_MIP_FAIXAS[0][2]
    for inicio, _, t in SEGURO_MIP_FAIXAS:
        if idade >= inicio:
            taxa = t
    return taxa


def calcular_seguro_dfi(preco_avaliacao: float) -> float:
    return preco_avaliacao * TAXA_DFI


def calcular_seguro_mip(financiamento: float, idade: int) -> float:
    return financiamento * obter_taxa_mip(idade)


def calcular_taxa_adm(renda: float) -> float:
    return TAXA_ADM_VALOR if renda > TAXA_ADM_TETO_FX1 else 0.0


# ============================================================================
# FINANCIAMENTO — E13 de 'MCMV Novo'
# ============================================================================

def calcular_financiamento(
    parcela_siric: float,
    taxa_juros_anual: float,
    idade: int,
    preco: float,
    sistema: str,
    prazo_meses: int,
    seguro_dfi: float,
    taxa_adm: float,
    renda: float,
    limite_g2: float,
    limite_g4: float,
) -> float:
    taxa_mensal = taxa_juros_anual / 12
    taxa_mip = obter_taxa_mip(idade)
    n = prazo_meses

    # (a) Capacidade pelo sistema de amortizacao
    parcela_liquida = parcela_siric - seguro_dfi - taxa_adm
    if parcela_liquida <= 0:
        capacidade = 0.0
    elif sistema == "SAC":
        capacidade = parcela_liquida / (1.0 / n + taxa_mensal + taxa_mip)
    elif sistema == "PRICE":
        if taxa_mensal == 0:
            pmt_fator = 1.0 / n
        else:
            pmt_fator = (taxa_mensal * (1 + taxa_mensal) ** n) / \
                        ((1 + taxa_mensal) ** n - 1)
        capacidade = parcela_liquida / (pmt_fator + taxa_mip)
    else:
        raise ValueError(f"Sistema '{sistema}' nao reconhecido.")

    # (b) Limite por faixa de renda
    if renda > FAIXAS_RENDA[6][1]:      # > 9600
        limite_faixa = limite_g4         # 600000
    elif renda > FAIXAS_RENDA[5][1]:    # > 5000
        limite_faixa = 400_000
    else:
        limite_faixa = limite_g2

    limite_por_faixa = limite_faixa * LTV

    # Resultado: MIN(capacidade, limite_por_faixa, preco * LTV)
    financiamento = min(capacidade, limite_por_faixa, preco * LTV)

    return max(0, round(financiamento, 2))


# ============================================================================
# SUBSIDIO — I13 de 'MCMV Novo'
# ============================================================================

def calcular_subsidio(
    renda: float,
    taxa_juros_anual: float,
    preco: float,
    uf: str,
    regiao: str,
    tipo_imovel: str,
    area_util: float,
    fator_social: bool,
    recorte_letra: str,
    recorte_numero: int,
) -> float:
    c = CURVA

    if renda > c["renda_max_desc"]:
        return 0.0

    # 1. Valor base da parabola
    if renda < c["renda_teto"]:
        desconto_base = c["D_max"]
    elif renda > c["renda_piso"]:
        desconto_base = c["D_min"]
    else:
        x = renda - c["renda_teto"]
        desconto_base = c["a"] * x ** 2 + c["b"] * x + c["D_max"]

    # 2. Ajuste IBGE
    ajuste_ibge = IBGE_DESPESA_RENDA.get(uf, 0.0)

    # 3. Score de capacidade financeira
    taxa_mensal = taxa_juros_anual / 12
    n = 420
    if taxa_mensal > 0:
        vp_anuidade = ((1 + taxa_mensal) ** n - 1) / \
                      (taxa_mensal * (1 + taxa_mensal) ** n)
    else:
        vp_anuidade = n

    limite_cfin = obter_limite_cfin(recorte_letra, recorte_numero)
    imovel_para_score = min(preco, limite_cfin) if limite_cfin > 0 else preco

    if imovel_para_score > 0:
        score_cfin = 10 - 40 * (
            renda * 0.25 * vp_anuidade / imovel_para_score - 0.5
        )
    else:
        score_cfin = 10

    # 4. Score de area util
    if tipo_imovel == "APTO":
        area_min, area_max = c["apto_min"], c["apto_max"]
    else:
        area_min, area_max = c["casa_min"], c["casa_max"]

    if area_util < area_min:
        score_area = 0
    elif area_util > area_max:
        score_area = 10
    else:
        score_area = 10 * ((area_util - area_min) / (area_max - area_min))

    # 5. Ajuste total
    ajuste_total = (ajuste_ibge + score_cfin + score_area) / 100
    desconto_ajustado = desconto_base * (1 + ajuste_total)

    # 6. Multiplicador territorial
    tabela_terr = REC_TERR_NORTE if regiao == "Norte" else REC_TERR_NACIONAL
    multiplicador = tabela_terr.get(recorte_letra, {}).get(recorte_numero, 0)
    desconto_com_terr = desconto_ajustado * multiplicador

    # 7. Teto regional
    teto_dc = c["dc_maximo_norte"] if regiao in ("Norte", "Nordeste") else c["dc_maximo"]
    desconto_final = min(desconto_com_terr, teto_dc)

    # 8. Minimo por cliente
    desconto_final = max(desconto_final, c["dc_minimo"])

    # 9. Fator Social
    desconto_final *= 1.0 if fator_social else 0.30

    return max(0, round(desconto_final, 2))


# ============================================================================
# FUNCAO PRINCIPAL
# ============================================================================

def simular(inp: InputSimulacao) -> ResultadoSimulacao:
    mun = buscar_municipio(inp.cidade, inp.uf)
    recorte_letra, recorte_numero = obter_recorte(mun)
    teto_fx2, teto_fx3, teto_classe_media = obter_tetos(mun)

    # Faixa por preco
    if inp.preco_avaliacao <= 275_000:
        faixa_preco = "Faixa 1 ou 2"
    elif inp.preco_avaliacao <= 400_000:
        faixa_preco = "Faixa 3"
    else:
        faixa_preco = "Classe Media"

    # Faixa por renda
    if inp.renda_bruta <= 2_850:
        faixa_renda = "Faixa 1"
    elif inp.renda_bruta <= 4_700:
        faixa_renda = "Faixa 2"
    elif inp.renda_bruta <= 8_600:
        faixa_renda = "Faixa 3"
    else:
        faixa_renda = "Faixa 4"

    # Taxa de juros
    taxa_juros = calcular_taxa_juros(
        renda=inp.renda_bruta, preco=inp.preco_avaliacao,
        regiao=inp.regiao, cotista_fgts=inp.cotista_fgts,
    )

    # Limites
    limite_cfin = obter_limite_cfin(recorte_letra, recorte_numero)
    limite_g2 = obter_limite_faixa(recorte_letra, recorte_numero)

    # Seguros e taxas
    seguro_dfi = calcular_seguro_dfi(inp.preco_avaliacao)
    taxa_adm = calcular_taxa_adm(inp.renda_bruta)
    taxa_mip = obter_taxa_mip(inp.idade)

    # Financiamento
    financiamento = calcular_financiamento(
        parcela_siric=inp.parcela_siric,
        taxa_juros_anual=taxa_juros,
        idade=inp.idade,
        preco=inp.preco_avaliacao,
        sistema=inp.sistema,
        prazo_meses=inp.prazo_meses,
        seguro_dfi=seguro_dfi,
        taxa_adm=taxa_adm,
        renda=inp.renda_bruta,
        limite_g2=limite_g2,
        limite_g4=teto_classe_media,
    )

    # Seguro MIP (depende do financiamento)
    seguro_mip = calcular_seguro_mip(financiamento, inp.idade)

    # Subsidio
    subsidio = calcular_subsidio(
        renda=inp.renda_bruta,
        taxa_juros_anual=taxa_juros,
        preco=inp.preco_avaliacao,
        uf=inp.uf,
        regiao=inp.regiao,
        tipo_imovel=inp.tipo_imovel,
        area_util=inp.area_util,
        fator_social=inp.fator_social,
        recorte_letra=recorte_letra,
        recorte_numero=recorte_numero,
    )

    fin_mais_sub = financiamento + subsidio
    entrada = inp.preco_avaliacao - fin_mais_sub
    condicionamento = inp.parcela_siric / inp.renda_bruta if inp.renda_bruta > 0 else 0

    return ResultadoSimulacao(
        faixa_renda=faixa_renda,
        faixa_preco=faixa_preco,
        teto_fx2=teto_fx2,
        teto_fx3=teto_fx3,
        teto_classe_media=teto_classe_media,
        recorte=mun["recorte"],
        condicionamento=round(condicionamento, 4),
        taxa_juros_anual=taxa_juros,
        taxa_juros_mensal=round(taxa_juros / 12, 10),
        ltv=LTV,
        seguro_dfi=round(seguro_dfi, 2),
        seguro_mip=round(seguro_mip, 2),
        taxa_adm=taxa_adm,
        taxa_mip_pct=taxa_mip,
        financiamento=round(financiamento, 2),
        subsidio_complemento=round(subsidio, 2),
        financiamento_mais_subsidio=round(fin_mais_sub, 2),
        entrada=round(entrada, 2),
        limite_cfin=limite_cfin,
        limite_g2=limite_g2,
        limite_g3=400_000,
        limite_g4=teto_classe_media,
    )


# ============================================================================
# FORMATACAO
# ============================================================================

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor: float) -> str:
    return f"{valor * 100:.2f}%"


# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    inp = InputSimulacao(
        regiao="C.Oeste", uf="DF", cidade="Brasília",
        idade=35, fator_social=True, cotista_fgts=False,
        renda_bruta=9_650, parcela_siric=3_690,
        preco_avaliacao=400_000, area_util=39,
        tipo_imovel="APTO", prazo_meses=420, sistema="PRICE",
    )
    res = simular(inp)

    checks = [
        ("Taxa Juros",    res.taxa_juros_anual,          0.10),
        ("Financiamento", res.financiamento,              320_000),
        ("Subsidio",      res.subsidio_complemento,       0),
        ("Seguro DFI",    res.seguro_dfi,                 28.40),
        ("Seguro MIP",    res.seguro_mip,                 37.12),
        ("Taxa Adm",      res.taxa_adm,                   25),
        ("Fin+Subsidio",  res.financiamento_mais_subsidio, 320_000),
        ("Entrada",       res.entrada,                    80_000),
        ("Condicion.",    res.condicionamento,             0.3824),
    ]

    print("Verificacao do cenario de teste:")
    all_ok = True
    for nome, calc, esperado in checks:
        ok = abs(calc - esperado) < 0.01
        status = "OK" if ok else "FALHA"
        print(f"  [{status}] {nome}: calculado={calc}, esperado={esperado}")
        if not ok:
            all_ok = False

    print(f"\nResultado: {'TODOS OK' if all_ok else 'FALHAS DETECTADAS'}")
