import streamlit as st
import pandas as pd
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_keyfile = 'C:/Users/USER/Desktop/4-1/info-prog-adv-2024/in-02-first-trial/week15/golden-index-424607-e1-504dc484c349.json'

creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)

client = gspread.authorize(creds)

# Google Sheets에 연결
sheet = client.open("finalfinal").sheet1

# Streamlit을 사용한 입력 폼
st.title("가계부 입력")
date = st.date_input("날짜", datetime.today())
category = st.selectbox("종류", ["식비", "교통비", "기타"])
amount = st.text_input("금액")

if st.button("입력"):
    try:
        # 금액이 숫자인지 확인
        amount = float(amount)
        # Google Sheets에 입력
        sheet.append_row([str(date), category, amount])
        st.success("입력 완료!")
    except ValueError:
        st.warning("금액은 숫자로 입력해 주세요.")

# Google Sheets에서 데이터 읽기
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 마지막 입력 날짜로부터 과거 4주 데이터 필터링
if not df.empty:
    df['날짜'] = pd.to_datetime(df['날짜'])
    last_date = df['날짜'].max()
    start_date = last_date - timedelta(weeks=4)
    filtered_df = df[(df['날짜'] >= start_date) & (df['날짜'] <= last_date)]

    # 주별로 데이터 그룹화
    filtered_df['주'] = filtered_df['날짜'].dt.isocalendar().week
    weekly_summary = filtered_df.groupby(['주', '종류'])['금액'].sum().unstack(fill_value=0).reset_index()

    # 통계 시각화
    st.write("최근 4주간 소비 내역")
    st.line_chart(weekly_summary.set_index('주'))
else:
    st.write("데이터가 없습니다.")
