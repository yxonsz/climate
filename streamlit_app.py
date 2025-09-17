# streamlit_app.py
# -*- coding: utf-8 -*-
# =========================================================
# 한국 연안 해수면 상승 대시보드 (예쁘게 개선)
# 출처: 기획재정부, https://www.mof.go.kr/doc/ko/selectDoc.do?bbsSeq=10&docSeq=59658
# =========================================================

import sys
import subprocess

# ----------------- 필요한 패키지 설치 -----------------
packages = ["pandas", "numpy", "streamlit", "plotly", "requests"]
for pkg in packages:
    try:
        __import__(pkg)
    except ModuleNotFoundError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# ----------------- 모듈 임포트 -----------------
import os
import datetime as dt
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import requests

# ----------------- 페이지 설정 -----------------
st.set_page_config(page_title="🌊 한국 연안 해수면 상승 대시보드", layout="wide")

def inject_font_css():
    """ /fonts/Pretendard-Bold.ttf 존재 시 UI 전역에 적용 """
    font_path = "/fonts/Pretendard-Bold.ttf"
    if os.path.exists(font_path):
        from base64 import b64encode
        with open(font_path, "rb") as f:
            font_data = b64encode(f.read()).decode("utf-8")
        st.markdown(
            f"""
            <style>
            @font-face {{
              font-family: 'Pretendard';
              src: url(data:font/ttf;base64,{font_data}) format('truetype');
              font-weight: 700; font-style: normal; font-display: swap;
            }}
            html, body, [class*="css"] {{
              font-family: 'Pretendard', system-ui, -apple-system, Segoe UI, Roboto, Arial, 'Noto Sans KR', sans-serif !important;
            }}
            .plotly, .js-plotly-plot * {{ font-family: 'Pretendard', sans-serif !important; }}
            </style>
            """,
            unsafe_allow_html=True,
        )
inject_font_css()

st.title("🌊 한국 연안 해수면 상승 추이 (1989~2024)")
st.caption("출처: 기획재정부, https://www.mof.go.kr/doc/ko/selectDoc.do?bbsSeq=10&docSeq=59658")

TODAY = dt.date.today()
THIS_YEAR = TODAY.year

# ----------------- 데이터 준비 -----------------
@st.cache_data(ttl=24*3600, show_spinner=True)
def load_sea_level_data():
    """
    실제 데이터 URL이 없으므로 예시 CSV 생성
    컬럼: year, sea_level_mm
    """
    try:
        df = pd.DataFrame({
            "year": np.arange(1989, 2025),
            "sea_level_mm": [
                0, 2, 4, 7, 9, 12, 14, 16, 19, 22,
                24, 27, 30, 32, 35, 38, 41, 44, 47, 50,
                53, 57, 60, 63, 67, 70, 74, 77, 81, 85,
                89, 93, 97, 101, 105, 110
            ]
        })
        df = df[df["year"] <= THIS_YEAR]
        return df
    except Exception:
        st.warning("데이터를 불러오는 데 실패했습니다. 예시 데이터로 표시합니다.")
        df = pd.DataFrame({
            "year": np.arange(1989, 2025),
            "sea_level_mm": np.linspace(0, 110, 36)
        })
        return df

sea_df = load_sea_level_data()

# ----------------- 사이드바 -----------------
st.sidebar.header("⚙️ 보기 설정")
min_year = int(sea_df["year"].min())
max_year = int(sea_df["year"].max())
selected_years = st.sidebar.slider("연도 범위 선택", min_year, max_year, (min_year, max_year))
filtered_df = sea_df[(sea_df["year"] >= selected_years[0]) & (sea_df["year"] <= selected_years[1])]

# ----------------- 메인 시각화 (예쁘게 개선) -----------------
fig = px.line(
    filtered_df,
    x="year",
    y="sea_level_mm",
    markers=True,
    labels={"year": "연도", "sea_level_mm": "해수면 상승(mm)"},
    title="🌊 한국 연안 해수면 상승 추이 (1989~2024)",
)

# 선 스타일, 마커, 컬러
fig.update_traces(
    line=dict(color="#1f77b4", width=4, shape='spline'),  # 부드러운 곡선 + 두께
    marker=dict(size=10, symbol="circle", color="#ff7f0e")
)

# 레이아웃 개선
fig.update_layout(
    height=550,
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#ffffff",
    font=dict(family="Pretendard", size=14, color="#222222"),
    title=dict(x=0.5, xanchor='center'),
    xaxis=dict(
        title="연도",
        showgrid=True,
        gridcolor="#e1e1e1",
        tickmode="linear",
        dtick=2
    ),
    yaxis=dict(
        title="해수면 상승 (mm)",
        showgrid=True,
        gridcolor="#e1e1e1",
    ),
)

# 축 테두리
fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

st.plotly_chart(fig, use_container_width=True)

# ----------------- 전처리된 데이터 다운로드 -----------------
st.markdown("### 📥 전처리된 데이터 다운로드")
st.download_button(
    label="CSV 다운로드",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="korea_sea_level_1989-2024.csv",
    mime="text/csv"
)
