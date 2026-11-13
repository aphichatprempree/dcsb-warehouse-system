import pandas as pd
import streamlit as st


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
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: var(--forest); }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px; }
    h1, h2, h3 { color: var(--forest); letter-spacing: -0.02em; }
    h1 { font-size: 2rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.05rem !important; font-weight: 600 !important; }
    [data-testid="stRadio"] label, [data-testid="stDateInput"] label { color: var(--ink); }
    [data-testid="stNumberInput"] > label { font-size: .9rem; font-weight: 500; color: #40564a; }
    [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea {
        border-radius: 10px; border-color: var(--line); background: white;
    }
    [data-testid="stNumberInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: var(--green); box-shadow: 0 0 0 1px var(--green);
    }
    .hero {
        background: linear-gradient(115deg, #174b3a 0%, #267653 72%, #438966 100%);
        border-radius: 20px; padding: 26px 30px; color: white;
        box-shadow: 0 12px 28px rgba(23, 75, 58, .14); margin-bottom: 22px;
    }
    .hero-kicker { color: #c8e1d1; font-size: .82rem; font-weight: 500; letter-spacing: .04em; }
    .hero-title { color: white; font-size: 1.75rem; font-weight: 700; margin: 4px 0 2px; }
    .hero-subtitle { color: #e0eee5; font-size: .95rem; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white; border-color: var(--line) !important; border-radius: 16px !important;
        box-shadow: 0 4px 14px rgba(30, 67, 48, .035); margin: 14px 0;
    }
    .section-heading { color: var(--forest); font-size: 1.05rem; font-weight: 700; margin-bottom: 2px; }
    .section-caption { color: var(--muted); font-size: .84rem; margin-bottom: 12px; }
    .summary-title { color: var(--forest); font-size: 1.24rem; font-weight: 700; margin: 22px 0 12px; }
    .metric-card {
        min-height: 128px; height: 100%; box-sizing: border-box; padding: 17px 18px;
        border-radius: 15px; background: white; border: 1px solid var(--line);
        border-top: 4px solid var(--green); box-shadow: 0 5px 16px rgba(30, 67, 48, .055);
    }
    .metric-label { color: var(--muted); font-size: .88rem; font-weight: 500; }
    .metric-value { color: var(--forest); font-size: 1.72rem; font-weight: 700; line-height: 1.35; margin-top: 6px; }
    .metric-unit { color: var(--muted); font-size: .78rem; margin-top: 1px; }
    .metric-card.emphasis { background: #eaf4ee; border-color: #cce2d3; border-top-color: #174b3a; }
    .report-grid {
        display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin: 10px 0 22px;
    }
    .report-cell {
        border: 1px solid #d7e2d9; border-radius: 10px; padding: 10px 8px 9px;
        text-align: center; background: #fff; min-height: 72px; box-sizing: border-box;
    }
    .report-cell:nth-child(3n + 1) { background: #edf5ef; }
    .report-cell:nth-child(3n + 2) { background: #f6f8e9; }
    .report-cell:nth-child(3n) { background: #e8f3ee; }
    .report-label { color: #53685c; font-size: .76rem; line-height: 1.3; min-height: 30px; }
    .report-value { color: var(--forest); font-size: 1.35rem; font-weight: 700; line-height: 1.3; }
    .report-value.alert { color: #a4443d; }
    .chart-panel {
        background: white; border: 1px solid var(--line); border-radius: 16px;
        padding: 18px; min-height: 360px; box-shadow: 0 4px 14px rgba(30, 67, 48, .04);
    }
    .chart-title { color: var(--forest); font-size: 1.02rem; font-weight: 700; margin-bottom: 14px; }
    .vchart { display: flex; align-items: stretch; justify-content: space-around; gap: 12px; height: 275px; padding: 10px 4px 0; border-bottom: 1px solid #dce5de; }
    .vitem { flex: 1; min-width: 0; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; text-align: center; }
    .vvalue { font-size: .84rem; font-weight: 700; color: var(--ink); margin-bottom: 5px; }
    .vbar { width: min(54px, 72%); min-height: 4px; border-radius: 8px 8px 2px 2px; box-shadow: inset 0 -12px 18px rgba(0,0,0,.06); }
    .vlabel { min-height: 44px; padding-top: 8px; color: #52655a; font-size: .72rem; line-height: 1.25; }
    .hchart { display: flex; flex-direction: column; gap: 19px; padding: 9px 0; }
    .hrow { display: grid; grid-template-columns: minmax(90px, 36%) 1fr; gap: 9px; align-items: center; }
    .hlabel { color: #52655a; font-size: .77rem; line-height: 1.25; text-align: right; }
    .htrack { height: 29px; background: #f0f4f1; border-radius: 0 7px 7px 0; position: relative; }
    .hbar { height: 100%; min-width: 2px; border-radius: 0 7px 7px 0; display: flex; align-items: center; justify-content: flex-end; }
    .hvalue { position: absolute; top: 4px; color: #263b30; font-weight: 700; font-size: .85rem; white-space: nowrap; }
    .stButton > button {
        background: var(--green); color: white; border: 0; border-radius: 10px;
        font-weight: 600; padding: .55rem 1rem;
    }
    .stButton > button:hover { background: var(--forest); color: white; border-color: var(--forest); }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
    div[data-testid="stAlert"] { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(label: str, value: str, unit: str = "Pallets", emphasis: bool = False):
    variant = " emphasis" if emphasis else ""
    st.markdown(
        f'<div class="metric-card{variant}"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-unit">{unit}</div></div>',
        unsafe_allow_html=True,
    )


st.markdown(
    '<div class="hero"><div class="hero-kicker">DCSB WAREHOUSE · MORNING BRIEFING</div>'
    '<div class="hero-title">📊 แดชบอร์ดสรุปรายงานประชุมเช้า</div>'
    '<div class="hero-subtitle">ภาพรวมการรับสินค้าและข้อมูลประกอบการประชุมประจำวัน</div></div>',
    unsafe_allow_html=True,
)

st.sidebar.header("📁 เลือกมุมมองข้อมูล")
sheet_selection = st.sidebar.radio(
    "เลือกชีต:", ["สถานการณ์การรับ (กะเช้า)", "ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม"]
)
st.sidebar.markdown("---")
report_date = st.sidebar.date_input(
    "ประจำวันที่", value=pd.to_datetime("2026-11-12")
)
st.sidebar.caption("DCSB Warehouse · Morning Report")


if sheet_selection == "สถานการณ์การรับ (กะเช้า)":
    with st.container(border=True):
        st.markdown('<div class="section-heading">📌 สถานการณ์การรับสินค้า</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-caption">กะเช้า · ประจำวันที่ {report_date.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="section-heading">01 · ข้อมูลตั้งต้นและปริมาณรับสินค้า</div>'
                    '<div class="section-caption">เปรียบเทียบประมาณการกับยอดรับทั้งหมดของวัน</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            inv_pallets = st.number_input("ประมาณการรับ (Inventory Pallets)", value=6126, step=1)
        with col2:
            total_received = st.number_input("งานรับทั้งหมด (16.10 น.) (Pallets)", value=5904, step=1)

    with st.container(border=True):
        st.markdown('<div class="section-heading">02 · สถานะงานรับสินค้า</div>'
                    '<div class="section-caption">ติดตามงานที่เสร็จสมบูรณ์และงานรับนอกรอบ</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            complete_pallets = st.number_input("งาน Complete (22.00 น.) (Pallets)", value=5722, step=1)
        with col4:
            extra_work = st.number_input("งานนอกรอบ (Complete Pallets)", value=138, step=1)

    with st.container(border=True):
        st.markdown('<div class="section-heading">03 · รายละเอียดสาเหตุงานไม่ได้รับ</div>'
                    '<div class="section-caption">แยกสาเหตุเพื่อให้เห็นรายการที่ต้องติดตาม</div>', unsafe_allow_html=True)
        col5, col6, col7 = st.columns(3)
        with col5:
            not_received_po = st.number_input("ส่งไม่ครบตาม PO (Pallets)", value=73, step=1)
        with col6:
            not_billed = st.number_input("ยังไม่ยื่นบิล (Pallets)", value=250, step=1)
        with col7:
            delayed_delivery = st.number_input("เลื่อนส่ง (Pallets)", value=0, step=1)

    total_not_received = not_received_po + not_billed
    percent_not_received = (total_not_received / total_received * 100) if total_received > 0 else 0

    st.markdown('<div class="summary-title">📈 สรุปผลการปฏิบัติงานภาพรวม</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("งานรับทั้งหมด", f"{total_received:,}")
    with m2:
        metric_card("งาน Complete", f"{complete_pallets:,}")
    with m3:
        metric_card("งานไม่ได้รับรวม", f"{total_not_received:,}", emphasis=True)
    with m4:
        metric_card("คิดเป็นร้อยละ", f"{percent_not_received:.2f}", unit="% ของงานรับทั้งหมด", emphasis=True)
    st.markdown('<div class="summary-title">📊 สรุปยอดรายงานประจำวัน</div>', unsafe_allow_html=True)
    report_values = [
        ("ประมาณการรับ", f"{inv_pallets:,}", False),
        ("งานรับทั้งหมด", f"{total_received:,}", False),
        ("งาน Complete", f"{complete_pallets:,}", False),
        ("งานนอกรอบ", f"{extra_work:,}", False),
        ("งานไม่ได้รับ", f"{total_not_received:,}", True),
        ("งานไม่ได้รับ (%)", f"{percent_not_received:.2f}%", True),
        ("เลื่อนส่ง", f"{delayed_delivery:,}", False),
        ("ส่งไม่ครบ PO", f"{not_received_po:,}", False),
        ("ยังไม่ยื่นบิล", f"{not_billed:,}", False),
        ("ไม่ได้รับรวม", f"{total_not_received:,}", True),
    ]
    cells = "".join(
        f'<div class="report-cell"><div class="report-label">{label}</div>'
        f'<div class="report-value{" alert" if alert else ""}">{value}</div></div>'
        for label, value, alert in report_values
    )
    st.markdown(f'<div class="report-grid">{cells}</div>', unsafe_allow_html=True)

    chart_df = pd.DataFrame(
        {
            "ประเภทรายการ": [
                "งานรับทั้งหมด", "งาน Complete", "งานนอกรอบ", "งานไม่ได้รับรวม", "ยังไม่ยื่นบิล", "ส่งไม่ครบ PO"
            ],
            "จำนวน (Pallets)": [
                total_received, complete_pallets, extra_work, total_not_received, not_billed, not_received_po
            ],
        }
    left_chart, right_chart = st.columns([1.15, 1])
    receipt_items = [
        ("งานรับทั้งหมด", total_received, "#27845c"),
        ("งาน Complete", complete_pallets, "#82a957"),
        ("งานนอกรอบ", extra_work, "#d4a745"),
        ("งานไม่ได้รับ", total_not_received, "#c87568"),
    ]
    max_receipt = max((value for _, value, _ in receipt_items), default=1) or 1
    vertical_bars = "".join(
        f'<div class="vitem"><div class="vvalue">{value:,}</div>'
        f'<div class="vbar" style="height:{max(2, value / max_receipt * 72):.1f}%;background:{color}"></div>'
        f'<div class="vlabel">{label}</div></div>'
        for label, value, color in receipt_items
    )
    with st.container(border=True):
        st.markdown('<div class="section-heading">องค์ประกอบของรายงาน</div>'
                    '<div class="section-caption">กราฟเดิมสำหรับรอปรับตามไฟล์ต้นฉบับ</div>', unsafe_allow_html=True)
        st.bar_chart(chart_df.set_index("ประเภทรายการ"))
    reasons = [
        ("งานไม่ได้รับรวม", total_not_received, "#c87568"),
        ("ยังไม่ยื่นบิล", not_billed, "#27845c"),
        ("ส่งไม่ครบตาม PO", not_received_po, "#82a957"),
        ("เลื่อนส่ง", delayed_delivery, "#d4a745"),
    ]
    max_reason = max((value for _, value, _ in reasons), default=1) or 1
    horizontal_bars = "".join(
        f'<div class="hrow"><div class="hlabel">{label}</div><div class="htrack">'
        f'<div class="hbar" style="width:{max(1.2, value / max_reason * 88):.1f}%;background:{color}"></div>'
        f'<span class="hvalue" style="left:calc({max(1.2, value / max_reason * 88):.1f}% + 8px)">{value:,}</span>'
        '</div></div>'
        for label, value, color in reasons
    )
    with left_chart:
        st.markdown(f'<div class="chart-panel"><div class="chart-title">สรุปงานรับและงานค้าง</div>'
                    f'<div class="vchart">{vertical_bars}</div></div>', unsafe_allow_html=True)
    with right_chart:
        st.markdown(f'<div class="chart-panel"><div class="chart-title">สาเหตุงานไม่ได้รับ</div>'
                    f'<div class="hchart">{horizontal_bars}</div></div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="section-card"><div class="section-heading">📋 ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม</div>'
        '<div class="section-caption">Sheet 2 · ตารางข้อมูลและหมายเหตุประกอบรายวัน</div></div>',
        unsafe_allow_html=True,
    )
    st.info("ส่วนนี้จัดเตรียมไว้สำหรับบันทึกหรือดึงข้อมูลตารางประวัติย้อนหลัง และรายละเอียดปลีกย่อยของแต่ละวัน")

    history_data = pd.DataFrame(
        {
            "วันที่": ["10/11/2026", "11/11/2026", "12/11/2026"],
            "ประมาณการรับ": [6000, 6100, 6126],
            "งานรับทั้งหมด": [5800, 5850, 5904],
            "งาน Complete": [5600, 5680, 5722],
            "งานไม่ได้รับ": [200, 170, 323],
        }
    )
    with st.container(border=True):
        st.markdown('<div class="section-heading">ประวัติผลการรับสินค้า</div>'
                    '<div class="section-caption">ข้อมูลตัวอย่างรายวัน</div>', unsafe_allow_html=True)
        st.dataframe(history_data, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.markdown('<div class="section-heading">✏️ บันทึกหมายเหตุประจำวัน</div>'
                    '<div class="section-caption">เพิ่มข้อมูลประกอบสำหรับผู้บริหาร</div>', unsafe_allow_html=True)
        daily_note = st.text_area(
            "หมายเหตุเพิ่มเติมสำหรับผู้บริหาร:",
            value="การรับสินค้าช่วงบ่ายมีความล่าช้าเล็กน้อยเนื่องจากระบบเครือข่ายขัดข้อง",
        )
        if st.button("บันทึกข้อมูลหมายเหตุ"):
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
