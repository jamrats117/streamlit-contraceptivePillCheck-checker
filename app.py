import math
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="ตารางข้อมูลยาคุมกำเนิด",
    page_icon="💊",
    layout="wide",
)

# ---------- THEME (Pastel + wrap text) ----------
st.markdown("""
<style>
/* พื้นหลังโทนพาสเทล */
body {
    background-color: #fff7fb;
}
.main {
    background-color: #fffafc;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1 {
    color: #8b5cf6;
}

/* ให้ตารางดูโค้งมน + สีพาสเทล */
.dataframe {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #f1e7ff !important;
}

/* เฮดเดอร์ตารางโทนม่วงพาสเทล */
thead tr th {
    background-color: #e5e0ff !important;
    color: #374151 !important;
    font-weight: 600 !important;
}

/* สลับสีแถว */
tbody tr:nth-child(odd) {
    background-color: #ffffff !important;
}
tbody tr:nth-child(even) {
    background-color: #f5f5ff !important;
}

/* ให้ทุก cell ห่อบรรทัดได้ */
table td, table th {
    white-space: normal !important;
    word-wrap: break-word !important;
}
</style>
""", unsafe_allow_html=True)

st.title("💊 ตารางข้อมูลยาคุมกำเนิด")
st.write("ข้อมูลดึงจาก Google Sheet ชีต **drug** โดยแสดงเฉพาะคอลัมน์สำคัญในธีมพาสเทล")

# ---------- CONNECT TO GOOGLE SHEET (แบบเดิมของคุณ) ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

cfg = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    cfg,
    scopes=SCOPES,
)

gc = gspread.authorize(creds)

# ลองอ่าน SHEET_ID / SHEET_NAME จาก secrets ระดับบนก่อน
sheet_id = st.secrets.get("SHEET_ID", cfg.get("SHEET_ID"))
sheet_name = st.secrets.get("SHEET_NAME", cfg.get("SHEET_NAME", "drug"))

sh = gc.open_by_key(sheet_id)
ws = sh.worksheet(sheet_name)

rows = ws.get_all_records()   # list[dict]
df = pd.DataFrame(rows)

# ---------- เลือกและตั้งชื่อคอลัมน์ ----------
col_map = {
    "trade name": "ชื่อการค้า (Trade Name)",
    "tablets": "จำนวนเม็ด",
    "group": "กลุ่มยา",
    "compound": "ส่วนประกอบ (Compound)",
    "How to take medicine": "วิธีรับประทาน",
}

# normalize ชื่อหัวคอลัมน์จากชีต
df.columns = [c.strip() for c in df.columns]

selected_cols = []
new_col_names = []
for eng, th in col_map.items():
    if eng in df.columns:
        selected_cols.append(eng)
        new_col_names.append(th)

df_view = df[selected_cols].copy()
df_view.columns = new_col_names

# ---------- FILTER ----------
st.markdown("ค้นหายาคุมจากชื่อการค้า หรือกรองตามกลุ่มยา", unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    keyword = st.text_input("🔍 ค้นหาจากชื่อการค้า (เช่น Mercilon, Yasmin)")
with c2:
    group_filter = st.text_input("🔍 ค้นหาจากกลุ่มยา (เช่น COC, POP)")

filtered = df_view.copy()
if keyword:
    filtered = filtered[filtered["ชื่อการค้า (Trade Name)"].str.contains(keyword, case=False, na=False)]
if group_filter:
    filtered = filtered[filtered["กลุ่มยา"].str.contains(group_filter, case=False, na=False)]

# ---------- PAGINATION (10 แถวต่อหน้า) ----------
ROWS_PER_PAGE = 10
total_rows = len(filtered)
total_pages = max(math.ceil(total_rows / ROWS_PER_PAGE), 1)

page = st.number_input("หน้า", min_value=1, max_value=total_pages, step=1)

start_idx = (page - 1) * ROWS_PER_PAGE
end_idx = start_idx + ROWS_PER_PAGE
page_df = filtered.iloc[start_idx:end_idx]

st.caption(f"แสดงแถวที่ {start_idx+1}–{min(end_idx, total_rows)} จากทั้งหมด {total_rows} รายการ")

# ---------- ใช้ pandas Styler เพื่อให้ wrap text ----------
styled = page_df.style.set_properties(
    **{
        "white-space": "normal",
        "text-align": "left",
    }
)

st.dataframe(styled, use_container_width=True, hide_index=True)