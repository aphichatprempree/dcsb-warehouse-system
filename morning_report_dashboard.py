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
[data-testid="stHeader"] {
    background: transparent;
}
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
h1, h2, h3 {
    color: var(--forest);
    letter-spacing: -0.02em;
}
h1 { font-size: 2rem !important; font-weight: 700 !important; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; }

[data-testid="stRadio"] label, [data-testid="stDateInput"] label {
    color: var(--ink);
}
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

.metric-card {
    min-height: 128px;
    height: 100%;
    box-sizing: border-box;
    padding: 17px 18px;
    border-radius: 15px;
    background: white;
    border: 1px solid var(--line);
    border-top: 4px solid var(--green);
    box-shadow: 0 5px 16px rgba(30, 67, 48, .055);
}
.metric-label { color: var(--muted); font-size: .88rem; font-weight: 500; }
.metric-value { color: var(--forest); font-size: 1.72rem; font-weight: 700; line-height: 1.35; margin-top: 6px; }
.metric-unit { color: var(--muted); font-size: .78rem; margin-top: 1px; }
.metric-card.emphasis {
    background: #eaf4ee;
    border-color: #cce2d3;
    border-top-color: #174b3a;
}
.report-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 8px;
    margin: 10px 0 22px;
}
.report-cell {
    border: 1px solid #d7e2d9;
    border-radius: 10px;
    padding: 10px 8px 9px;
    text-align: center;
    background: #fff;
    min-height: 72px;
    box-sizing: border-box;
}
.report-cell:nth-child(3n + 1) { background: #edf5ef; }
.report-cell:nth-child(3n + 2) { background: #f6f8e9; }
.report-cell:nth-child(3n) { background: #e8f3ee; }
.report-label { color: #53685c; font-size: .76rem; line-height: 1.3; min-height: 30px; }
.report-value { color: var(--forest); font-size: 1.35rem; font-weight: 700; line-height: 1.3; }
.report-value.alert { color: #a4443d; }
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
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}
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
    " แดชบอร์ดสรุปรายงานประชุมเช้า</div><div"
    ' class="hero-subtitle">ภาพรวมการรับสินค้าและข้อมูลประกอบการประชุมประจำวัน</div></div>',
    unsafe_allow_html=True,
)

st.sidebar.header("📁 เลือกมุมมองข้อมูล")
sheet_selection = st.sidebar.radio(
    "เลือกชีต:",
    ["สถานการณ์การรับ (กะเช้า)", "ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม"],
)
st.sidebar.markdown("---")
report_date = st.sidebar.date_input(
    "ประจำวันที่", value=pd.to_datetime("2026-11-12")
)
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
        unsafe_allow_html=True,
    )

    with st.container(border=True):
      st.markdown(
          '<div class="section-heading">01 · ข้อมูลตั้งต้นและปริมาณรับสินค้า</div>'
          '<div class="section-caption">เปรียบเทียบประมาณการกับยอดรับทั้งหมดของวัน</div>',
          unsafe_allow_html=True,
      )
      col1, col2 = st.columns(2)
      with col1:
        inv_pallets = st.number_input(
            "ประมาณการรับ (Inventory Pallets)", value=6126, step=1
        )
      with col2:
        total_received = st.
