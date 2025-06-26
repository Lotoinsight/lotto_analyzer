import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
from io import StringIO

# 페이지 기본 설정
st.set_page_config(page_title="로또 분석기", layout="wide")
st.title("🎯 로또 번호 분석기: 평균 회귀 vs. 단순 빈도")

# 데이터 불러오기
df = pd.read_csv("lotto_1977_named.csv")
number_cols = [f'번호{i}' for i in range(1, 7)]

# 회차 범위 슬라이더
min_round = int(df["회차"].min())
max_round = int(df["회차"].max())
selected_range = st.slider("🔍 분석할 회차 범위 선택", min_value=min_round, max_value=max_round,
                             value=(min_round, max_round))

filtered_df = df[(df["회차"] >= selected_range[0]) & (df["회차"] <= selected_range[1])]
st.write(f"Selected rounds: **{len(filtered_df)}**")

# 번호 추출 및 출현 횟수 계산
numbers = filtered_df[number_cols].values.flatten()
counts = pd.Series(numbers).value_counts().sort_index()
counts = counts.reindex(range(1, 46), fill_value=0)

# 전체 회차 기준 정보
full_counts = pd.Series(df[number_cols].values.flatten()).value_counts().sort_index()
full_counts = full_counts.reindex(range(1, 46), fill_value=0)

# 평균 및 회귀점수 계산
avg_count = counts.mean()
full_avg = full_counts.mean()
regression_score = avg_count - counts
reference_regression = full_avg - full_counts
combined_score = (regression_score * 0.6) + (reference_regression * 0.4)

# 번호 필터링 조건 설정
even_odd = st.sidebar.radio("🔢 홀/짝 번호 필터", ("전체", "홀수만", "짝수만"))
number_range = st.sidebar.selectbox("📦 번호 구간 필터", ("전체", "1~10", "11~20", "21~30", "31~40", "41~45"))
ac_filter = st.sidebar.checkbox("🧠 AC 번호(숫자 다양성) 기준 필터 적용")

def calculate_ac(numbers):
    diffs = sorted(set([b - a for i, a in enumerate(numbers) for b in numbers[i+1:]]))
    return len(diffs)

def passes_filters(nums):
    if even_odd == "홀수만" and any(n % 2 == 0 for n in nums): return False
    if even_odd == "짝수만" and any(n % 2 != 0 for n in nums): return False
    if number_range != "전체":
        start, end = map(int, number_range.split("~"))
        if any(n < start or n > end for n in nums): return False
    if ac_filter and calculate_ac(nums) < 4: return False
    return True

# 분석 방식 선택
mode = st.radio("📊 추천 방식 선택", ["통합 회귀 점수 기반 (추천)", "평균 회귀 기반", "단순 빈도 기반"])

if mode == "통합 회귀 점수 기반 (추천)":
    score = combined_score.sort_values(ascending=False)
elif mode == "평균 회귀 기반":
    score = regression_score.sort_values(ascending=False)
else:
    score = counts.sort_values(ascending=False)

result_df = pd.DataFrame({
    "번호": score.index,
    "출현횟수": counts[score.index].values,
    "회귀점수(선택범위)": regression_score[score.index].values,
    "회귀점수(전체기준)": reference_regression[score.index].values,
    "통합회귀점수(60:40)": combined_score[score.index].values
})

# 추천 번호 필터링 적용
top_candidates = result_df["번호"].tolist()
recommended = []
for i in range(len(top_candidates) - 5):
    subset = sorted(top_candidates[i:i+6])
    if passes_filters(subset):
        recommended = subset
        break

st.success(f"🎯 추천 번호 ({mode}): {recommended}")

# 결과 테이블 출력
st.subheader("📋 분석 결과 표")
st.dataframe(result_df)

# 추천 번호 저장
csv_download = result_df.to_csv(index=False)
st.download_button("💾 분석 결과 다운로드", csv_download, file_name="lotto_analysis_result.csv")

# 출현 횟수 그래프
st.subheader("📊 번호별 출현 횟수")
fig1, ax1 = plt.subplots(figsize=(12, 4))
counts.plot(kind='bar', color='skyblue', ax=ax1)
plt.axhline(avg_count, color='red', linestyle='--', label='Average (Selected)')
plt.title("Draw Frequency by Number")
plt.xlabel("Number")
plt.ylabel("Frequency")
plt.legend()
st.pyplot(fig1)

# 회차 범위 슬라이더로 추세 구간 설정
trend_range = st.slider("📈 Draw Trend Round Range", min_value=selected_range[0], max_value=selected_range[1],
                        value=(selected_range[0], selected_range[1]))
trend_df = filtered_df[(filtered_df["회차"] >= trend_range[0]) & (filtered_df["회차"] <= trend_range[1])]

st.subheader("📈 Draw Trend by Round (Selected Numbers)")
selected_numbers = st.multiselect("📌 Select numbers to view trend", options=list(range(1, 46)), default=recommended)
max_window = len(trend_df)
rolling_window = st.slider("📐 Moving average window (rounds)", min_value=1, max_value=max_window, value=min(5, max_window))

trend_data = {num: [] for num in selected_numbers}
rounds = trend_df["회차"].tolist()
for _, row in trend_df.iterrows():
    nums = row[number_cols].tolist()
    for num in selected_numbers:
        trend_data[num].append(1 if num in nums else 0)

smoothed_data = {
    num: pd.Series(values).rolling(window=rolling_window, min_periods=1).mean().tolist()
    for num, values in trend_data.items()
}

# Plotly 그래프로 대체 (인터랙티브 수치 확인 가능)
fig2 = go.Figure()
for num, values in smoothed_data.items():
    fig2.add_trace(go.Scatter(x=rounds, y=values, mode='lines', name=f"Number {num}"))
fig2.update_layout(title=f"Number Trend (Moving Average: {rolling_window} rounds)",
                   xaxis_title="Round", yaxis_title="Appearance Probability",
                   xaxis=dict(autorange='reversed'))
st.plotly_chart(fig2)
