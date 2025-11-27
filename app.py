import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="DDI Checker", page_icon="💊")
st.title("💊 DDI Checker from Google Sheet")

# ---------- CONNECT TO GOOGLE SHEET ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)

gc = gspread.authorize(creds)

sheet_id = st.secrets["SHEET_ID"]
sh = gc.open_by_key(sheet_id)
ws = sh.sheet1

data = ws.get_all_records()

st.subheader("Preview data from Google Sheet")
st.write(data)

# ---------- BASIC UI ----------
drug1 = st.text_input("Drug 1")
drug2 = st.text_input("Drug 2")

def check_ddi(d1, d2):
    d1 = d1.lower().strip()
    d2 = d2.lower().strip()
    results = []
    for row in data:
        a = str(row.get("drug1", "")).lower()
        b = str(row.get("drug2", "")).lower()
        if (a == d1 and b == d2) or (a == d2 and b == d1):
            results.append(row)
    return results

if st.button("Check DDI"):
    if not drug1 or not drug2:
        st.warning("กรุณากรอกชื่อยาให้ครบ")
    else:
        hits = check_ddi(drug1, drug2)
        if hits:
            st.error("พบ Interaction")
            st.write(hits)
        else:
            st.success("ไม่พบ Interaction")