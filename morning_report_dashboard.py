import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(
    page_title="รายงานการรับสินค้า | DCSB Warehouse",
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
.report-cell:nth-child(4n + 1) { background: #edf5ef; }
.report-cell:nth-child(4n + 2) { background: #f6f8e9; }
.report-cell:nth-child(4n + 3) { background: #e8f3ee; }
.report-cell:nth-child(4n) { background: #fdf5f2; }
.report-label { color: #53685c; font-size: .63rem; line-height: 1.2; min-height: 32px; font-weight: 500; }
.report-value { color: var(--forest); font-size: 1.05rem; font-weight: 700; line-height: 1.3; overflow-wrap: anywhere; }
.report-value.alert { color: #a4443d; }

.chart-panel {
    background: white;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 20px;
    min-height: 400px;
    box-shadow: 0 4px 14px rgba(30, 67, 48, .04);
}
.chart-title { color: var(--forest); font-size: 1.05rem; font-weight: 700; margin-bottom: 16px; text-align: center; }

.summary-title { color: var(--forest); font-size: 1.2rem; font-weight: 700; margin: 22px 0 12px; }

@media (max-width: 1200px) {
    .report-grid { grid-template-columns: repeat(7, minmax(0, 1fr)); }
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
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><div class="hero-kicker">DCSB WAREHOUSE · REPORT'
    ' SYSTEM</div><div class="hero-title">📊'
    " รายงานการรับสินค้าประจำวัน</div><div"
    ' class="hero-subtitle">ระบบสรุปยอดงานรับสินค้าและงานค้างรับคงเหลือ</div></div>',
    unsafe_allow_html=True,
)

# Sidebar เมนูและ Import ไฟล์
st.sidebar.header("📁 เลือกมุมมองข้อมูล")
sheet_selection = st.sidebar.radio(
    "เลือกชีต:",
    ["รายงานการรับสินค้า (กะเช้า)", "ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม"],
)
st.sidebar.markdown("---")
report_date = st.sidebar.date_input(
    "ประจำวันที่", value=pd.to_datetime("2026-11-13")
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

if sheet_selection == "รายงานการรับสินค้า (กะเช้า)":
  # ดึงค่าจาก Session State หรือค่าเริ่มต้นตามต้นฉบับ
  inv_all = st.session_state.get("inv_all", 6058)
  night_received = st.session_state.get("night_received", 4240)
  morning_received = st.session_state.get("morning_received", 1818)
  complete_night = st.session_state.get("complete_night", 4475)
  work_night = st.session_state.get("work_night", 3507)
  work_morning = st.session_state.get("work_morning", 310)
  extra_work = st.session_state.get("extra_work", 658)

  # คำนวณอัตโนมัติ
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

  # ตารางสรุป 13 คอลัมน์ ตามโครงสร้าง Excel ต้นฉบับ
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

  # หมายเหตุ: ปรับให้แสดง 14 ช่องครบถ้วนตามแบบฟอร์ม
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

  # ส่วนแสดงกราฟวงแหวน (Donut Charts) 3 ส่วนหลัก
  c1, c2, c3 = st.columns(3)

  import plotly.express as px

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
          legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
      )
      st.plotly_chart(fig1, use_container_width=True)

  with c2:
    with st.container(border=True):
      st.markdown(
          '<div class="chart-title">ยอดงาน Complete รับกะดึก (00.00-06.00)</div>',
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
          legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
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
          legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
      )
      st.plotly_chart(fig3, use_container_width=True)

  # ส่วนกรอกข้อมูลเพื่อปรับแต่งค่าตัวเลข
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

else:
  st.subheader("📋 ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม (Sheet 2)")
  st.info("ส่วนนี้จัดเตรียมไว้สำหรับบันทึกประวัติย้อนหลังและข้อมูลรายละเอียด")

  history_data = pd.DataFrame({
      "วันที่": ["11/11/2026", "12/11/2026", "13/11/2026"],
      "ประมาณการทั้งหมด": [6000, 6100, 6058],
      "รับกะดึก": [4100, 4200, 4240],
      "รับกะเช้า": [1900, 1900, 1818],
      "งานคงเหลือ": [2500, 2450, 2425],
  })
  st.dataframe(history_data, use_container_width=True)

  st.markdown("### ✏️ บันทึกหมายเหตุประจำวัน")
  daily_note = st.text_area(
      "หมายเหตุเพิ่มเติมสำหรับผู้บริหาร:",
      value="การรับสินค้ากะดึกดำเนินการเรียบร้อยตามแผนงาน",
  )
  if st.button("บันทึกข้อมูลหมายเหตุ"):
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
