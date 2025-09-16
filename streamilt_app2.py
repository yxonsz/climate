# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="기후위기 & 청소년 정신건강", layout="wide")

# ------------------------------
# 본론 1: 지난 35년간 한국 연안 해수면 상승 추이 (꺾은선그래프)
# ------------------------------
st.markdown("## 🌊 본론 1: 지난 35년간 한국 연안 해수면 상승 추이")

# 예시 데이터 (연도별 해수면 높이, cm 단위라고 가정)
sea_level_data = {
    "연도": list(range(1990, 2025, 5)),
    "해수면(cm)": [0, 3, 7, 11, 16, 20, 25]  # 임의 값
}
df_sea = pd.DataFrame(sea_level_data)

fig1, ax1 = plt.subplots()
ax1.plot(df_sea["연도"], df_sea["해수면(cm)"], marker="o", color="blue")
ax1.set_title("한국 연안 해수면 상승 추이 (1990~2025)")
ax1.set_xlabel("연도")
ax1.set_ylabel("해수면(cm)")
st.pyplot(fig1)

st.caption("👉 해수면은 꾸준히 상승해왔으며, 이미 진행 중인 변화임을 수치로 확인할 수 있다.")

# ------------------------------
# 본론 2: Lancet 청소년 기후불안 조사 + 한국 청소년 정신건강 (원그래프)
# ------------------------------
st.markdown("## 🧠 본론 2: 청소년 기후불안 & 정신건강 통계")

# 예시 데이터 (퍼센트)
mental_data = {
    "구분": ["기후불안 경험", "우울/불안 진료 경험", "기타"],
    "비율(%)": [45, 30, 25]  # 임의 값
}
df_mental = pd.DataFrame(mental_data)

fig2, ax2 = plt.subplots()
ax2.pie(df_mental["비율(%)"], labels=df_mental["구분"], autopct="%.1f%%", startangle=90)
ax2.set_title("청소년 기후불안 & 정신건강 통계")
st.pyplot(fig2)

st.caption("👉 청소년 다수가 기후위기와 관련된 우울·불안을 경험하고 있으며, 이는 세대 전체의 정신 건강 문제로 이어지고 있다.")
