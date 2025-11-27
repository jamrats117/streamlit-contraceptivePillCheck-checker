import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="ตารางข้อมูลยาคุมกำเนิด",
    page_icon="💊",
    layout="wide",
)

# ---------- PASTEL THEME ----------
pastel_css = """
<style>
body {
    background-color: #fff7fb;
}
.main {
    background-color: #fffafd;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1 {
    color: #8b5cf6;
}
.table-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 0.5rem;
}
</style>
"""
st.markdown(pastel_css, unsafe_allow_html=True)

st.title("💊 ตารางข้อมูลยาคุมกำเนิด")

st.write("ข้อมูลดึงจาก Google Sheet ชีต `drug` โดยแสดงเฉพาะคอลัมน์สำคัญในธีมพาสเทล")

# ---------- CONNECT TO GOOGLE SHEET ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)

gc = gspread.authorize(creds)

sheet_id = st.secrets["SHEET_ID"]
sheet_name = st.secrets.get("SHEET_NAME", "drug")

sh = gc.open_by_key(sheet_id)
ws = sh.worksheet(sheet_name)

rows = ws.get_all_records()  # list of dict

# ---------- TO DATAFRAME & RENAME COLUMNS ----------
df = pd.DataFrame(rows)

# ชื่อคอลัมน์ในชีต (ภาษาอังกฤษ) → ชื่อที่แสดง (ภาษาไทย)
col_map = {
    "trade name": "ชื่อการค้า (Trade Name)",
    "tablets": "จำนวนเม็ด",
    "group": "กลุ่มยา",
    "compound": "ส่วนประกอบ (Compound)",
    "How to take medicine": "วิธีรับประทาน",
}

# normalize ให้ชื่อคอลัมน์ตรงกับ key ใน col_map
df.columns = [c.strip() for c in df.columns]

selected_cols = []
new_col_names = []
for eng, th in col_map.items():
    if eng in df.columns:
        selected_cols.append(eng)
        new_col_names.append(th)

df_view = df[selected_cols].copy()
df_view.columns = new_col_names

# ---------- FILTER UI ----------
st.markdown('<p class="table-title">ค้นหายาคุมจากชื่อการค้า หรือกรองตามกลุ่มยา</p>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    keyword = st.text_input("🔍 ค้นหาจากชื่อการค้า (เช่น Mercilon, Yasmin)", "")
with c2:
    group_filter = st.text_input("🔍 ค้นหาจากกลุ่มยา (เช่น COC, POP)", "")

filtered = df_view.copy()
if keyword:
    filtered = filtered[filtered["ชื่อการค้า (Trade Name)"].str.contains(keyword, case=False, na=False)]
if group_filter:
    filtered = filtered[filtered["กลุ่มยา"].str.contains(group_filter, case=False, na=False)]

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)