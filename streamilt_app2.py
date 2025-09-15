# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="해수면 & 청소년 정신건강 시각화", layout="wide")

# ------------------------------
# Demo 데이터
# ------------------------------

# 해수면 상승
years = list(range(1985, 2021))
sea_level = [0.2*i + 0.1*(i%3) for i in range(len(years))]  # 예시

df_sea = pd.DataFrame({
    "연도": years,
    "해수면 상승(cm)": sea_level
})

# 청소년 정신건강
labels = ["기후불안 경험", "정신건강 진료 경험", "정상"]
sizes = [40, 30, 30]  # 예시
colors = ['#ff9999','#66b3ff','#99ff99']

# ------------------------------
# 좌우 레이아웃
# ------------------------------
col_line, col_pie = st.columns([5, 3], gap="large")

# 왼쪽: 해수면 상승 꺾은선
with col_line:
    st.header("🌊 한국 연안 해수면 상승 (1985~2020)")
    fig1, ax1 = plt.subplots()
    ax1.plot(df_sea["연도"], df_sea["해수면 상승(cm)"], marker='o', color='b')
    ax1.set_xlabel("연도")
    ax1.set_ylabel("해수면 상승(cm)")
    ax1.grid(True)
    st.pyplot(fig1)

# 오른쪽: 청소년 정신건강 원그래프
with col_pie:
    st.header("🧠 청소년 정신건강 현황")
    fig2, ax2 = plt.subplots()
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax2.set_title("청소년 정신건강 및 기후불안")
    st.pyplot(fig2)

# ------------------------------
# Optional: CSV 업로드
# ------------------------------
with st.expander("🧩 나만의 데이터 업로드 (선택)"):
    st.write("해수면 CSV 예시: 연도,해수면")
    st.write("청소년 CSV 예시: label,size")
    up = st.file_uploader("CSV 업로드", type=["csv"])
    if up is not None:
        try:
            user_df = pd.read_csv(up)
            st.success("CSV 로드 완료!")
            st.dataframe(user_df)
        except Exception as e:
            st.error(f"CSV 처리 중 오류: {e}")
