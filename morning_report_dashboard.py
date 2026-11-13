import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(
    page_title="รายงานประชุมเช้า | DCSB Warehouse",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');
:root {
    --forest: #174b3a;
    --green: #27845c;
    --mint: #e8f3ed;
    --sage: #f4f8f5;
    --ink: #20342c;
    --muted: #6c7d73;
    --line: #dce8df;
    --white: #ffffff;
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'IBM Plex Sans Thai', sans-serif;
    color: var(--ink);
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f2f7f3 0%, #f8faf8 260px, #f8faf8 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: #edf4ef;
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--forest);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
h1, h2, h3 { color: var(--forest); letter-spacing: -0.02em; }
h1 { font-size: 2rem !important; font-weight: 700 !important; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; }

[data-testid="stNumberInput"] > label {
    font-size: .9rem;
    font-weight: 500;
    color: #40564a;
}
[data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea {
    border-radius: 10px;
    border-color: var(--line);
    background: white;
}
[data-testid="stNumberInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--green);
    box-shadow: 0 0 0 1px var(--green);
}
.hero {
    background: linear-gradient(115deg, #174b3a 0%, #267653 72%, #438966 100%);
    border-radius: 20px;
    padding: 26px 30px;
    color: white;
    box-shadow: 0 12px 28px rgba(23, 75, 58, .14);
    margin-bottom: 22px;
}
.hero-kicker { color: #c8e1d1; font-size: .82rem; font-weight: 500; letter-spacing: .04em; }
.hero-title { color: white; font-size: 1.75rem; font-weight: 700; margin: 4px 0 2px; }
.hero-subtitle { color: #e0eee5; font-size: .95rem; }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-color: var(--line) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(30, 67, 48, .035);
    margin: 14px 0;
}
.section-heading { color: var(--forest); font-size: 1.05rem; font-weight: 700; margin-bottom: 2px; }
.section-caption { color: var(--muted); font-size: .84rem; margin-bottom: 12px; }
.summary-title { color: var(--forest); font-size: 1.24rem; font-weight: 700; margin: 22px 0 12px; }

.report-wrap {
    background: white;
    border: 1px solid #c8d8cc;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 8px 22px rgba(23,75,58,.09);
    margin: 8px 0 22px;
}
.report-head {
    background: linear-gradient(100deg, #174b3a, #27845c);
    color: white;
    text-align: center;
    padding: 12px;
    font-size: 1.1rem;
    font-weight: 700;
}
.report-date { font-size: .82rem; font-weight: 500; color: #e0eee5; }
.report-grid {
    display: grid;
    grid-template-columns: repeat(10, minmax(0, 1fr));
    gap: 0;
}
.report-cell {
    border-right: 1px solid #d7e2d9;
    border-top: 1px solid #d7e2d9;
    padding: 9px 5px 8px;
    text-align: center;
    background: #fff;
    min-height: 76px;
    box-sizing: border-box;
}
.report-cell:nth-child(3n + 1) { background: #edf5ef; }
.report-cell:nth-child(3n + 2) { background: #f6f8e9; }
.report-cell:nth-child(3n) { background: #e8f3ee; }
.report-label { color: #53685c; font-size: .69rem; line-height: 1.25; min-height: 31px; }
.report-value { color: var(--forest); font-size: 1.12rem; font-weight: 700; line-height: 1.3; overflow-wrap: anywhere; }
.report-value.alert { color: #a4443d; }

.chart-panel {
    background: white;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 18px;
    min-height: 360px;
    box-shadow: 0 4px 14px rgba(30, 67, 48, .04);
}
.chart-title { color: var(--forest); font-size: 1.02rem; font-weight: 700; margin-bottom: 14px; }
.vchart {
    display: flex;
    align-items: stretch;
    justify-content: space-around;
    gap: 12px;
    height: 275px;
    padding: 10px 4px 0;
    border-bottom: 1px solid #dce5de;
}
.vitem {
    flex: 1;
    min-width: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    text-align: center;
}
.vvalue { font-size: .84rem; font-weight: 700; color: var(--ink); margin-bottom: 5px; }
.vbar {
    width: min(54px, 72%);
    min-height: 4px;
    border-radius: 8px 8px 2px 2px;
    box-shadow: inset 0 -12px 18px rgba(0,0,0,.06);
}
.vlabel { min-height: 44px; padding-top: 8px; color: #52655a; font-size: .72rem; line-height: 1.25; }

.hchart { display: flex; flex-direction: column; gap: 19px; padding: 9px 0; }
.hrow { display: grid; grid-template-columns: minmax(90px, 36%) 1fr; gap: 9px; align-items: center; }
.hlabel { color: #52655a; font-size: .77rem; line-height: 1.25; text-align: right; }
.htrack { height: 29px; background: #f0f4f1; border-radius: 0 7px 7px 0; position: relative; }
.hbar {
    height: 100%;
    min-width: 2px;
    border-radius: 0 7px 7px 0;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}
.hvalue {
    position: absolute;
    top: 4px;
    color: #263b30;
    font-weight: 700;
    font-size: .85rem;
    white-space: nowrap;
}

@media (max-width: 1100px) {
    .report-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); }
}

.stButton > button {
    background: var(--green);
    color: white;
    border: 0;
    border-radius: 10px;
    font-weight: 600;
    padding: .55rem 1rem;
}
.stButton > button:hover {
    background: var(--forest);
    color: white;
    border-color: var(--forest);
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stAlert"] { border-radius: 12px; }
</style>
""",
    unsafe_allow_html=True,
)


def metric_card(
    label: str, value: str, unit: str = "Pallets", emphasis: bool = False
):
  variant = " emphasis" if emphasis else ""
  st.markdown(
      f'<div class="metric-card{variant}"><div class="metric-label">{label}</div>'
      f'<div class="metric-value">{value}</div><div'
      f' class="metric-unit">{unit}</div></div>',
      unsafe_allow_html=True,
  )


st.markdown(
    '<div class="hero"><div class="hero-kicker">DCSB WAREHOUSE · MORNING'
    ' BRIEFING</div><div class="hero-title">📊'
    " สรุปงานรับและงานค้างส่ง(00.00-22.00 น.)</div><div"
    ' class="hero-subtitle">ภาพรวมการรับสินค้าและข้อมูลประกอบการประชุมประจำวัน</div></div>',
    unsafe_allow_html=True,
)

# เมนูด้านข้าง Sidebar
st.sidebar.header("📁 เลือกมุมมองข้อมูล")
sheet_selection = st.sidebar.radio(
    "เลือกชีต:",
    ["สถานการณ์การรับ (กะเช้า)", "ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม"],
)
st.sidebar.markdown("---")
report_date = st.sidebar.date_input(
    "ประจำวันที่", value=pd.to_datetime("2026-11-12")
)

# ส่วน Import ไฟล์รายงาน 3 ตัวใน Sidebar
st.sidebar.markdown("---")
st.sidebar.header("📥 Import ไฟล์รายงานระบบ")
uploaded_rp01 = st.sidebar.file_uploader(
    "อัปโหลดรายงาน RP01", type=["xlsx", "xls", "csv"], key="rp01"
)
uploaded_rp03 = st.sidebar.file_uploader(
    "อัปโหลดรายงาน RP03", type=["xlsx", "xls", "csv"], key="rp03"
)
uploaded_rp42 = st.sidebar.file_uploader(
    "อัปโหลดรายงาน RP42", type=["xlsx", "xls", "csv"], key="rp42"
)

df_rp01, df_rp03, df_rp42 = None, None, None
if uploaded_rp01:
  try:
    df_rp01 = (
        pd.read_csv(uploaded_rp01)
        if uploaded_rp01.name.endswith(".csv")
        else pd.read_excel(uploaded_rp01)
    )
    st.sidebar.success(f"RP01 สำเร็จ ({len(df_rp01):,} แถว)")
  except Exception as e:
    st.sidebar.error(f"RP01 Error: {e}")

if uploaded_rp03:
  try:
    df_rp03 = (
        pd.read_csv(uploaded_rp03)
        if uploaded_rp03.name.endswith(".csv")
        else pd.read_excel(uploaded_rp03)
    )
    st.sidebar.success(f"RP03 สำเร็จ ({len(df_rp03):,} แถว)")
  except Exception as e:
    st.sidebar.error(f"RP03 Error: {e}")

if uploaded_rp42:
  try:
    df_rp42 = (
        pd.read_csv(uploaded_rp42)
        if uploaded_rp42.name.endswith(".csv")
        else pd.read_excel(uploaded_rp42)
    )
    st.sidebar.success(f"RP42 สำเร็จ ({len(df_rp42):,} แถว)")
  except Exception as e:
    st.sidebar.error(f"RP42 Error: {e}")

st.sidebar.caption("DCSB Warehouse · Morning Report")

if sheet_selection == "สถานการณ์การรับ (กะเช้า)":
  with st.container(border=True):
    st.markdown(
        '<div class="section-heading">📌 สถานการณ์การรับสินค้า</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="section-caption">กะเช้า · ประจำวันที่'
        f' {report_date.strftime("%d/%m/%Y")}</div>',
        unsafe_allow_
