import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPRD Koopanalyse", layout="centered")

st.markdown("""
    <style>
        .stSelectbox label {
            font-weight: bold;
            background-color: #f0f2f6;
            padding: 8px 12px;
            border-radius: 8px;
            margin-top: 10px;
            display: block;
        }
        .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 IWDA.AS (MSCI World ETF) - Koopmoment Analyse")

st.header("1. Invulformulier: Fear & Greed Parameters")

# Keuzelijst voor scores
keuzeopties = {
    "Extreme Fear": 10,
    "Fear": 25,
    "Neutral": 50,
    "Greed": 75,
    "Extreme Greed": 90
}

params = {
    "Momentum": st.selectbox("Momentum", list(keuzeopties.keys())),
    "Stock Price Strength": st.selectbox("Stock Price Strength", list(keuzeopties.keys())),
    "Stock Price Breadth": st.selectbox("Stock Price Breadth", list(keuzeopties.keys())),
    "Put/Call Ratio": st.selectbox("Put/Call Ratio", list(keuzeopties.keys())),
    "Market Volatility": st.selectbox("Market Volatility", list(keuzeopties.keys())),
    "Safe Haven Demand": st.selectbox("Safe Haven Demand", list(keuzeopties.keys())),
    "Junk Bond Demand": st.selectbox("Junk Bond Demand", list(keuzeopties.keys())),
}

# Omzetten naar numerieke scores
numerieke_scores = [keuzeopties[waarde] for waarde in params.values()]
fear_greed_score = sum(numerieke_scores) / len(numerieke_scores)

st.markdown(f"Gemiddelde Fear & Greed Score: **{fear_greed_score:.1f}/100**")

# Interpretatie
if fear_greed_score < 30:
    sentiment = ("😨 Angst op de markt", "red")
elif fear_greed_score > 70:
    sentiment = ("😎 Hebzucht overheerst", "green")
else:
    sentiment = ("😐 Neutraal sentiment", "orange")

st.markdown(f"**Sentiment:** <span style='color:{sentiment[1]}'>{sentiment[0]}</span>", unsafe_allow_html=True)

st.header("2. IWDA ETF Analyse")

# Haal IWDA.AS op
s = yf.Ticker("IWDA.AS")
data = s.history(period="1y")

# Check of data geldig is
if data.empty:
    st.error("⚠️ Geen data beschikbaar voor IWDA.AS. Probeer later opnieuw of controleer je internetverbinding.")
    st.stop()

# Berekeningen
close = data['Close']
data['200d_avg'] = close.rolling(window=200).mean()
current_price = close[-1]
avg_200d = data['200d_avg'][-1]
lowest_price = close.min()

st.markdown(f"**Huidige koers:** €{current_price:.2f}")
st.markdown(f"**200-daags gemiddelde:** €{avg_200d:.2f}")
st.markdown(f"**12-maands dieptepunt:** €{lowest_price:.2f}")

# Beoordelingen
boven_gem = current_price > avg_200d
afstand_tot_dieptepunt = (current_price - lowest_price) / lowest_price

# Scoring
score = 0
if not boven_gem:
    score += 1
if fear_greed_score < 30:
    score += 1
if afstand_tot_dieptepunt < 0.1:
    score += 1

# Visualisatie
st.subheader("📊 IWDA Koersgrafiek + 200d Gemiddelde")
if data['200d_avg'].isnull().all():
    st.warning("📉 Onvoldoende data voor 200-daags gemiddelde. Grafiek wordt niet getoond.")
else:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(close.index, close, label="Koers")
    ax.plot(data['200d_avg'], label="200d Gem.", linestyle='--')
    ax.axhline(lowest_price, color='gray', linestyle=':', label='12m Bodem')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

st.header("3. Analyse Resultaat")
if score == 3:
    st.success("🟢 Interessant koopmoment: angstig sentiment, lage prijs en onder 200d gemiddelde.")
elif score == 2:
    st.info("🟠 Potentieel koopmoment, maar niet alle signalen zijn gunstig.")
elif score == 1:
    st.warning("🟡 Markt is niet overgewaardeerd, maar geen sterk signaal.")
else:
    st.error("🔴 Weinig koopargumenten momenteel. Geduld is een deugd.")
