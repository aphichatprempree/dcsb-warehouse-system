import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(
    page_title="Daily Report Inventory Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 แดชบอร์ดสรุปสถานการณ์การรับสินค้า (กะเช้า)")
st.markdown("อ้างอิงโครงสร้างจากไฟล์ Excel: **รายงานประชุมเช้า.xlsx**")

# Sidebar สำหรับเลือกชีตและวันที่
st.sidebar.header("⚙️ ตัวเลือกการใช้งาน")
sheet_choice = st.sidebar.selectbox(
    "เลือกชีตข้อมูล (Sheet)",
    ["สถานการณ์การรับ(กะเช้า)", "ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม"],
)
report_date = st.sidebar.date_input("ประจำวันที่", value=pd.to_datetime("2026-11-12"))

if sheet_choice == "สถานการณ์การรับ(กะเช้า)":
  st.subheader(
      f"📌 สรุปงานรับและงานค้างส่ง ประจำวันที่ {report_date.strftime('%d/%m/%Y')}"
  )

  # ส่วนรับค่าข้อมูล (Input Form)
  col1, col2, col3, col4 = st.columns(4)

  with col1:
    inv_pallets = st.number_input(
        "ประมาณการรับ (Pallets)", value=6126, step=1
    )
  with col2:
    total_received = st.number_input(
        "งานรับทั้งหมด (16.10 น.)", value=5904, step=1
    )
  with col3:
    complete_pallets = st.number_input(
        "งาน Complete (22.00 น.)", value=5722, step=1
    )
  with col4:
    extra_work = st.number_input("งานนอกรอบ", value=138, step=1)

  st.markdown("---")
  st.markdown("### 🔍 สาเหตุงานไม่ได้รับ (Unreceived Reasons)")

  col5, col6, col7 = st.columns(3)
  with col5:
    not_received_po = st.number_input("ส่งไม่ครบตาม PO (Pallets)", value=73, step=1)
  with col6:
    not_billed = st.number_input("ยังไม่ยื่นบิล (Pallets)", value=250, step=1)
  with col7:
    delayed_delivery = st.number_input("เลื่อนส่ง (Pallets)", value=0, step=1)

  # คำนวณค่าอัตโนมัติ
  total_not_received = not_received_po + not_billed
  percent_not_received = (
      (total_not_received / total_received * 100) if total_received > 0 else 0
  )

  st.markdown("---")
  st.markdown("### 📈 ผลลัพธ์การสรุปภาพรวม")

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("งานรับทั้งหมด", f"{total_received:,} Pallets")
  m2.metric("งาน Complete", f"{complete_pallets:,} Pallets")
  m3.metric("งานไม่ได้รับรวม", f"{total_not_received:,} Pallets")
  m4.metric("คิดเป็นร้อยละ (%)", f"{percent_not_received:.2f}%")

  # แสดงแผนภูมิแท่งจำลอง (Bar Chart Breakdown)
  chart_data = pd.DataFrame({
      "ประเภทงาน": [
          "งานรับทั้งหมด (16.10น.)",
          "งาน Complete (22.00น.)",
          "งานนอกรอบ",
          "งานไม่ได้รับทั้งหมด",
          "ยังไม่ยื่นบิล",
          "ส่งไม่ครบตาม PO",
      ],
      "จำนวน (Pallets)": [
          total_received,
          complete_pallets,
          extra_work,
          total_not_received,
          not_billed,
          not_received_po,
      ],
  })

  st.bar_chart(chart_data.set_index("ประเภทงาน"))

else:
  st.info(
      "📁 ชีตที่ 2: สำหรับแสดงข้อมูลรายละเอียดเพิ่มเติมหรือประวัติย้อนหลัง (สามารถเชื่อมต่อไฟล์ Excel จริงบน GitHub ได้)"
  )
