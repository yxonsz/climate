import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("한국 연안 해수면 & 청소년 정신건강 데이터 시각화 🌊🧠")

# -----------------------
# 본론 1: 해수면 상승 꺾은선 그래프
# -----------------------
st.header("본론 1: 지난 35년간 한국 연안 해수면 상승")

# 예시 데이터 생성 (연도 1985~2020, 해수면 cm)
years = list(range(1985, 2021))
sea_level = [0.2*i + 0.1*(i%3) for i in range(len(years))]  # 단순 증가 패턴

df_sea = pd.DataFrame({
    "연도": years,
    "해수면 상승(cm)": sea_level
})

fig1, ax1 = plt.subplots()
ax1.plot(df_sea["연도"], df_sea["해수면 상승(cm)"], marker='o', color='b')
ax1.set_xlabel("연도")
ax1.set_ylabel("해수면 상승(cm)")
ax1.set_title("1985~2020 한국 연안 해수면 상승 추이")
ax1.grid(True)

st.pyplot(fig1)

# -----------------------
# 본론 2: 청소년 기후불안 + 정신건강 원그래프
# -----------------------
st.header("본론 2: 청소년 기후불안 및 정신건강 통계")

# 예시 데이터
labels = ["기후불안 경험 청소년", "정신건강 진료 청소년", "정상"]
sizes = [40, 30, 30]  # 퍼센트 예시
colors = ['#ff9999','#66b3ff','#99ff99']

fig2, ax2 = plt.subplots()
ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
ax2.set_title("청소년 정신건강 및 기후불안 현황")

st.pyplot(fig2)
