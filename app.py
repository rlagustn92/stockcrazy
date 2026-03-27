import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(page_title="시장 대시보드", layout="wide")

st.title("📊 시장 + 종목 대시보드")

NEWS_API_KEY = "17df4ce9e1a74990a4414f4a369876de"

# ---------------------------
# 🔥 테이블 글씨 크게 (CSS)
# ---------------------------
st.markdown("""
<style>
[data-testid="stDataFrame"] {
    font-size: 18px;
}
[data-testid="stDataFrame"] thead th {
    font-size: 20px;
    font-weight: bold;
}
[data-testid="stDataFrame"] tbody td {
    font-size: 18px;
    padding: 12px !important;
}
</style>
""", unsafe_allow_html=True)

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
    "SK하이닉스": "000660.KS",
    "현대차": "005380.KS",
    "KODEX 200위클리커버드콜": "498400.KS"
}

# ---------------------------
# 데이터 가져오기
# ---------------------------
@st.cache_data(ttl=300)
def get_data():
    data = []

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

        ath_val = hist_max["Close"].max()
        ath_date = hist_max["Close"].idxmax().strftime('%Y-%m-%d')
        ath_chg = ((curr - ath_val) / ath_val) * 100

        data.append({
            "항목": name,
            "현재가": curr,
            "변동폭": diff,
            "변동률": d_chg,
            "역대 최고가 대비": ath_chg,
            "역대 최고가": ath_val,
            "최고가 날짜": ath_date
        })

    df = pd.DataFrame(data)
    return df

# ---------------------------
# 🔥 색상 + 굵게 함수
# ---------------------------
def color_text(val):
    if val > 0:
        return "color: red; font-weight: bold;"
    elif val < 0:
        return "color: blue; font-weight: bold;"
    return ""

# ---------------------------
# 뉴스
# ---------------------------
@st.cache_data(ttl=600)
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=kr&category=business&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get('status') == 'ok':
            return data.get('articles', [])
    except:
        return []
    return []

# ---------------------------
# 데이터 로드
# ---------------------------
df_raw = get_data()
news = get_news()

# 👉 표시용 복사본 생성
df_display = df_raw.copy()

# ---------------------------
# 🔥 포맷 적용 (콤마 + 퍼센트)
# ---------------------------
df_display["현재가"] = df_display["현재가"].map(lambda x: f"{x:,.2f}")
df_display["변동폭"] = df_display["변동폭"].map(lambda x: f"{x:,.2f}")
df_display["변동률"] = df_display["변동률"].map(lambda x: f"{x:.2f}%")
df_display["역대 최고가 대비"] = df_display["역대 최고가 대비"].map(lambda x: f"{x:.2f}%")
df_display["역대 최고가"] = df_display["역대 최고가"].map(lambda x: f"{x:,.2f}")

# ---------------------------
# 🔥 스타일 적용
# ---------------------------
styled_df = df_raw.style.applymap(color_text, subset=["변동폭", "변동률", "역대 최고가 대비"])

# 표시용 포맷 반영
styled_df = styled_df.format({
    "현재가": "{:,.2f}",
    "변동폭": "{:,.2f}",
    "변동률": "{:.2f}%",
    "역대 최고가 대비": "{:.2f}%",
    "역대 최고가": "{:,.2f}"
})

# ---------------------------
# 기준 시간 크게
# ---------------------------
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"## ⏱ 기준 시간: {now}")

# ---------------------------
# 테이블
# ---------------------------
st.subheader("📈 시장 및 종목 현황")

# 🔥 핵심: st.write 써야 스타일 먹는다
st.write(styled_df)

# ---------------------------
# 차트
# ---------------------------
st.subheader("📉 종목 차트")

selected = st.selectbox("종목 선택", df_raw["항목"])
symbol = tickers[selected]

chart_data = yf.Ticker(symbol).history(period="3mo")
st.line_chart(chart_data["Close"])

# ---------------------------
# 뉴스
# ---------------------------
st.subheader("📰 최신 뉴스")

if news:
    for n in news:
        st.markdown(f"- [{n['title']}]({n['url']})")
else:
    st.write("뉴스 없음")
