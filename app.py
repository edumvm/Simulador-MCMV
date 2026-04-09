"""
Simulador MCMV 2026 — App Streamlit
Grupo Direcional — Forca de Vendas
Design com identidade visual Direcional
"""

import streamlit as st
import base64
import os
from simulador import (
    MUNICIPIOS, InputSimulacao, simular, formatar_moeda, formatar_percentual,
)

# ============================================================================
# CONFIGURACAO DA PAGINA
# ============================================================================

st.set_page_config(
    page_title="Simulador MCMV 2026 — Direcional",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CORES DA MARCA DIRECIONAL
# ============================================================================
# Azul Marinho (primaria):  #00325B
# Azul Medio:              #0D5F9E
# Vermelho (seta/destaque): #E30613
# Cinza Claro (fundo):     #F4F6F9
# Branco:                  #FFFFFF

COR_AZUL_ESCURO = "#00325B"
COR_AZUL_MEDIO  = "#0D5F9E"
COR_VERMELHO    = "#E30613"
COR_CINZA_FUNDO = "#F4F6F9"
COR_CINZA_TEXTO = "#6B7280"
COR_VERDE_OK    = "#0D9F6E"

# ============================================================================
# CSS CUSTOMIZADO
# ============================================================================

st.markdown(f"""
<style>
    /* ===== TIPOGRAFIA GERAL ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* ===== FUNDO DA PAGINA ===== */
    .stApp {{
        background-color: {COR_CINZA_FUNDO};
    }}

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COR_AZUL_ESCURO} 0%, #001A33 100%);
        color: white;
    }}

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stNumberInput label {{
        color: #CBD5E1 !important;
        font-size: 0.85rem;
        font-weight: 500;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: white !important;
    }}

    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stNumberInput > div > div > input {{
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }}

    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {{
        background-color: rgba(255,255,255,0.08) !important;
        border-color: rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }}

    section[data-testid="stSidebar"] .stSelectbox svg {{
        fill: white !important;
    }}

    /* ===== HEADER PRINCIPAL ===== */
    .header-container {{
        background: linear-gradient(135deg, {COR_AZUL_ESCURO} 0%, {COR_AZUL_MEDIO} 100%);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(0, 50, 91, 0.25);
    }}

    .header-title {{
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }}

    .header-subtitle {{
        color: rgba(255,255,255,0.7);
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 4px;
    }}

    .header-badge {{
        background: {COR_VERMELHO};
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}

    /* ===== INFO BAR (Cidade selecionada) ===== */
    .info-bar {{
        background: white;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 32px;
        border-left: 4px solid {COR_AZUL_MEDIO};
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}

    .info-item {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .info-label {{
        color: {COR_CINZA_TEXTO};
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .info-value {{
        color: {COR_AZUL_ESCURO};
        font-size: 0.95rem;
        font-weight: 700;
    }}

    /* ===== CARDS DE RESULTADO ===== */
    .result-card {{
        background: white;
        border-radius: 14px;
        padding: 22px 24px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }}

    .result-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }}

    .result-card .card-label {{
        color: {COR_CINZA_TEXTO};
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}

    .result-card .card-value {{
        color: {COR_AZUL_ESCURO};
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.2;
    }}

    .result-card .card-detail {{
        color: {COR_CINZA_TEXTO};
        font-size: 0.78rem;
        margin-top: 6px;
    }}

    /* Card DESTAQUE (Entrada) */
    .result-card.destaque {{
        background: linear-gradient(135deg, {COR_AZUL_ESCURO}, {COR_AZUL_MEDIO});
        border: none;
    }}

    .result-card.destaque .card-label {{
        color: rgba(255,255,255,0.7);
    }}

    .result-card.destaque .card-value {{
        color: white;
        font-size: 1.9rem;
    }}

    .result-card.destaque .card-detail {{
        color: rgba(255,255,255,0.6);
    }}

    /* Card ALERTA (Condicionamento alto) */
    .result-card.alerta {{
        border-left: 4px solid {COR_VERMELHO};
    }}

    .result-card.alerta .card-value {{
        color: {COR_VERMELHO};
    }}

    /* Card SUCESSO */
    .result-card.sucesso {{
        border-left: 4px solid {COR_VERDE_OK};
    }}

    /* ===== SECAO ===== */
    .section-title {{
        color: {COR_AZUL_ESCURO};
        font-size: 1.05rem;
        font-weight: 700;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid {COR_AZUL_MEDIO};
        display: inline-block;
    }}

    /* ===== SIDEBAR SECTION DIVIDER ===== */
    .sidebar-section {{
        color: rgba(255,255,255,0.5);
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 24px;
        margin-bottom: 8px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }}

    .sidebar-section:first-of-type {{
        border-top: none;
        margin-top: 8px;
    }}

    /* ===== ESCONDER DEFAULTS DO STREAMLIT ===== */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ===== METRICAS NATIVAS - override ===== */
    [data-testid="stMetric"] {{
        display: none;
    }}

    /* ===== SIDEBAR LOGO ===== */
    .sidebar-logo {{
        text-align: center;
        padding: 20px 16px 8px 16px;
    }}

    .sidebar-logo img {{
        max-width: 85%;
        height: auto;
        filter: brightness(0) invert(1);
    }}

    .sidebar-app-title {{
        color: white;
        font-size: 1.05rem;
        font-weight: 400;
        text-align: center;
        margin-top: 16px;
        padding: 10px 0;
        background: rgba(255,255,255,0.06);
        border-radius: 8px;
        letter-spacing: 0.3px;
    }}

    .sidebar-app-title strong {{
        font-weight: 800;
        color: {COR_VERMELHO};
    }}

    /* ===== NUMBER INPUTS — aparencia ===== */
    section[data-testid="stSidebar"] .stNumberInput input {{
        font-variant-numeric: tabular-nums;
    }}

    /* ===== RESPONSIVO MOBILE ===== */
    @media (max-width: 768px) {{
        .header-container {{
            padding: 20px;
            flex-direction: column;
            text-align: center;
            gap: 12px;
        }}
        .header-title {{
            font-size: 1.5rem;
        }}
        .info-bar {{
            flex-direction: column;
            gap: 12px;
            padding: 14px 18px;
        }}
        .result-card .card-value {{
            font-size: 1.3rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# FUNCOES AUXILIARES
# ============================================================================

def _parse_moeda(texto: str) -> float:
    """Converte texto em formato brasileiro (ex: '4.000,00' ou '4000') para float.
    Aceita formatos: '4.000,00', '4000,00', '4000.00', '4000', 'R$ 4.000,00'
    """
    if not texto:
        return 0.0
    # Remove prefixo R$, espaços
    t = texto.strip().replace("R$", "").replace(" ", "")
    if not t:
        return 0.0

    # Detecta formato brasileiro: se tem vírgula → vírgula é decimal
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    else:
        # Sem vírgula: ponto pode ser milhar (ex: '600.000' ou '4.000')
        # Se ponto existe e depois dele tem 3 dígitos → é separador de milhar
        import re
        if re.match(r'^\d{1,3}(\.\d{3})+$', t):
            # Padrão de milhar: 600.000, 4.000, 1.500
            t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return 0.0


# ============================================================================
# FUNCOES AUXILIARES DE RENDERIZACAO
# ============================================================================

def render_card(label, value, detail="", style="normal"):
    """Renderiza um card de resultado estilizado."""
    css_class = {
        "normal": "result-card",
        "destaque": "result-card destaque",
        "alerta": "result-card alerta",
        "sucesso": "result-card sucesso",
    }.get(style, "result-card")

    detail_html = f'<div class="card-detail">{detail}</div>' if detail else ""

    return f"""
    <div class="{css_class}">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
        {detail_html}
    </div>
    """


# ============================================================================
# DADOS PARA DROPDOWNS ENCADEADOS
# ============================================================================

@st.cache_data
def montar_mapeamentos():
    regioes = {}
    ufs = {}
    cidades = {}

    for _chave, mun in MUNICIPIOS.items():
        r = mun["regiao"]
        u = mun["uf"]
        c = mun["municipio"]
        regioes.setdefault(r, set()).add(u)
        ufs.setdefault(u, set()).add(c)
        cidades[(c, u)] = r

    regioes_sorted = {r: sorted(list(s)) for r, s in sorted(regioes.items())}
    ufs_sorted = {u: sorted(list(s)) for u, s in sorted(ufs.items())}
    return regioes_sorted, ufs_sorted, cidades


regioes_map, ufs_map, cidades_map = montar_mapeamentos()


# ============================================================================
# SIDEBAR — BRANDING + INPUTS
# ============================================================================

with st.sidebar:
    # Logo / Branding — carrega PNG se existir, senao usa texto
    _logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo_direcional.png")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            _logo_b64 = base64.b64encode(_f.read()).decode()
        st.markdown(
            f'<div class="sidebar-logo">'
            f'<img src="data:image/png;base64,{_logo_b64}" alt="Direcional">'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Fallback SVG inline — logo "DIRECIONAL" com seta vermelha no I
        st.markdown(f"""
        <div class="sidebar-logo">
            <svg viewBox="0 0 520 60" xmlns="http://www.w3.org/2000/svg" style="max-width:85%;">
                <text x="0" y="48" font-family="Arial Black,Impact,sans-serif"
                      font-size="56" font-weight="900" fill="white"
                      letter-spacing="1">D</text>
                <!-- I com seta vermelha -->
                <rect x="56" y="12" width="12" height="40" fill="white" rx="1"/>
                <polygon points="62,2 50,18 74,18" fill="{COR_VERMELHO}"/>
                <text x="76" y="48" font-family="Arial Black,Impact,sans-serif"
                      font-size="56" font-weight="900" fill="white"
                      letter-spacing="1">RECIONAL</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-app-title">
        Simulador <strong>MCMV</strong> 2026
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")  # spacer

    # --- Localizacao ---
    st.markdown('<div class="sidebar-section">📍 Localização</div>', unsafe_allow_html=True)

    regiao = st.selectbox("Região", list(regioes_map.keys()), label_visibility="collapsed",
                          help="Selecione a região do imóvel")
    ufs_disponiveis = regioes_map.get(regiao, [])
    uf = st.selectbox("UF", ufs_disponiveis, label_visibility="collapsed")
    cidades_disponiveis = ufs_map.get(uf, [])
    cidade = st.selectbox("Cidade", cidades_disponiveis, label_visibility="collapsed")

    # --- Cliente ---
    st.markdown('<div class="sidebar-section">👤 Cliente</div>', unsafe_allow_html=True)

    idade = st.slider("Idade", min_value=18, max_value=80, value=35,
                       help="Idade do comprador principal")

    renda_bruta_txt = st.text_input(
        "💰 Renda Bruta Familiar (R$)", value="4.000,00",
        help="De R$ 0 a R$ 13.000",
    )
    renda_bruta = _parse_moeda(renda_bruta_txt)

    parcela_siric_txt = st.text_input(
        "📋 Parcela SIRIC (R$)", value="1.500,00",
        help="Parcela apurada no SIRIC",
    )
    parcela_siric = _parse_moeda(parcela_siric_txt)

    col_fs, col_ct = st.columns(2)
    with col_fs:
        fator_social = st.selectbox("Fator Social", ["Sim", "Não"],
                                     help="Beneficiário de programa social?")
    with col_ct:
        cotista_fgts = st.selectbox("Cotista FGTS", ["Não", "Sim"],
                                     help="3+ anos de contribuição FGTS?")

    # --- Imovel ---
    st.markdown('<div class="sidebar-section">🏠 Imóvel</div>', unsafe_allow_html=True)

    preco_avaliacao_txt = st.text_input(
        "🏷️ Preço de Avaliação (R$)", value="250.000,00",
        help="Máximo R$ 600.000",
    )
    preco_avaliacao = _parse_moeda(preco_avaliacao_txt)

    col_area, col_tipo = st.columns(2)
    with col_area:
        area_util = st.number_input(
            "Área (m²)", min_value=20.0, max_value=200.0,
            value=45.0, step=1.0, format="%.1f",
        )
    with col_tipo:
        tipo_imovel = st.selectbox("Tipo", ["APTO", "CASA"])

    # --- Financiamento ---
    st.markdown('<div class="sidebar-section">🏦 Financiamento</div>', unsafe_allow_html=True)

    col_prazo, col_sist = st.columns(2)
    with col_prazo:
        prazo_meses = st.selectbox("Prazo", [360, 420], index=1,
                                    format_func=lambda x: f"{x} meses")
    with col_sist:
        sistema = st.selectbox("Sistema", ["PRICE", "SAC"])

    # Rodape sidebar
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center;color:rgba(255,255,255,0.3);font-size:0.65rem;">'
        f'v2.0 — MCMV 2026<br>Grupo Direcional</div>',
        unsafe_allow_html=True
    )


# ============================================================================
# VALIDACAO
# ============================================================================

erros = []
if renda_bruta <= 0:
    erros.append("Renda Bruta deve ser maior que zero.")
if parcela_siric <= 0:
    erros.append("Parcela SIRIC deve ser maior que zero.")
if preco_avaliacao <= 0:
    erros.append("Preço de Avaliação deve ser maior que zero.")
if preco_avaliacao > 600_000:
    erros.append("Preço máximo do programa MCMV é R$ 600.000.")


# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown("""
<div class="header-container">
    <div>
        <div class="header-title">Simulador <strong>MCMV</strong> 2026</div>
        <div class="header-subtitle">Minha Casa Minha Vida — Grupo Direcional</div>
    </div>
    <div class="header-badge">Simulação Instantânea</div>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# AREA DE RESULTADOS
# ============================================================================

if erros:
    for e in erros:
        st.error(e)
else:
    try:
        inp = InputSimulacao(
            regiao=regiao,
            uf=uf,
            cidade=cidade,
            idade=idade,
            fator_social=(fator_social == "Sim"),
            cotista_fgts=(cotista_fgts == "Sim"),
            renda_bruta=renda_bruta,
            parcela_siric=parcela_siric,
            preco_avaliacao=preco_avaliacao,
            area_util=area_util,
            tipo_imovel=tipo_imovel,
            prazo_meses=prazo_meses,
            sistema=sistema,
        )

        res = simular(inp)

        # --- Barra de informacao da cidade ---
        st.markdown(f"""
        <div class="info-bar">
            <div class="info-item">
                <div>
                    <div class="info-label">Cidade</div>
                    <div class="info-value">{cidade}/{uf}</div>
                </div>
            </div>
            <div class="info-item">
                <div>
                    <div class="info-label">Região</div>
                    <div class="info-value">{regiao}</div>
                </div>
            </div>
            <div class="info-item">
                <div>
                    <div class="info-label">Recorte</div>
                    <div class="info-value">{res.recorte}</div>
                </div>
            </div>
            <div class="info-item">
                <div>
                    <div class="info-label">Faixa de Renda</div>
                    <div class="info-value">{res.faixa_renda}</div>
                </div>
            </div>
            <div class="info-item">
                <div>
                    <div class="info-label">Faixa de Preço</div>
                    <div class="info-value">{res.faixa_preco}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # === METRICAS PRINCIPAIS ===
        st.markdown('<div class="section-title">📊 Resultado da Simulação</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(render_card(
                "Valor de Entrada",
                formatar_moeda(res.entrada),
                f"({100 - res.ltv*100:.0f}% do imóvel)",
                style="destaque"
            ), unsafe_allow_html=True)

        with c2:
            st.markdown(render_card(
                "Financiamento",
                formatar_moeda(res.financiamento),
                f"LTV: {formatar_percentual(res.ltv)}"
            ), unsafe_allow_html=True)

        with c3:
            st.markdown(render_card(
                "Subsídio",
                formatar_moeda(res.subsidio_complemento),
                "Complemento MCMV" if res.subsidio_complemento > 0 else "Não se aplica",
                style="sucesso" if res.subsidio_complemento > 0 else "normal"
            ), unsafe_allow_html=True)

        with c4:
            st.markdown(render_card(
                "Fin. + Subsídio",
                formatar_moeda(res.financiamento_mais_subsidio),
                f"Sobre {formatar_moeda(preco_avaliacao)}"
            ), unsafe_allow_html=True)

        # === CONDICOES DO FINANCIAMENTO ===
        st.markdown('<div class="section-title">🏦 Condições do Financiamento</div>', unsafe_allow_html=True)

        c5, c6, c7 = st.columns(3)

        with c5:
            st.markdown(render_card(
                "Taxa de Juros (a.a.)",
                formatar_percentual(res.taxa_juros_anual),
                f"{formatar_percentual(res.taxa_juros_mensal)} ao mês"
            ), unsafe_allow_html=True)

        with c6:
            # Condicionamento com alerta visual se > 30%
            cond_pct = res.condicionamento * 100
            cond_style = "alerta" if cond_pct > 30 else "sucesso"
            cond_detail = "⚠️ Acima de 30%" if cond_pct > 30 else "✅ Dentro do limite"
            st.markdown(render_card(
                "Condicionamento",
                formatar_percentual(res.condicionamento),
                cond_detail,
                style=cond_style
            ), unsafe_allow_html=True)

        with c7:
            st.markdown(render_card(
                "Sistema / Prazo",
                sistema,
                f"{prazo_meses} meses ({prazo_meses // 12} anos)"
            ), unsafe_allow_html=True)

        # === SEGUROS E TAXAS ===
        st.markdown('<div class="section-title">🛡️ Seguros e Taxas Mensais</div>', unsafe_allow_html=True)

        cs1, cs2, cs3 = st.columns(3)

        with cs1:
            st.markdown(render_card(
                "Seguro DFI",
                formatar_moeda(res.seguro_dfi),
                "Danos Físicos ao Imóvel"
            ), unsafe_allow_html=True)

        with cs2:
            st.markdown(render_card(
                "Seguro MIP",
                formatar_moeda(res.seguro_mip),
                f"Morte/Invalidez ({formatar_percentual(res.taxa_mip_pct)})"
            ), unsafe_allow_html=True)

        with cs3:
            st.markdown(render_card(
                "Taxa Administrativa",
                formatar_moeda(res.taxa_adm),
                "Mensal fixa"
            ), unsafe_allow_html=True)

        # === TETOS POR FAIXA ===
        st.markdown('<div class="section-title">📋 Tetos do Município</div>', unsafe_allow_html=True)

        ct1, ct2, ct3 = st.columns(3)

        with ct1:
            st.markdown(render_card(
                "Teto Faixa 2",
                formatar_moeda(res.teto_fx2),
                "Renda até R$ 4.700"
            ), unsafe_allow_html=True)

        with ct2:
            st.markdown(render_card(
                "Teto Faixa 3",
                formatar_moeda(res.teto_fx3),
                "Renda R$ 4.700 — R$ 8.600"
            ), unsafe_allow_html=True)

        with ct3:
            st.markdown(render_card(
                "Teto Classe Média",
                formatar_moeda(res.teto_classe_media),
                "Renda R$ 8.600 — R$ 13.000"
            ), unsafe_allow_html=True)

        # === RODAPE INFORMATIVO ===
        st.markdown("")
        st.markdown(
            f'<div style="text-align:center;color:{COR_CINZA_TEXTO};font-size:0.75rem;'
            f'padding:20px 0 10px 0;">'
            f'Simulação meramente indicativa — sujeita à análise de crédito pela instituição financeira. '
            f'Valores podem variar conforme políticas vigentes do programa MCMV.'
            f'</div>',
            unsafe_allow_html=True,
        )

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
