import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ดหลัก
st.set_page_config(
    page_title="DCSB Warehouse Central System",
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
    max-width: 1550px;
}
h1, h2, h3 { color: var(--forest); letter-spacing: -0.02em; }

[data-testid="stNumberInput"] > label {
    font-size: .88rem;
    font-weight: 500;
    color: #40564a;
}
[data-testid="stNumberInput"] input {
    border-radius: 10px;
    border-color: var(--line);
    background: white;
}
[data-testid="stNumberInput"] input:focus {
    border-color: var(--green);
    box-shadow: 0 0 0 1px var(--green);
}
.hero {
    background: linear-gradient(115deg, #174b3a 0%, #267653 72%, #438966 100%);
    border-radius: 20px;
    padding: 24px 30px;
    color: white;
    box-shadow: 0 12px 28px rgba(23, 75, 58, .14);
    margin-bottom: 22px;
}
.hero-kicker { color: #c8e1d1; font-size: .82rem; font-weight: 500; letter-spacing: .04em; }
.hero-title { color: white; font-size: 1.65rem; font-weight: 700; margin: 4px 0 2px; }
.hero-subtitle { color: #e0eee5; font-size: .92rem; }

.focus-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 22px;
}
.focus-card {
    background: linear-gradient(135deg, #ffffff 0%, #f6faf7 100%);
    border: 2px solid #b8d4c2;
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 8px 24px rgba(23, 75, 58, 0.08);
    position: relative;
    overflow: hidden;
}
.focus-card.alert {
    background: linear-gradient(135deg, #fffcfb 0%, #fef2f2 100%);
    border-color: #fca5a5;
}
.focus-label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #53685c;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.focus-card.alert .focus-label { color: #991b1b; }
.focus-value {
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--forest);
    line-height: 1.2;
    margin: 6px 0 2px;
}
.focus-card.alert .focus-value { color: #dc2626; }
.focus-unit {
    font-size: 0.88rem;
    color: var(--muted);
    font-weight: 500;
}

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
    font-size: 1.08rem;
    font-weight: 700;
}
.report-date { font-size: .82rem; font-weight: 500; color: #e0eee5; }
.report-grid {
    display: grid;
    grid-template-columns: repeat(13, minmax(0, 1fr));
    gap: 0;
}
.report-cell {
    border-right: 1px solid #d7e2d9;
    border-top: 1px solid #d7e2d9;
    padding: 9px 4px 8px;
    text-align: center;
    background: #fff;
    min-height: 76px;
    box-sizing: border-box;
}
.report-label { color: #53685c; font-size: .63rem; line-height: 1.2; min-height: 32px; font-weight: 500; }
.report-value { color: var(--forest); font-size: 1.05rem; font-weight: 700; line-height: 1.3; overflow-wrap: anywhere; }
.report-value.alert { color: #a4443d; }

.chart-title { color: var(--forest); font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; text-align: center; }
.summary-title { color: var(--forest); font-size: 1.2rem; font-weight: 700; margin: 22px 0 12px; }

@media (max-width: 1200px) {
    .report-grid { grid-template-columns: repeat(7, minmax(0, 1fr)); }
    .focus-grid { grid-template-columns: 1fr; }
}

.stButton > button {
    background: var(--green);
    color: white;
    border: 0;
    border-radius: 10px;
    font-weight: 600;
    padding: .55rem 1rem;
}
.stButton > button:hover { background: var(--forest); color: white; }
</style>
""",
    unsafe_allow_html=True,
)

# --- 📁 เมนูหลักสำหรับเลือกโปรแกรม (Central Hub) ---
st.sidebar.header("🗂️ เมนูระบบหลัก (Central Hub)")
main_app_selection = st.sidebar.radio(
    "เลือกโปรแกรม:",
    [
        "📊 รายงานการรับสินค้า (Morning Report)",
        "🔄 โปรแกรมประมวลผล / Real-time Utility",
    ],
)
st.sidebar.markdown("---")

# =========================================================================
# 📊 โปรแกรมที่ 1: รายงานการรับสินค้า (Morning Report)
# =========================================================================
if main_app_selection == "📊 รายงานการรับสินค้า (Morning Report)":
  st.sidebar.header("📁 เลือกมุมมองรายงาน")
  sheet_selection = st.sidebar.radio(
      "เลือกชีต:",
      [
          "สรุปงานรับและงานค้างส่ง(ย้อนหลัง)",
          "สถานการณ์การรับ(กะเช้าปัจจุบัน)",
      ],
  )
  st.sidebar.markdown("---")
  report_date = st.sidebar.date_input(
      "ประจำวันที่", value=pd.to_datetime("2026-11-12")
  )

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

  st.markdown(
      '<div class="hero"><div class="hero-kicker">DCSB WAREHOUSE · REPORT'
      ' SYSTEM</div><div class="hero-title">📊'
      " รายงานการรับสินค้าประจำวัน</div><div"
      ' class="hero-subtitle">ระบบสรุปยอดงานรับสินค้าและงานค้างรับคงเหลือ</div></div>',
      unsafe_allow_html=True,
  )

  # --- ชีต: สถานการณ์การรับ (กะเช้าปัจจุบัน) ---
  if sheet_selection == "สถานการณ์การรับ(กะเช้าปัจจุบัน)":
    inv_all = st.session_state.get("inv_all", 6058)
    night_received = st.session_state.get("night_received", 4240)
    morning_received = st.session_state.get("morning_received", 1818)
    complete_night = st.session_state.get("complete_night", 4475)
    work_night = st.session_state.get("work_night", 3507)
    work_morning = st.session_state.get("work_morning", 310)
    extra_work = st.session_state.get("extra_work", 658)

    pct_night_received = (
        (night_received / inv_all * 100) if inv_all > 0 else 0
    )
    total_remaining = st.session_state.get("total_remaining", 2425)
    recv_start = st.session_state.get("recv_start", 473)
    in_transit = st.session_state.get("in_transit", 268)
    sup_night_missing = st.session_state.get("sup_night_missing", 239)
    sup_morning_missing = st.session_state.get("sup_morning_missing", 1445)
    pct_remaining = (
        (total_remaining / inv_all * 100) if inv_all > 0 else 40.03
    )

    st.markdown(
        f"""
        <div class="focus-grid">
            <div class="focus-card">
                <div class="focus-label">📦 ยอดงาน Complete รับกะดึก (00.00-06.00)</div>
                <div class="focus-value">{complete_night:,} <span style="font-size: 1.5rem;">Pallets</span></div>
                <div class="focus-unit">ผลรวมงานสำเร็จในช่วงกะดึก</div>
            </div>
            <div class="focus-card alert">
                <div class="focus-label">🚨 Supplier ที่ยังไม่มาส่งกะเช้า</div>
                <div class="focus-value">{sup_morning_missing:,} <span style="font-size: 1.5rem;">Pallets</span></div>
                <div class="focus-unit">ยอดงานค้างส่งสูงสุดที่ต้องติดตามด่วน</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    report_values = [
        ("ยอดงานประมาณการรับทั้งหมด", f"{inv_all:,}", False),
        ("ยอดงานรับกะดึก (ทั้งหมด)", f"{night_received:,}", False),
        ("ยอดงานรับกะเช้า (ทั้งหมด)", f"{morning_received:,}", False),
        ("ยอดงาน Complete รับกะดึก (00.00-06.00)", f"{complete_night:,}", False),
        ("งาน Complete (00.00-06.00)\nงานกะดึก", f"{work_night:,}", False),
        ("งาน Complete (00.00-06.00)\nงานกะเช้า", f"{work_morning:,}", False),
        ("งาน Complete (00.00-06.00)\nงานนอกรอบ", f"{extra_work:,}", False),
        ("(%) สรุปยอดงานรับกะดึก", f"{pct_night_received:.2f}%", False),
        ("สรุปงานรับคงเหลือทั้งหมด (Pallets)", f"{total_remaining:,}", True),
        (
            "งานรับคงเหลือทั้งหมด\nกำลังลงสินค้า (Receiving Start)",
            f"{recv_start:,}",
            False,
        ),
        ("งานรับคงเหลือทั้งหมด\nรอลงสินค้า (InTransit)", f"{in_transit:,}", False),
        (
            "งานรับคงเหลือทั้งหมด\nSupplier ที่ยังไม่มาส่งกะดึก",
            f"{sup_night_missing:,}",
            False,
        ),
        (
            "งานรับคงเหลือทั้งหมด\nSupplier ที่ยังไม่มาส่งกะเช้า",
            f"{sup_morning_missing:,}",
            False,
        ),
        ("(%) สรุปงานค้างรับคงเหลือ", f"{pct_remaining:.2f}%", True),
    ]

    cells = "".join(
        f'<div class="report-cell"><div class="report-label">{label}</div>'
        f'<div class="report-value{" alert" if alert else ""}">{value}</div></div>'
        for label, value, alert in report_values
    )
    st.markdown(
        f'<div class="report-wrap"><div class="report-head">รายงานการรับสินค้าประจำวันที่'
        f' {report_date.strftime("%d/%m/%Y")} <span'
        f' class="report-date">(00.00 - 06.00 น.)</span></div><div'
        f' class="report-grid">{cells}</div></div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
      with st.container(border=True):
        st.markdown(
            '<div class="chart-title">ยอดงานประมาณการรับทั้งหมด</div>',
            unsafe_allow_html=True,
        )
        fig1 = px.pie(
            names=["ยอดงานประมาณการรับทั้งหมด", "ยอดงานรับกะดึก (ทั้งหมด)"],
            values=[inv_all, night_received],
            hole=0.6,
            color_discrete_sequence=["#27845c", "#a4443d"],
        )
        fig1.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
      with st.container(border=True):
        st.markdown(
            '<div class="chart-title">ยอดงาน Complete รับกะดึก'
            " (00.00-06.00)</div>",
            unsafe_allow_html=True,
        )
        fig2 = px.pie(
            names=["งานกะดึก", "งานกะเช้า", "งานนอกรอบ"],
            values=[work_night, work_morning, extra_work],
            hole=0.6,
            color_discrete_sequence=["#27845c", "#a4443d", "#82a957"],
        )
        fig2.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
      with st.container(border=True):
        st.markdown(
            '<div class="chart-title">สรุปงานรับคงเหลือทั้งหมด (Pallets)</div>',
            unsafe_allow_html=True,
        )
        fig3 = px.pie(
            names=[
                "กำลังลงสินค้า",
                "รอลงสินค้า",
                "Supplier กะดึก",
                "Supplier กะเช้า",
            ],
            values=[
                recv_start,
                in_transit,
                sup_night_missing,
                sup_morning_missing,
            ],
            hole=0.6,
            color_discrete_sequence=["#3b82f6", "#ef4444", "#10b981", "#8b5cf6"],
        )
        fig3.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
        '<div class="summary-title">✏️ ปรับปรุงข้อมูลรายงานประจำวัน</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
      col_a, col_b, col_c = st.columns(3)
      with col_a:
        inv_all = st.number_input(
            "ยอดงานประมาณการรับทั้งหมด", value=inv_all, step=1, key="inv_all"
        )
        night_received = st.number_input(
            "ยอดงานรับกะดึก (ทั้งหมด)",
            value=night_received,
            step=1,
            key="night_received",
        )
        morning_received = st.number_input(
            "ยอดงานรับกะเช้า (ทั้งหมด)",
            value=morning_received,
            step=1,
            key="morning_received",
        )
      with col_b:
        complete_night = st.number_input(
            "ยอดงาน Complete รับกะดึก",
            value=complete_night,
            step=1,
            key="complete_night",
        )
        work_night = st.number_input(
            "งาน Complete - กะดึก", value=work_night, step=1, key="work_night"
        )
        work_morning = st.number_input(
            "งาน Complete - กะเช้า",
            value=work_morning,
            step=1,
            key="work_morning",
        )
        extra_work = st.number_input(
            "งาน Complete - นอกรอบ", value=extra_work, step=1, key="extra_work"
        )
      with col_c:
        total_remaining = st.number_input(
            "สรุปงานรับคงเหลือทั้งหมด",
            value=total_remaining,
            step=1,
            key="total_remaining",
        )
        recv_start = st.number_input(
            "กำลังลงสินค้า (Receiving Start)",
            value=recv_start,
            step=1,
            key="recv_start",
        )
        in_transit = st.number_input(
            "รอลงสินค้า (InTransit)", value=in_transit, step=1, key="in_transit"
        )
        sup_night_missing = st.number_input(
            "Supplier ยังไม่มาส่งกะดึก",
            value=sup_night_missing,
            step=1,
            key="sup_night_missing",
        )
        sup_morning_missing = st.number_input(
            "Supplier ยังไม่มาส่งกะเช้า",
            value=sup_morning_missing,
            step=1,
            key="sup_morning_missing",
        )

  # --- ชีต: สรุปงานรับและงานค้างส่ง(ย้อนหลัง) (ปรับกราฟสไตล์ Sweet Excel พรีเมียม) ---
  else:
    st.subheader(
        f"📋 สรุปงานรับและงานค้างส่ง ประจำวันที่ {report_date.strftime('%d/%m/%Y')}"
        " (ย้อนหลัง)"
    )
    st.markdown(
        "แดชบอร์ดวิเคราะห์เชิงลึก ดีไซน์สไตล์ Sweet Excel พรีเมียม"
    )

    hist_inv = st.session_state.get("hist_inv", 6126)
    hist_total_recv = st.session_state.get("hist_total_recv", 5904)
    hist_complete = st.session_state.get("hist_complete", 5722)
    hist_extra = st.session_state.get("hist_extra", 138)
    hist_delayed = st.session_state.get("hist_delayed", 0)
    hist_not_po = st.session_state.get("hist_not_po", 73)
    hist_not_billed = st.session_state.get("hist_not_billed", 250)

    hist_not_recv = hist_delayed + hist_not_po + hist_not_billed
    hist_pct_not_recv = (
        (hist_not_recv / hist_total_recv * 100) if hist_total_recv > 0 else 0
    )

    hist_report_values = [
        ("ประมาณการรับ (Inventory)", f"{hist_inv:,}", False),
        ("งานรับทั้งหมด (16.10 น.)", f"{hist_total_recv:,}", False),
        ("งาน Complete (22.00 น.)", f"{hist_complete:,}", False),
        ("งานนอกรอบ Complete", f"{hist_extra:,}", False),
        ("งานไม่ได้รับ", f"{hist_not_recv:,}", True),
        ("งานไม่ได้รับ (%)", f"{hist_pct_not_recv:.2f}%", True),
        ("เลื่อนส่ง", f"{hist_delayed:,}", False),
        ("ส่งไม่ครบตาม PO", f"{hist_not_po:,}", False),
        ("ยังไม่ยื่นบิล", f"{hist_not_billed:,}", False),
        ("งานไม่ได้รับทั้งหมด", f"{hist_not_recv:,}", True),
    ]

    hist_cells = "".join(
        f'<div class="report-cell"><div class="report-label">{label}</div>'
        f'<div class="report-value{" alert" if alert else ""}">{value}</div></div>'
        for label, value, alert in hist_report_values
    )
    st.markdown(
        f'<div class="report-wrap"><div class="report-head">สรุปงานรับและงานค้างส่ง'
        f' ประจำวันที่ {report_date.strftime("%d/%m/%Y")} <span'
        f' class="report-date">(00.00-22.00 น.)</span></div><div'
        f' class="report-grid" style="grid-template-columns: repeat(10, minmax(0, 1fr));">{hist_cells}</div></div>',
        unsafe_allow_html=True,
    )

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
      with st.container(border=True):
        st.markdown(
            '<div class="chart-title">📊 สรุปภาพรวมงานรับ (สไตล์พรีเมียม)'
            "</div>",
            unsafe_allow_html=True,
        )
        df_bar_v = pd.DataFrame({
            "ประเภทงาน": [
                "งานรับทั้งหมด\n(16.10 น.)",
                "งาน Complete\n(22.00 น.)",
                "งานนอกรอบ",
                "งานไม่ได้รับ",
            ],
            "จำนวน (Pallets)": [
                hist_total_recv,
                hist_complete,
                hist_extra,
                hist_not_recv,
            ],
        })
        # กราฟสไตล์ Sweet Excel แท่งแคปซูล/โค้งมน โทนสีหรูหรา
        fig_v = go.Figure(
            data=[
                go.Bar(
                    x=df_bar_v["ประเภทงาน"],
                    y=df_bar_v["จำนวน (Pallets)"],
                    text=df_bar_v["จำนวน (Pallets)"],
                    textposition="outside",
                    marker=dict(
                        color=["#174b3a", "#eab308", "#d97706", "#dc2626"],
                        cornerRadius=12,
                        line=dict(width=2, color="white"),
                    ),
                )
            ]
        )
        fig_v.update_layout(
            margin=dict(t=35, b=20, l=20, r=20),
            showlegend=False,
            xaxis_title="",
            yaxis_title="จำนวน (Pallets)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Sans Thai", size=13),
        )
        st.plotly_chart(fig_v, use_container_width=True)

    with col_chart2:
      with st.container(border=True):
        st.markdown(
            '<div class="chart-title">🚨 วิเคราะห์สาเหตุงานไม่ได้รับ</div>',
            unsafe_allow_html=True,
        )
        df_bar_h = pd.DataFrame({
            "สาเหตุ": [
                "งานไม่ได้รับทั้งหมด",
                "ยังไม่ยื่นบิล",
                "ส่งไม่ครบตาม PO",
                "เลื่อนส่ง",
            ],
            "จำนวน (Pallets)": [
                hist_not_recv,
                hist_not_billed,
                hist_not_po,
                hist_delayed,
            ],
        })
        df_bar_h = df_bar_h.sort_values(by="จำนวน (Pallets)", ascending=True)
        fig_h = go.Figure(
            data=[
                go.Bar(
                    y=df_bar_h["สาเหตุ"],
                    x=df_bar_h["จำนวน (Pallets)"],
                    text=df_bar_h["จำนวน (Pallets)"],
                    textposition="outside",
                    orientation="h",
                    marker=dict(
                        color=["#94a3b8", "#facc15", "#10b981", "#fca5a5"],
                        cornerRadius=10,
                        line=dict(width=1.5, color="white"),
                    ),
                )
            ]
        )
        fig_h.update_layout(
            margin=dict(t=35, b=20, l=20, r=20),
            showlegend=False,
            xaxis_title="จำนวน (Pallets)",
            yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Sans Thai", size=13),
        )
        st.plotly_chart(fig_h, use_container_width=True)

    st.markdown(
        '<div class="summary-title">✏️ ปรับปรุงข้อมูลสรุปงานรับและงานค้างส่ง(ย้อนหลัง)</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
      hc1, hc2, hc3, hc4 = st.columns(4)
      with hc1:
        hist_inv = st.number_input(
            "ประมาณการรับ (Inventory)", value=hist_inv, step=1, key="hist_inv"
        )
        hist_total_recv = st.number_input(
            "งานรับทั้งหมด (16.10 น.)",
            value=hist_total_recv,
            step=1,
            key="hist_total_recv",
        )
      with hc2:
        hist_complete = st.number_input(
            "งาน Complete (22.00 น.)",
            value=hist_complete,
            step=1,
            key="hist_complete",
        )
        hist_extra = st.number_input(
            "งานนอกรอบ Complete", value=hist_extra, step=1, key="hist_extra"
        )
      with hc3:
        hist_delayed = st.number_input(
            "เลื่อนส่ง", value=hist_delayed, step=1, key="hist_delayed"
        )
        hist_not_po = st.number_input(
            "ส่งไม่ครบตาม PO", value=hist_not_po, step=1, key="hist_not_po"
        )
      with hc4:
        hist_not_billed = st.number_input(
            "ยังไม่ยื่นบิล", value=hist_not_billed, step=1, key="hist_not_billed"
        )

# =========================================================================
# 🔄 โปรแกรมที่ 2: โปรแกรมประมวลผล / Real-time Utility
# =========================================================================
else:
  st.markdown(
      '<div class="hero" style="background: linear-gradient(115deg, #1b3a4b 0%,'
      ' #28526f 72%, #3a7095 100%);"><div class="hero-kicker">REAL-TIME UTILITY'
      ' SYSTEM</div><div class="hero-title">🔄 โปรแกรมประมวลผล / Real-time'
      ' Utility</div><div class="hero-subtitle">ระบบประมวลผลข้อมูลและจัดการคิวแบบ'
      " Real-time</div></div>",
      unsafe_allow_html=True,
  )

  st.subheader("⚙️ แดชบอร์ดจัดการคิวและประมวลผลข้อมูล Real-time")
  st.info(
      "โปรแกรมนี้ถูกแยกการทำงานมาไว้ในระบบกลางอย่างเป็นระเบียบ ท่านสามารถอัปโหลด"
      "ไฟล์ข้อมูลหรือจัดการสถานะคิวได้ที่นี่"
  )

  col_r1, col_r2 = st.columns(2)
  with col_r1:
    with st.container(border=True):
      st.markdown("### 📥 อัปโหลดไฟล์ประมวลผล Real-time")
      uploaded_realtime = st.file_uploader(
          "เลือกไฟล์ Excel หรือ CSV", type=["xlsx", "csv"], key="rt_file"
      )
      if uploaded_realtime:
        st.success(f"อัปโหลดไฟล์ {uploaded_realtime.name} สำเร็จ")
  with col_r2:
    with st.container(border=True):
      st.markdown("### 📈 สถานะระบบเชื่อมต่อ")
      st.metric(
          label="สถานะเซิร์ฟเวอร์", value="Active / Online", delta="Real-time"
      )
      st.metric(
          label="คิวงานปัจจุบัน", value="0 รายการ", delta="พร้อมประมวลผล"
      )
        
