import pandas as pd
import numpy as np
import yfinance as yf

from pypfopt import risk_models, EfficientFrontier, DiscreteAllocation
from pypfopt.discrete_allocation import get_latest_prices
from pypfopt.black_litterman import BlackLittermanModel

def rodar_modelo(carteira, universo, views):
    # =========================
    # CONFIG
    # =========================

    start_date = "2020-01-01"

    # =========================
    # 1. DADOS
    # =========================

    dados = yf.download(universo, start=start_date, auto_adjust=True)

    # Garante que pegamos apenas os preços de fechamento
    if "Close" in dados:
        dados = dados["Close"]

    # Se vier como Series (apenas 1 ativo), converte para DataFrame
    if isinstance(dados, pd.Series):
        dados = dados.to_frame()

    dados = dados.dropna(axis=1, how="all")

    # =========================
    # FILTRO DIFERENCIADO
    # =========================

    min_dias_strict = int(len(dados) * 0.8)
    min_dias_relaxed = int(len(dados) * 0.3)

    def is_etf_ou_bdr(ticker):
        # ETFs conhecidos
        etfs = ["BOVA11.SA", "SMAL11.SA", "IVVB11.SA", "HASH11.SA"]
        
        # BDRs terminam com 3 ou 4 números + SA (ex: AAPL34, NVDC34)
        return ticker in etfs or ticker.endswith("34.SA") or ticker.endswith("39.SA")

    colunas_validas = []

    for col in dados.columns:
        serie = dados[col].dropna()
        
        if is_etf_ou_bdr(col):
            if len(serie) >= min_dias_relaxed:
                colunas_validas.append(col)
        else:
            if len(serie) >= min_dias_strict:
                colunas_validas.append(col)

    dados = dados[colunas_validas]

    dados = dados.ffill().dropna()

    if len(dados.columns) < 2:
        raise ValueError("Menos de 2 ativos válidos após filtro. Ajuste o universo.")

    # =========================
    # 2. VALOR DA CARTEIRA
    # =========================

    latest_prices = get_latest_prices(dados)

    valor_total = 0
    valores_ativos = {}


    for ativo, qtd in carteira.items():
        if ativo not in latest_prices:
            continue

        preco = latest_prices[ativo]
        valor = preco * qtd
        valores_ativos[ativo] = valor
        valor_total += valor

    if valor_total == 0:
        raise ValueError(
            "Carteira inválida: nenhum ativo possui preço disponível no universo."
        )

    # =========================
    # 3. COVARIÂNCIA ROBUSTA
    # =========================

    S = risk_models.CovarianceShrinkage(dados).ledoit_wolf()

    # =========================
    # 4. BLACK-LITTERMAN
    # =========================

    # Remove views de ativos que não existem nos dados
    views_filtradas = {
        k: v for k, v in views.items()
        if k in dados.columns
    }

    bl = BlackLittermanModel(
        S,
        pi="equal",
        absolute_views=views_filtradas,
        tau=0.03
    )

    retornos_bl = bl.bl_returns()

    # =========================
    # 5. OTIMIZAÇÃO ROBUSTA
    # =========================

    ef = EfficientFrontier(retornos_bl, S, weight_bounds=(0, 0.25))

    def is_fii(ticker):
        return ticker.endswith("11.SA") and ticker not in [
            "BOVA11.SA", "SMAL11.SA", "IVVB11.SA", "HASH11.SA"
        ]

    fiis_no_universo = [t for t in dados.columns if is_fii(t)]

    if len(fiis_no_universo) > 0:

        ef.add_constraint(
            lambda w: sum(
                w[i] for i, t in enumerate(dados.columns) if is_fii(t)
            ) >= 0.1
        )

        ef.add_constraint(
            lambda w: sum(
                w[i] for i, t in enumerate(dados.columns) if is_fii(t)
            ) <= 0.3
        )

    pesos_otimizados = ef.max_sharpe()
    pesos_otimizados = ef.clean_weights()

    # =========================
    # 6. REBALANCEAMENTO
    # =========================

    alocador = DiscreteAllocation(
        pesos_otimizados,
        latest_prices,
        total_portfolio_value=valor_total
    )

    alocacao, sobra = alocador.lp_portfolio()

    # =========================
    # 7. DIVERSIFICAÇÃO
    # =========================

    corr = dados.pct_change().dropna().corr()

    ativos_carteira = [
        ativo for ativo in carteira.keys()
        if ativo in corr.columns
    ]

    score_div = {}

    for ativo in dados.columns:
        if ativo not in ativos_carteira:
            media_corr = corr[ativo][ativos_carteira].mean()
            score_div[ativo] = media_corr

    diversificacao = sorted(score_div.items(), key=lambda x: x[1])

    return {
        "valor_total": valor_total,
        "pesos": pesos_otimizados,
        "rebalanceamento": alocacao,
        "sobra": sobra,
        "diversificacao": diversificacao[:10]
    }