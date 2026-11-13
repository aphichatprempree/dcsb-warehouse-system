import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(
    page_title="รายงานประชุมเช้า - DCSB Warehouse", page_icon="📊", layout="wide"
)

st.title("📊 แดชบอร์ดสรุปรายงานประชุมเช้า")
st.markdown("ระบบบันทึกและสรุปผลข้อมูลคลังสินค้า (แยกตามโครงสร้าง 2 เวิร์กชีต)")

# Sidebar เมนูเลือกชีตข้อมูล
st.sidebar.header("📁 เลือกมุมมองข้อมูล (Sheet)")
sheet_selection = st.sidebar.radio(
    "เลือกชีต:",
    [
        "สถานการณ์การรับ (กะเช้า)",
        "ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม",
    ],
)

st.sidebar.markdown("---")
report_date = st.sidebar.date_input(
    "ประจำวันที่", value=pd.to_datetime("2026-11-12")
)

# ==========================================
# ชีตที่ 1: สถานการณ์การรับ (กะเช้า)
# ==========================================
if sheet_selection == "สถานการณ์การรับ (กะเช้า)":
  st.subheader(
      f"📌 สถานการณ์การรับ (กะเช้า) ประจำวันที่ {report_date.strftime('%d/%m/%Y')}"
  )

  st.markdown("#### 1. ข้อมูลตั้งต้นและการรับสินค้า")
  col1, col2 = st.columns(2)
  with col1:
    inv_pallets = st.number_input(
        "ประมาณการรับ (Inventory Pallets)", value=6126, step=1
    )
  with col2:
    total_received = st.number_input(
        "งานรับทั้งหมด (16.10 น.) (Pallets)", value=5904, step=1
    )

  st.markdown("#### 2. สถานะงานรับสินค้า")
  col3, col4 = st.columns(2)
  with col3:
    complete_pallets = st.number_input(
        "งาน Complete (22.00 น.) (Pallets)", value=5722, step=1
    )
  with col4:
    extra_work = st.number_input(
        "งานนอกรอบ (Complete Pallets)", value=138, step=1
    )

  st.markdown("#### 3. รายละเอียดสาเหตุงานไม่ได้รับ")
  col5, col6, col7 = st.columns(3)
  with col5:
    not_received_po = st.number_input(
        "ส่งไม่ครบตาม PO (Pallets)", value=73, step=1
    )
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
  st.markdown("### 📈 สรุปผลการปฏิบัติงานภาพรวม")

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("งานรับทั้งหมด", f"{total_received:,} Pallets")
  m2.metric("งาน Complete", f"{complete_pallets:,} Pallets")
  m3.metric("งานไม่ได้รับรวม", f"{total_not_received:,} Pallets")
  m4.metric("คิดเป็นร้อยละ (%)", f"{percent_not_received:.2f}%")

  # กราฟแสดงสัดส่วน
  chart_df = pd.DataFrame({
      "ประเภทรายการ": [
          "งานรับทั้งหมด",
          "งาน Complete",
          "งานนอกรอบ",
          "งานไม่ได้รับรวม",
          "ยังไม่ยื่นบิล",
          "ส่งไม่ครบ PO",
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
  st.bar_chart(chart_df.set_index("ประเภทรายการ"))

# ==========================================
# ชีตที่ 2: ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม
# ==========================================
else:
  st.subheader("📋 ข้อมูลย้อนหลัง / รายละเอียดเพิ่มเติม (Sheet 2)")
  st.info(
      "ส่วนนี้ถูกจัดเตรียมไว้สำหรับบันทึกหรือดึงข้อมูลตารางประวัติย้อนหลัง"
      " หรือรายการรายละเอียดปลีกย่อยของแต่ละวัน"
  )

  # ตัวอย่างตารางจำลองข้อมูลย้อนหลัง
  history_data = pd.DataFrame({
      "วันที่": ["10/11/2026", "11/11/2026", "12/11/2026"],
      "ประมาณการรับ": [6000, 6100, 6126],
      "งานรับทั้งหมด": [5800, 5850, 5904],
      "งาน Complete": [5600, 5680, 5722],
      "งานไม่ได้รับ": [200, 170, 323],
  })

  st.dataframe(history_data, use_container_width=True)

  st.markdown("### ✏️ บันทึกหมายเหตุประจำวัน")
  daily_note = st.text_area(
      "หมายเหตุเพิ่มเติมสำหรับผู้บริหาร:",
      value="การรับสินค้าช่วงบ่ายมีความล่าช้าเล็กน้อยเนื่องจากระบบเครือข่ายขัดข้อง",
  )
  if st.button("บันทึกข้อมูลหมายเหตุ"):
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

5. เลื่อนลงมาด้านล่างสุด กดปุ่มเขียว **Commit changes...** เพื่อบันทึกทับไฟล์เดิมบน GitHub ได้เลยครับ

---

### 📦 ตรวจสอบไฟล์ `requirements.txt`
เพื่อให้แน่ใจว่าโปรแกรมรันได้สมบูรณ์ ให้เช็คว่าไฟล์ `requirements.txt` ใน GitHub มีข้อความนี้อยู่หรือไม่ (ถ้ายังไม่มี ให้กดเข้าไปแก้ไขเพิ่มได้เลยครับ):
```text
streamlit
pandas
