
import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="로또 당첨 분석기", layout="wide")
st.title("🎯 로또 번호 당첨 분석기 + 자동 추천기")

uploaded_file = st.file_uploader("📂 CSV 파일 업로드 (lotto_data_bonus_date.csv)", type=["csv"])
numbers_input = st.text_input("🔢 로또 번호 6개 입력 (쉼표로 구분)", value="1, 2, 3, 4, 5, 6")

def 추천번호():
    return sorted(random.sample(range(1, 46), 6))

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        if df.empty or 'Round' not in df.columns:
            st.error("CSV 파일에 유효한 'Round' 컬럼이 없습니다.")
        else:
            last_round = int(df["Round"].max())
            trend_range = st.slider("📈 회차 범위 선택", min_value=1, max_value=last_round, value=(last_round - 10, last_round))

            df = df[(df["Round"] >= trend_range[0]) & (df["Round"] <= trend_range[1])]

            if numbers_input:
                user_numbers = sorted(set(int(x.strip()) for x in numbers_input.split(",") if x.strip().isdigit()))
                if len(user_numbers) != 6:
                    st.warning("❗ 정확히 6개의 숫자를 입력해주세요.")
                else:
                    match_results = []

                    for _, row in df.iterrows():
                        draw_nums = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
                        bonus = row['Bonus']
                        matched = len(set(user_numbers) & set(draw_nums))
                        is_bonus_matched = bonus in user_numbers
                        rank = None

                        if matched == 6:
                            rank = "🥇 1등"
                        elif matched == 5 and is_bonus_matched:
                            rank = "🥈 2등"
                        elif matched == 5:
                            rank = "🥉 3등"
                        elif matched == 4:
                            rank = "🏅 4등"
                        elif matched == 3:
                            rank = "🎖 5등"

                        if rank:
                            match_results.append({
                                "회차": row['Round'],
                                "날짜": row['Date'],
                                "당첨번호": draw_nums,
                                "보너스": bonus,
                                "입력번호": user_numbers,
                                "일치수": matched,
                                "등수": rank
                            })

                    if match_results:
                        st.success(f"🎉 총 {len(match_results)}회 당첨 이력 발견!")
                        df_match = pd.DataFrame(match_results)
                        st.dataframe(df_match)

                        st.subheader("📈 등수별 횟수 시각화")
                        rank_counts = df_match["등수"].value_counts()
                        fig, ax = plt.subplots(figsize=(6, 4))
                        rank_counts.plot(kind='bar', color='skyblue', ax=ax)
                        ax.set_ylabel("횟수")
                        ax.set_title("등수별 당첨 횟수")
                        st.pyplot(fig)
                    else:
                        st.info("😢 당첨 이력이 없습니다.")

            st.markdown("---")
            st.subheader("🤖 로또 자동 추천 번호")
            추천세트 = [추천번호() for _ in range(5)]
            for idx, r in enumerate(추천세트, 1):
                st.markdown(f"- 추천 {idx}: `{r}`")

    except Exception as e:
        st.error(f"오류 발생: {e}")
