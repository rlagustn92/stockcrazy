import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

st.set_page_config(page_title="📊 시장 대시보드", layout="wide")

st.title("📊 시장 & 종목 대시보드")

# ---------------------------
# 뉴스 API 키
# ---------------------------
NEWS_API_KEY = "여기너키"

# ---------------------------
# 티커 설정
# ---------------------------
tickers = {
    "S&P500": "^GSPC",
    "나스닥": "^IXIC",
    "코스피": "^KS11",
    "코스닥": "^KQ11",
    "USD/KRW": "KRW=X",
    "비트코인": "BTC-USD",
    "삼성전자": "005930.KS",
    "KODEX 200위클리커버드콜": "498400.KS",
    "SK하이닉스": "000660.KS",
    "현대차": "005380.KS"
}

# ---------------------------
# 데이터 가져오기 함수
# ---------------------------
@st.cache_data(ttl=300)
def get_market_data():
    combined_data = []

    for name, symbol in tickers.items():
        t = yf.Ticker(symbol)
        hist_short = t.history(period="5d")
        hist_max = t.history(period="max")

        if hist_short.empty or len(hist_short) < 2:
            continue

        curr = hist_short["Close"].iloc[-1]
        prev = hist_short["Close"].iloc[-2]

        diff = curr - prev
        d_chg = (diff / prev) * 100

        ath_series = hist_max["Close"]
        ath_val = ath_series.max()
        ath_date = ath_series.idxmax().strftime('%Y-%m-%d')
        a_chg = ((curr - ath_val) / ath_val) * 100

        combined_data.append({
            "항목": name,
            "현재가": round(curr, 2),
            "전일가": round(prev, 2),
            "변동률": round(d_chg, 2),
            "변동폭": round(diff, 2),
            "ATH대비": round(a_chg, 2),
            "ATH": round(ath_val, 2),
            "ATH 날짜": ath_date
        })

    return pd.DataFrame(combined_data)

# ---------------------------
# 뉴스 가져오기
# ---------------------------
@st.cache_data(ttl=600)
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=kr&category=business&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
    except:
        pass
    return []

df = get_market_data()
news = get_news()

# ---------------------------
# 기준 시간
# ---------------------------
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"기준 시간: {now_kst}")

# ---------------------------
# 색상 표시 함수
# ---------------------------
def color_change(val):
    if val > 0:
        return "color:red"
    elif val < 0:
        return "color:blue"
    return ""

# ---------------------------
# 데이터 표시
# ---------------------------
st.subheader("📈 시장 및 종목")

styled_df = df.style.applymap(color_change, subset=["변동률", "ATH대비"])

st.dataframe(styled_df, use_container_width=True)

# ---------------------------
# 차트
# ---------------------------
st.subheader("📉 종목 차트")

selected = st.selectbox("종목 선택", df["항목"])

symbol = tickers[selected]
chart_data = yf.Ticker(symbol).history(period="3mo")

st.line_chart(chart_data["Close"])

# ---------------------------
# 뉴스 표시
# ---------------------------
st.subheader("📰 최신 뉴스")

for n in news:
    st.markdown(f"- [{n['title']}]({n['url']})")
