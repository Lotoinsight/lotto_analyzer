import streamlit as st
import pandas as pd

st.title("🎯 로또 번호 당첨 회차 확인기")
st.markdown("`lotto_data_bonus_date.csv`를 기반으로 내가 고른 번호가 언제 당첨됐는지 확인합니다.")

uploaded_file = st.file_uploader("📂 CSV 파일 업로드", type=["csv"])
numbers_input = st.text_input("🔢 로또 번호 6개 입력 (쉼표로 구분)", value="1, 2, 3, 4, 5, 6")

if uploaded_file and numbers_input:
    try:
        user_numbers = sorted(set(int(x.strip()) for x in numbers_input.split(",") if x.strip().isdigit()))
        if len(user_numbers) != 6:
            st.warning("❗ 정확히 6개의 숫자를 입력해주세요.")
        else:
            df = pd.read_csv(uploaded_file)
            match_results = []

            for _, row in df.iterrows():
                draw_nums = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
                matched = len(set(user_numbers) & set(draw_nums))
                if matched >= 3:
                    match_results.append({
                        "회차": row['Round'],
                        "날짜": row['Date'],
                        "당첨번호": draw_nums,
                        "입력번호": user_numbers,
                        "일치수": matched
                    })

            if match_results:
                st.success(f"🎉 총 {len(match_results)}회 당첨 이력 발견!")
                for count in [6, 5, 4, 3]:
                    matched_df = [m for m in match_results if m["일치수"] == count]
                    if matched_df:
                        st.markdown(f"### ✅ {count}개 일치 ({len(matched_df)}회)")
                        st.dataframe(pd.DataFrame(matched_df))
            else:
                st.info("😢 일치하는 회차가 없습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")
