import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Indicadores técnicos
def MACD(df, fast=12, slow=26, signal=9):
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def RSI(df, periods=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def Bollinger_Bands(df, n=20):
    sma = df['Close'].rolling(window=n).mean()
    std = df['Close'].rolling(window=n).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band

# Função para gerar sinais simples
def gerar_sinal(df):
    macd, signal_line = MACD(df)
    rsi = RSI(df)
    upper_band, lower_band = Bollinger_Bands(df)

    last_macd = macd.iloc[-1]
    last_signal = signal_line.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_close = df['Close'].iloc[-1]
    last_upper = upper_band.iloc[-1]
    last_lower = lower_band.iloc[-1]

    # Estratégia simples:
    # Compra (CALL) se MACD > signal, RSI < 70 e Close próximo da lower band
    # Venda (PUT) se MACD < signal, RSI > 30 e Close próximo da upper band
    if (last_macd > last_signal) and (last_rsi < 70) and (last_close < last_lower * 1.01):
        return "CALL"
    elif (last_macd < last_signal) and (last_rsi > 30) and (last_close > last_upper * 0.99):
        return "PUT"
    else:
        return "AGUARDANDO"

# Interface do Streamlit
st.set_page_config(page_title="Sinais Forex", layout="wide", page_icon="💹")
st.title("📈 Sinais Forex com MACD, RSI e Bandas de Bollinger")

symbol = st.text_input("Digite o símbolo do ativo (ex: EURUSD=X)", value="EURUSD=X")
interval = st.selectbox("Intervalo de tempo", ["1m", "5m", "15m"])
if st.button("Gerar sinal"):
    try:
        df = yf.download(tickers=symbol, period="5d", interval=interval)  # aumentei período pra garantir dados
        if df.empty:
            st.error("Nenhum dado disponível para o símbolo e intervalo informados.")
        else:
            # Mostrar os dados para debug (opção 5)
            macd, signal_line = MACD(df)
            rsi = RSI(df)
            upper_band, lower_band = Bollinger_Bands(df)
            
            st.write(f"Último MACD: {macd.iloc[-1]:.4f}")
            st.write(f"Último Signal: {signal_line.iloc[-1]:.4f}")
            st.write(f"Último RSI: {rsi.iloc[-1]:.2f}")
            st.write(f"Última Close: {df['Close'].iloc[-1]:.4f}")
            st.write(f"Banda Superior: {upper_band.iloc[-1]:.4f}")
            st.write(f"Banda Inferior: {lower_band.iloc[-1]:.4f}")
            
            sinal = gerar_sinal(df)
            st.write(f"### Sinal para {symbol} no intervalo {interval}: **{sinal}**")
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}"
