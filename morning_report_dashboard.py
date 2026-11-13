import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ดหลัก
st.set_page_config(
    page_title="DCSB Warehouse Morning Report",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ชุดสีรุ้งตามตัวอย่าง (ส้ม > ชมพู > ม่วง > ฟ้า > เขียวมิ้นต์ > เขียวอ่อน > เหลือง > น้ำเงิน)
RAINBOW = [
    "#f59a0c",
    "#e8456f",
    "#a02a6f",
    "#4aa3e8",
    "#35c9a0",
    "#9be07a",
    "#f2c230",
    "#2a6f9e",
]
INK = "#2f3b42"
MUTED = "#7b8991"
FONT = "IBM Plex Sans Thai, sans-serif"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');
:root {
    --ink: #2f3b42;
    --muted: #7b8991;
    --line: #dfe6ea;
    --orange: #f59a0c;
    --pink: #e8456f;
    --purple: #a02a6f;
    --blue: #4aa3e8;
    --mint: #35c9a0;
    --navy: #2a6f9e;
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'IBM Plex Sans Thai', sans-serif;
    color: var(--ink);
}
/* พื้นหลังเทาอ่อนมีลายเส้นแนวนอนจาง ๆ เหมือนตัวอย่าง */
[data-testid="stAppViewContainer"] {
    background-color: #f1f3f4;
    background-image: repeating-linear-gradient(
        180deg, rgba(255,255,255,.75) 0, rgba(255,255,255,.75) 2px,
        rgba(0,0,0,0) 2px, rgba(0,0,0,0) 9px);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: #e9edef;
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--ink);
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
h1, h2, h3 { color: var(--ink); letter-spacing: -0.01em; }

[data-testid="stVerticalBlock"] { gap: 0.6rem; }
/* ----- แผ่นป้ายหัวข้อ (เหมือนกรอบชื่อกราฟในตัวอย่าง) ----- */
.hero {
    background: linear-gradient(180deg, #ffffff 0%, #f1f4f5 100%);
    border: 2px solid #b9c4ca;
    border-radius: 14px;
    padding: 18px 28px 16px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(60, 80, 90, .14), inset 0 1px 0 #fff;
    margin: 0 auto 4px;
    max-width: 980px;
}
.hero-kicker { color: var(--muted); font-size: .78rem; font-weight: 600; letter-spacing: .14em; }
.hero-title { color: var(--ink); font-size: 1.7rem; font-weight: 700; margin: 4px 0 2px; }
.hero-subtitle { color: var(--muted); font-size: .92rem; }
.hero-bar {
    height: 5px; border-radius: 3px; margin: 12px auto 0; max-width: 420px;
    background: linear-gradient(90deg, #f59a0c, #e8456f, #a02a6f, #4aa3e8, #35c9a0, #9be07a);
}
.page-sub {
    text-align: center; color: var(--muted); font-size: .9rem; margin: 2px 0 10px;
}

/* ----- ป้ายหัวข้อส่วนต่าง ๆ ----- */
.section-title {
    display: flex; align-items: center; gap: 12px;
    color: var(--ink); font-size: 1.15rem; font-weight: 700;
    margin: 14px 0 4px;
}
.section-title::before {
    content: ""; width: 6px; height: 24px; border-radius: 3px;
    background: linear-gradient(180deg, #f59a0c, #e8456f 50%, #4aa3e8);
}

/* ----- การ์ดโฟกัส ----- */
.focus-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 0;
}
.focus-card {
    background: linear-gradient(180deg, #ffffff 0%, #f4f6f7 100%);
    border: 1px solid #d3dce0;
    border-radius: 18px;
    padding: 16px 24px 16px 30px;
    box-shadow: 0 8px 20px rgba(60,80,90,.10), inset 0 1px 0 #fff;
    position: relative;
    overflow: hidden;
}
.focus-card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 10px;
    background: linear-gradient(180deg, #35c9a0, #4aa3e8);
}
.focus-card.alert::before { background: linear-gradient(180deg, #f59a0c, #e8456f); }
.focus-label { font-size: .92rem; font-weight: 600; color: var(--muted); }
.focus-value { font-size: 2.7rem; font-weight: 700; color: var(--navy); line-height: 1.2; margin: 8px 0 2px; }
.focus-card.alert .focus-value { color: var(--pink); }
.focus-value span { font-size: 1.3rem; font-weight: 600; color: var(--muted); }
.focus-unit { font-size: .85rem; color: var(--muted); font-weight: 500; }

/* ----- ตารางรายงาน ----- */
.report-wrap {
    background: #fff;
    border: 1px solid #d3dce0;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(60,80,90,.10);
    margin: 0;
}
.report-head {
    background: linear-gradient(180deg, #ffffff 0%, #eef1f3 100%);
    color: var(--ink);
    text-align: center;
    padding: 16px 12px 12px;
    font-size: 1.1rem;
    font-weight: 700;
    border-bottom: 1px solid #dfe6ea;
}
.report-date { font-size: .82rem; font-weight: 500; color: var(--muted); }
.report-grid { display: grid; gap: 0; }
.report-cell {
    border-right: 1px solid #e3e9ec;
    border-bottom: 1px solid #e3e9ec;
    padding: 10px 8px 8px;
    text-align: center;
    background: #fff;
    min-height: 84px;
    box-sizing: border-box;
}
.report-label { color: var(--muted); font-size: .7rem; line-height: 1.3; min-height: 36px; font-weight: 500; }
.report-value { color: var(--ink); font-size: 1.35rem; font-weight: 700; line-height: 1.3; overflow-wrap: anywhere; }
.report-value.alert { color: var(--pink); }

/* ----- การ์ดกราฟ / ฟอร์ม (container ที่ตั้ง key ขึ้นต้นด้วย card) ----- */
[class*="st-key-card"] {
    background: linear-gradient(180deg, #ffffff 0%, #f7f9fa 100%);
    border: 1px solid #d3dce0;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(60,80,90,.10), inset 0 1px 0 #fff;
    padding: 0.9rem 1rem 0.6rem;
}
.chart-title {
    color: var(--ink); font-size: 1.02rem; font-weight: 700;
    margin: 0 0 4px; text-align: center;
}
.chart-sub { color: var(--muted); font-size: .8rem; text-align: center; margin-bottom: 6px; }

@media (max-width: 1200px) {
    .report-grid { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }
    .focus-grid { grid-template-columns: 1fr; }
}

[data-testid="stNumberInput"] > label { font-size: .86rem; font-weight: 500; color: #4a5860; }
[data-testid="stNumberInput"] input { border-radius: 10px; border-color: var(--line); background: white; }
[data-testid="stNumberInput"] input:focus {
    border-color: var(--blue); box-shadow: 0 0 0 1px var(--blue);
}
.stButton > button {
    background: var(--navy); color: white; border: 0; border-radius: 10px;
    font-weight: 600; padding: .55rem 1rem;
}
.stButton > button:hover { background: var(--blue); color: white; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================================
# ฟังก์ชันวาดกราฟตามตัวอย่าง
# =========================================================================
def _pct(value, base):
    return (value / base * 100) if base and base > 0 else 0.0


def radial_chart(labels, values, base=None, height=440):
    """กราฟพัดครึ่งวงกลมสีรุ้ง (ตามตัวอย่างที่ 1) + ฟองเปอร์เซ็นต์ครึ่งซ้าย"""
    n = len(labels)
    base = base if base else sum(values)
    maxv = max(values) if max(values) > 0 else 1
    width = 180 / n
    colors = [RAINBOW[i % len(RAINBOW)] for i in range(n)]

    fig = go.Figure()

    # แผ่นครึ่งวงกลมซ้ายสีเทาอ่อน
    fig.add_trace(
        go.Barpolar(
            r=[1.12],
            theta=[180],
            width=[180],
            marker=dict(color="rgba(214,220,224,0.55)", line=dict(width=0)),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    # วงแหวนจาง ๆ ตกแต่ง
    fig.add_trace(
        go.Barpolar(
            r=[0.72],
            theta=[180],
            width=[180],
            marker=dict(color="rgba(255,255,255,0.55)", line=dict(width=0)),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # กลีบพัดฝั่งขวา
    for i, (lb, v) in enumerate(zip(labels, values)):
        center = 90 - width * (i + 0.5)
        r = 0.6 + 0.4 * (v / maxv)
        fig.add_trace(
            go.Barpolar(
                r=[r],
                theta=[center],
                width=[width],
                name=lb,
                marker=dict(color=colors[i], line=dict(color="white", width=2)),
                hovertemplate=f"{lb}<br>{v:,} Pallets<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[r - 0.09],
                theta=[center],
                mode="text",
                text=[f"{v:,}"],
                textfont=dict(color="white", size=14, family=FONT),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # ฟองเปอร์เซ็นต์ตามแนวโค้งด้านซ้าย
    if n == 1:
        angles = [180]
    else:
        angles = [100 + (160 / (n - 1)) * i for i in range(n)]
    fig.add_trace(
        go.Scatterpolar(
            r=[0.9] * n,
            theta=angles,
            mode="markers+text",
            text=[f"{_pct(v, base):.0f}%" for v in values],
            marker=dict(
                size=46,
                color="white",
                line=dict(color=colors, width=3),
            ),
            textfont=dict(color=colors, size=12, family=FONT),
            hovertext=labels,
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=height,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            hole=0.16,
            radialaxis=dict(visible=False, range=[0, 1.12]),
            angularaxis=dict(
                visible=False, rotation=0, direction="counterclockwise"
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
        ),
        annotations=[
            dict(
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                text="<b>REPORT</b>",
                showarrow=False,
                font=dict(size=10, color=MUTED),
            )
        ],
    )
    return fig


def tube_chart(labels, values, base, height=520):
    """กราฟหลอดแท่งเงา + เส้นประเปอร์เซ็นต์ด้านบน (ตามตัวอย่างที่ 2)"""
    n = len(labels)
    colors = [RAINBOW[i % len(RAINBOW)] for i in range(n)]
    xs = list(range(n))
    maxv = max(values) if max(values) > 0 else 1
    bg_max = maxv * 1.08
    pcts = [_pct(v, base) for v in values]

    fig = go.Figure()

    # หลอดแก้วด้านหลัง
    fig.add_trace(
        go.Bar(
            x=xs,
            y=[bg_max] * n,
            width=0.68,
            marker=dict(
                color="rgba(255,255,255,0.95)",
                line=dict(color="#b7c4ca", width=3),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    # แท่งสีด้านใน
    fig.add_trace(
        go.Bar(
            x=xs,
            y=values,
            width=0.52,
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,.7)", width=1)),
            text=[f"{v:,}" for v in values],
            textposition="inside",
            insidetextanchor="middle",
            textangle=-90,
            textfont=dict(color="white", size=14, family=FONT),
            customdata=[[lb, p] for lb, p in zip(labels, pcts)],
            hovertemplate="%{customdata[0]}<br>%{y:,} Pallets (%{customdata[1]:.1f}%)<extra></extra>",
            showlegend=False,
        )
    )
    # แถบเงาสะท้อน
    fig.add_trace(
        go.Bar(
            x=[x - 0.17 for x in xs],
            y=[v * 0.95 for v in values],
            width=0.07,
            marker=dict(color="rgba(255,255,255,0.38)", line=dict(width=0)),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # เส้นประแสดงเปอร์เซ็นต์ (แกน y2 อยู่ด้านบน)
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=pcts,
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#4b5860", width=2, dash="dash"),
            marker=dict(
                size=13, symbol="square", color=colors,
                line=dict(color="white", width=2),
            ),
            hovertemplate="%{y:.1f}%<extra></extra>",
            showlegend=False,
        )
    )
    lo, hi = min(pcts), max(pcts)
    span = max(hi - lo, 10)
    annotations = [
        dict(
            x=x,
            y=p,
            xref="x",
            yref="y2",
            text=f"<b>{p:.0f}%</b>",
            showarrow=False,
            yshift=26,
            bgcolor="white",
            bordercolor="#9fb0b8",
            borderwidth=1,
            borderpad=3,
            font=dict(size=12, color=INK, family=FONT),
        )
        for x, p in zip(xs, pcts)
    ]

    fig.update_layout(
        height=height,
        barmode="overlay",
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK),
        showlegend=False,
        annotations=annotations,
        xaxis=dict(
            tickmode="array",
            tickvals=xs,
            ticktext=[lb.replace(" ", "<br>", 1) if len(lb) > 12 else lb for lb in labels],
            tickfont=dict(size=12),
            range=[-0.6, n - 0.4],
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            domain=[0, 0.64],
            range=[0, bg_max],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis2=dict(
            domain=[0.76, 1],
            range=[lo - span * 0.6, hi + span * 0.7],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
    )
    # มุมโค้งของหลอด (รองรับใน Plotly รุ่นใหม่)
    try:
        fig.update_traces(marker_cornerradius=18, selector=dict(type="bar"))
    except Exception:
        pass
    return fig


def report_table(title, date_str, time_str, items, cols):
    cells = "".join(
        f'<div class="report-cell" style="border-top:4px solid {RAINBOW[i % len(RAINBOW)]};">'
        f'<div class="report-label">{label.replace(chr(10), "<br>")}</div>'
        f'<div class="report-value{" alert" if alert else ""}">{value}</div></div>'
        for i, (label, value, alert) in enumerate(items)
    )
    return (
        f'<div class="report-wrap"><div class="report-head">{title} {date_str}'
        f' <span class="report-date">{time_str}</span></div>'
        f'<div class="report-grid" style="grid-template-columns: repeat({cols}, minmax(0, 1fr));">'
        f"{cells}</div></div>"
    )


def chart_card_title(title, sub=""):
    sub_html = f'<div class="chart-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="chart-title">{title}</div>{sub_html}',
        unsafe_allow_html=True,
    )


# --- Sidebar เมนูเลือกชีตรายงาน ---
st.sidebar.header("📁 เลือกมุมมองรายงาน")
sheet_selection = st.sidebar.radio(
    "เลือกชีต:",
    [
        "สรุปงานรับและงานค้างส่ง(ย้อนหลัง)",
        "สถานการณ์การรับ(กะเช้าปัจจุบัน)",
    ],
)
st.sidebar.markdown("---")

# แยกตัวเลือกวันที่ของแต่ละชีตให้อิสระจากกันอย่างชัดเจน
if sheet_selection == "สถานการณ์การรับ(กะเช้าปัจจุบัน)":
    morning_date = st.sidebar.date_input(
        "ประจำวันที่ (กะเช้าปัจจุบัน)",
        value=pd.to_datetime("2026-11-13"),
        key="m_date_input",
    )
else:
    hist_date = st.sidebar.date_input(
        "ประจำวันที่ (ย้อนหลัง)",
        value=pd.to_datetime("2026-11-12"),
        key="h_date_input",
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
    '<div class="hero"><div class="hero-kicker">DCSB WAREHOUSE · REPORT SYSTEM</div>'
    '<div class="hero-title">📊 รายงานการรับสินค้าประจำวัน</div>'
    '<div class="hero-subtitle">ระบบสรุปยอดงานรับสินค้าและงานค้างรับคงเหลือ</div>'
    '<div class="hero-bar"></div></div>'
    '<div class="page-sub">Daily receiving summary dashboard</div>',
    unsafe_allow_html=True,
)

# =========================================================================
# ชีตที่ 1: สถานการณ์การรับ (กะเช้าปัจจุบัน)
# =========================================================================
if sheet_selection == "สถานการณ์การรับ(กะเช้าปัจจุบัน)":
    inv_all = st.session_state.get("inv_all", 6058)
    night_received = st.session_state.get("night_received", 4240)
    morning_received = st.session_state.get("morning_received", 1818)
    complete_night = st.session_state.get("complete_night", 4475)
    work_night = st.session_state.get("work_night", 3507)
    work_morning = st.session_state.get("work_morning", 310)
    extra_work = st.session_state.get("extra_work", 658)

    pct_night_received = (night_received / inv_all * 100) if inv_all > 0 else 0
    total_remaining = st.session_state.get("total_remaining", 2425)
    recv_start = st.session_state.get("recv_start", 473)
    in_transit = st.session_state.get("in_transit", 268)
    sup_night_missing = st.session_state.get("sup_night_missing", 239)
    sup_morning_missing = st.session_state.get("sup_morning_missing", 1445)
    pct_remaining = (total_remaining / inv_all * 100) if inv_all > 0 else 40.03

    st.markdown(
        f"""
    <div class="focus-grid">
        <div class="focus-card">
            <div class="focus-label">📦 ยอดงาน Complete รับกะดึก (00.00-06.00)</div>
            <div class="focus-value">{complete_night:,} <span>Pallets</span></div>
            <div class="focus-unit">ผลรวมงานสำเร็จในช่วงกะดึก</div>
        </div>
        <div class="focus-card alert">
            <div class="focus-label">🚨 Supplier ที่ยังไม่มาส่งกะเช้า</div>
            <div class="focus-value">{sup_morning_missing:,} <span>Pallets</span></div>
            <div class="focus-unit">ยอดงานค้างส่งสูงสุดที่ต้องติดตามด่วน</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">ตารางสรุปรายงาน</div>', unsafe_allow_html=True)
    report_values = [
        ("ยอดงานประมาณการรับทั้งหมด", f"{inv_all:,}", False),
        ("ยอดงานรับกะดึก (ทั้งหมด)", f"{night_received:,}", False),
        ("ยอดงานรับกะเช้า (ทั้งหมด)", f"{morning_received:,}", False),
        ("ยอดงาน Complete รับกะดึก\n(00.00-06.00)", f"{complete_night:,}", False),
        ("งาน Complete (00.00-06.00)\nงานกะดึก", f"{work_night:,}", False),
        ("งาน Complete (00.00-06.00)\nงานกะเช้า", f"{work_morning:,}", False),
        ("งาน Complete (00.00-06.00)\nงานนอกรอบ", f"{extra_work:,}", False),
        ("(%) สรุปยอดงานรับกะดึก", f"{pct_night_received:.2f}%", False),
        ("สรุปงานรับคงเหลือทั้งหมด\n(Pallets)", f"{total_remaining:,}", True),
        ("งานรับคงเหลือทั้งหมด\nกำลังลงสินค้า (Receiving Start)", f"{recv_start:,}", False),
        ("งานรับคงเหลือทั้งหมด\nรอลงสินค้า (InTransit)", f"{in_transit:,}", False),
        ("งานรับคงเหลือทั้งหมด\nSupplier ที่ยังไม่มาส่งกะดึก", f"{sup_night_missing:,}", False),
        ("งานรับคงเหลือทั้งหมด\nSupplier ที่ยังไม่มาส่งกะเช้า", f"{sup_morning_missing:,}", False),
        ("(%) สรุปงานค้างรับคงเหลือ", f"{pct_remaining:.2f}%", True),
    ]
    st.markdown(
        report_table(
            "รายงานการรับสินค้าประจำวันที่",
            morning_date.strftime("%d/%m/%Y"),
            "(00.00 - 06.00 น.)",
            report_values,
            7,
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">กราฟสรุปภาพรวม</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        with st.container(key="card_radial_1"):
            chart_card_title("สัดส่วนงานรับเทียบประมาณการ", "% เทียบยอดประมาณการรับทั้งหมด")
            st.plotly_chart(
                radial_chart(
                    ["รับกะดึก", "รับกะเช้า", "คงเหลือทั้งหมด"],
                    [night_received, morning_received, total_remaining],
                    base=inv_all,
                ),
                use_container_width=True,
            )
    with c2:
        with st.container(key="card_radial_2"):
            chart_card_title("ยอดงาน Complete รับกะดึก", "(00.00-06.00) แยกตามประเภทงาน")
            st.plotly_chart(
                radial_chart(
                    ["งานกะดึก", "งานกะเช้า", "งานนอกรอบ"],
                    [work_night, work_morning, extra_work],
                ),
                use_container_width=True,
            )
    with c3:
        with st.container(key="card_radial_3"):
            chart_card_title("สรุปงานรับคงเหลือทั้งหมด", "หน่วย Pallets แยกตามสถานะ")
            st.plotly_chart(
                radial_chart(
                    ["กำลังลงสินค้า", "รอลงสินค้า", "Supplier กะดึก", "Supplier กะเช้า"],
                    [recv_start, in_transit, sup_night_missing, sup_morning_missing],
                ),
                use_container_width=True,
            )

    st.markdown(
        '<div class="section-title">✏️ ปรับปรุงข้อมูลรายงานประจำวัน</div>',
        unsafe_allow_html=True,
    )
    with st.container(key="card_edit"):
        col_a, col_b, col_c = st.columns(3, gap="small")
        with col_a:
            inv_all = st.number_input(
                "ยอดงานประมาณการรับทั้งหมด", value=inv_all, step=1, key="inv_all"
            )
            night_received = st.number_input(
                "ยอดงานรับกะดึก (ทั้งหมด)", value=night_received, step=1, key="night_received"
            )
            morning_received = st.number_input(
                "ยอดงานรับกะเช้า (ทั้งหมด)", value=morning_received, step=1, key="morning_received"
            )
        with col_b:
            complete_night = st.number_input(
                "ยอดงาน Complete รับกะดึก", value=complete_night, step=1, key="complete_night"
            )
            work_night = st.number_input(
                "งาน Complete - กะดึก", value=work_night, step=1, key="work_night"
            )
            work_morning = st.number_input(
                "งาน Complete - กะเช้า", value=work_morning, step=1, key="work_morning"
            )
            extra_work = st.number_input(
                "งาน Complete - นอกรอบ", value=extra_work, step=1, key="extra_work"
            )
        with col_c:
            total_remaining = st.number_input(
                "สรุปงานรับคงเหลือทั้งหมด", value=total_remaining, step=1, key="total_remaining"
            )
            recv_start = st.number_input(
                "กำลังลงสินค้า (Receiving Start)", value=recv_start, step=1, key="recv_start"
            )
            in_transit = st.number_input(
                "รอลงสินค้า (InTransit)", value=in_transit, step=1, key="in_transit"
            )
            sup_night_missing = st.number_input(
                "Supplier ยังไม่มาส่งกะดึก", value=sup_night_missing, step=1, key="sup_night_missing"
            )
            sup_morning_missing = st.number_input(
                "Supplier ยังไม่มาส่งกะเช้า", value=sup_morning_missing, step=1, key="sup_morning_missing"
            )

# =========================================================================
# ชีตที่ 2: สรุปงานรับและงานค้างส่ง(ย้อนหลัง)
# =========================================================================
else:
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

    st.markdown(
        '<div class="section-title">ตารางสรุปรายงาน</div>', unsafe_allow_html=True
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
    st.markdown(
        report_table(
            "สรุปงานรับและงานค้างส่ง ประจำวันที่",
            hist_date.strftime("%d/%m/%Y"),
            "(00.00-22.00 น.)",
            hist_report_values,
            5,
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">กราฟสรุปภาพรวม</div>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns([1.35, 1], gap="small")
    with col_chart1:
        with st.container(key="card_hist_tube"):
            chart_card_title(
                "📊 สรุปภาพรวมงานรับและงานค้างส่ง",
                "เส้นประแสดง % เทียบงานรับทั้งหมด (16.10 น.)",
            )
            st.plotly_chart(
                tube_chart(
                    ["งานรับทั้งหมด", "งาน Complete", "งานนอกรอบ", "งานไม่ได้รับ"],
                    [hist_total_recv, hist_complete, hist_extra, hist_not_recv],
                    base=hist_total_recv,
                    height=500,
                ),
                use_container_width=True,
            )
    with col_chart2:
        with st.container(key="card_hist_radial"):
            chart_card_title(
                "🚨 วิเคราะห์สาเหตุงานไม่ได้รับ",
                "% เทียบงานไม่ได้รับทั้งหมด",
            )
            st.plotly_chart(
                radial_chart(
                    ["ยังไม่ยื่นบิล", "ส่งไม่ครบตาม PO", "เลื่อนส่ง"],
                    [hist_not_billed, hist_not_po, hist_delayed],
                    base=hist_not_recv,
                    height=500,
                ),
                use_container_width=True,
            )

    st.markdown(
        '<div class="section-title">✏️ ปรับปรุงข้อมูลสรุปงานรับและงานค้างส่ง(ย้อนหลัง)</div>',
        unsafe_allow_html=True,
    )
    with st.container(key="card_edit_hist"):
        hc1, hc2, hc3, hc4 = st.columns(4, gap="small")
        with hc1:
            hist_inv = st.number_input(
                "ประมาณการรับ (Inventory)", value=hist_inv, step=1, key="hist_inv"
            )
            hist_total_recv = st.number_input(
                "งานรับทั้งหมด (16.10 น.)", value=hist_total_recv, step=1, key="hist_total_recv"
            )
        with hc2:
            hist_complete = st.number_input(
                "งาน Complete (22.00 น.)", value=hist_complete, step=1, key="hist_complete"
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
