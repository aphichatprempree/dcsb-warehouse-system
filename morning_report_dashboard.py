import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ตั้งค่าหน้าเว็บแดชบอร์ดหลัก
st.set_page_config(
    page_title="DCSB Warehouse Morning Report",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ชุดสีโทนน้ำเงิน-เทาฟ้า ตามธีม Soft UI
RAINBOW = [
    "#3a3dff", "#2e8bff", "#7b6cff", "#8d9bb3",
    "#27b3d6", "#5b6b8c", "#9aa8ff", "#b4bfd0",
]
INK = "#2d3650"
MUTED = "#8590a6"
FONT = "IBM Plex Sans Thai, sans-serif"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');
:root {
    --ink:#2d3650; --muted:#8590a6; --bg:#e4e9f1; --bg2:#eef2f8;
    --blue:#3a3dff; --blue2:#2e8bff; --rose:#e0536a;
    --sh: 8px 8px 18px rgba(163,177,198,.55), -8px -8px 18px rgba(255,255,255,.95);
    --sh-sm: 5px 5px 11px rgba(163,177,198,.5), -5px -5px 11px rgba(255,255,255,.95);
    --sh-in: inset 4px 4px 9px rgba(163,177,198,.45), inset -4px -4px 9px rgba(255,255,255,.9);
    --grad: linear-gradient(135deg,#3a3dff,#2e8bff);
    --line:#9aaccb; --line-strong:#5f77a6;
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family:'IBM Plex Sans Thai',sans-serif; color:var(--ink); }
[data-testid="stAppViewContainer"] { background: linear-gradient(145deg,#e9eef5,#dde4ee); }
[data-testid="stHeader"] { background:transparent; height:2.2rem; }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer { display:none !important; }
.block-container { padding:.6rem 1.4rem 1rem; max-width:1700px; }
h1,h2,h3 { color:var(--ink); letter-spacing:-.02em; }
[data-testid="stVerticalBlock"] { gap:.55rem; }

/* ---------- HERO ---------- */
.hero { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border-radius:26px; padding:14px 26px 12px; text-align:center; box-shadow:var(--sh); border:2px solid var(--line-strong); margin:0 auto 8px; max-width:1000px; }
.hero-kicker { color:var(--blue2); font-size:.68rem; font-weight:600; letter-spacing:.2em; }
.hero-title { color:var(--ink); font-size:1.5rem; font-weight:700; margin:2px 0 0; }
.hero-subtitle { color:var(--muted); font-size:.82rem; }
.hero-bar { height:4px; border-radius:4px; margin:9px auto 0; max-width:200px; background:var(--grad); box-shadow:0 3px 8px rgba(58,61,255,.3); }
.page-sub { display:none; }
.section-title { display:flex; align-items:center; gap:10px; color:var(--ink); font-size:1rem; font-weight:700; margin:14px 0 4px; padding-bottom:6px; border-bottom:2px solid var(--line); }
.section-title::before { content:""; width:5px; height:20px; border-radius:5px; background:var(--grad); box-shadow:0 2px 7px rgba(58,61,255,.3); }

/* ---------- FOCUS CARDS ---------- */
.focus-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; margin:6px 0 6px; }
.focus-card { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border-radius:24px; padding:16px 24px 14px 30px; box-shadow:var(--sh); border:2px solid var(--line-strong); position:relative; overflow:hidden; }
.focus-card::before { content:""; position:absolute; left:0; top:16px; bottom:16px; width:5px; border-radius:0 5px 5px 0; background:var(--grad); }
.focus-card.alert::before { background:linear-gradient(180deg,#ffb35c,#e0536a); }
.focus-label { font-size:.82rem; font-weight:600; color:var(--muted); }
.focus-value { font-size:2.1rem; font-weight:700; color:var(--blue); line-height:1.25; margin:6px 0 4px; font-variant-numeric:tabular-nums; }
.focus-card.alert .focus-value { color:var(--rose); }
.focus-value span { font-size:.95rem; font-weight:600; color:var(--muted); }
.focus-unit { font-size:.74rem; color:var(--muted); font-weight:500; }

/* ---------- REPORT TABLE ---------- */
.report-wrap { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border-radius:24px; overflow:hidden; box-shadow:var(--sh); border:2px solid var(--line-strong); padding:8px 10px 14px; }
.report-head { color:var(--ink); text-align:left; padding:8px 14px 10px; margin-bottom:6px; border-bottom:2px solid var(--line); font-size:.92rem; font-weight:700; }
.report-date { font-size:.74rem; font-weight:500; color:var(--muted); margin-left:5px; }
.report-grid { display:grid; gap:12px; padding:4px 6px; }
.report-cell { border-radius:16px; padding:10px 8px 10px; text-align:center; background:#f1f4f9; box-shadow:var(--sh-sm); border:1.5px solid var(--line); min-height:84px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:space-between; gap:6px; }
.report-label { color:#5d6987; font-size:.66rem; line-height:1.35; font-weight:500; }
.report-value { color:var(--ink); font-size:1.15rem; font-weight:700; line-height:1.3; overflow-wrap:anywhere; font-variant-numeric:tabular-nums; }
.report-value.alert { color:var(--rose); }

/* ---------- CHART CARDS ---------- */
[class*="st-key-card"] { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border-radius:26px; box-shadow:var(--sh); padding:.8rem .9rem .6rem; border:2px solid var(--line-strong); }
.chart-title { color:var(--ink); font-size:.92rem; font-weight:700; margin:0 0 4px; text-align:center; }
.chart-sub { color:var(--muted); font-size:.7rem; text-align:center; margin-bottom:6px; padding-bottom:6px; border-bottom:1.5px dashed var(--line); }
@media (max-width:1200px) { .report-grid { grid-template-columns:repeat(4,minmax(0,1fr)) !important; } .focus-grid { grid-template-columns:1fr; } }
@media (max-width:700px) { .hero-title{font-size:1.25rem} .report-grid{grid-template-columns:repeat(2,minmax(0,1fr)) !important} .focus-value{font-size:1.8rem} }

/* ---------- EXPANDER + INPUTS ---------- */
[data-testid="stExpander"] { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border:2px solid var(--line-strong) !important; border-radius:22px; box-shadow:var(--sh-sm); }
[data-testid="stExpander"] summary p { font-weight:700; color:var(--ink); }
[data-testid="stNumberInput"] > label p { font-size:.8rem; font-weight:600; color:#56627d; }
[data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="base-input"] { background:#e6ebf3 !important; border:1.5px solid var(--line) !important; border-radius:12px; box-shadow:var(--sh-in); }
[data-testid="stNumberInput"] input { color:var(--ink); background:transparent !important; }
[data-testid="stNumberInput"] button { background:transparent; color:var(--blue); }
.stButton > button { background:var(--grad); color:#fff; border:0; border-radius:14px; font-weight:600; padding:.55rem 1.1rem; box-shadow:0 8px 16px rgba(58,61,255,.28); }
.stButton > button:hover { color:#fff; filter:brightness(1.07); }

/* ---------- SIDEBAR (soft light) ---------- */
[data-testid="stSidebar"] { background:linear-gradient(185deg,#eaeff6,#dde4ee); border-right:2px solid var(--line-strong); box-shadow:8px 0 24px rgba(163,177,198,.35); }
[data-testid="stSidebarContent"] { padding:0 1rem 1rem; }
[data-testid="stSidebarHeader"] { position:absolute; top:.4rem; right:.4rem; z-index:5; height:auto; padding:0; width:auto; background:transparent; }
[data-testid="stSidebarHeader"] button { color:var(--muted); }
[data-testid="stSidebarUserContent"] { padding-top:1rem; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.45rem; }
[data-testid="stSidebar"] hr { display:none; }
.sb-brand { display:flex; align-items:center; gap:12px; padding:4px 6px 14px; margin-bottom:8px; border-bottom:2px solid var(--line); }
.sb-logo { width:46px; height:46px; border-radius:15px; display:grid; place-items:center; flex:none; background:linear-gradient(145deg,#4a4dff,#2e8bff); border:2px solid #2a2cc9; box-shadow:0 8px 16px rgba(58,61,255,.35), inset 2px 2px 4px rgba(255,255,255,.35), inset -3px -3px 6px rgba(20,30,160,.35); }
.sb-logo svg { width:27px; height:27px; display:block; filter:drop-shadow(0 2px 2px rgba(20,30,160,.4)); }
.sb-name { color:var(--ink); font-weight:700; font-size:1rem; line-height:1.2; }
.sb-sub { color:var(--muted); font-size:.68rem; letter-spacing:.08em; }
.sb-label { color:var(--muted); font-size:.72rem; font-weight:600; letter-spacing:.05em; text-transform:uppercase; margin:14px 4px 0; padding-bottom:.5rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap:.5rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > div { width:100%; }
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stRadioOption"],
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] { width:100%; margin:0; padding:.65rem .8rem; border-radius:16px; background:#f1f4f9; box-shadow:var(--sh-sm); border:1.5px solid var(--line); transition:all .16s ease; cursor:pointer; box-sizing:border-box; }
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child,
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p { color:#56627d; font-weight:600; font-size:.78rem; line-height:1.4; margin:0; }
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) { background:var(--grad); border-color:#2a2cc9 !important; box-shadow:0 9px 18px rgba(58,61,255,.3); }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p { color:#fff; }
[data-testid="stSidebar"] label p, [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color:#56627d; font-size:.78rem; font-weight:500; }
[data-testid="stSidebar"] [data-baseweb="input"], [data-testid="stSidebar"] [data-baseweb="base-input"] { background:#e6ebf3 !important; border-radius:12px; border:0 !important; box-shadow:var(--sh-in); }
[data-testid="stSidebar"] [data-baseweb="input"] input { color:var(--ink) !important; -webkit-text-fill-color:var(--ink); background:transparent !important; }
[data-testid="stSidebar"] [data-testid="stDateInputField"] { background:#e6ebf3 !important; border:1.5px solid var(--line) !important; border-radius:12px; box-shadow:var(--sh-in); }
[data-testid="stSidebar"] [data-testid="stDateInputField"] * { color:var(--ink) !important; -webkit-text-fill-color:var(--ink); }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] { background:#e6ebf3; border:1.5px dashed var(--line-strong); border-radius:14px; box-shadow:var(--sh-in); padding:.5rem .7rem; display:flex; flex-direction:column; align-items:flex-start; gap:.3rem; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * { color:#6a7690; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small, [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span { font-size:.66rem !important; line-height:1.3; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button { font-size:.76rem; background:var(--grad); border:0; border-radius:10px; color:#fff; padding:.22rem .7rem; box-shadow:0 5px 10px rgba(58,61,255,.25); }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * { color:#fff; }
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * { color:var(--ink); }
.sb-foot { display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-top:14px; padding-top:12px; border-top:2px solid var(--line); }
.sb-chip { font-size:.7rem; font-weight:600; padding:5px 13px; border-radius:999px; background:#f1f4f9; border:1.5px solid var(--line); box-shadow:var(--sh-sm); color:var(--muted); }
.sb-chip.on { background:var(--grad); color:#fff; box-shadow:0 5px 12px rgba(58,61,255,.3); }
</style>

""",
    unsafe_allow_html=True,
)


# =========================================================================
# ฟังก์ชันวาดกราฟ
# =========================================================================
def _pct(value, base):
    return (value / base * 100) if base and base > 0 else 0.0


def radial_chart(labels, values, base=None, height=300):
    """กราฟพัดครึ่งวงกลม + ฟองเปอร์เซ็นต์ครึ่งซ้าย"""
    n = len(labels)
    base = base if base else sum(values)
    maxv = max(values) if max(values) > 0 else 1
    width = 180 / n
    colors = [RAINBOW[i % len(RAINBOW)] for i in range(n)]

    fig = go.Figure()

    fig.add_trace(
        go.Barpolar(
            r=[1.12], theta=[180], width=[180],
            marker=dict(color="rgba(200,209,222,0.55)", line=dict(width=0)),
            hoverinfo="skip", showlegend=False,
        )
    )
    fig.add_trace(
        go.Barpolar(
            r=[0.72], theta=[180], width=[180],
            marker=dict(color="rgba(255,255,255,0.7)", line=dict(width=0)),
            hoverinfo="skip", showlegend=False,
        )
    )

    for i, (lb, v) in enumerate(zip(labels, values)):
        center = 90 - width * (i + 0.5)
        r = 0.6 + 0.4 * (v / maxv)
        fig.add_trace(
            go.Barpolar(
                r=[r], theta=[center], width=[width], name=lb,
                marker=dict(color=colors[i], line=dict(color="#eef2f8", width=2)),
                hovertemplate=f"{lb}<br>{v:,} Pallets<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[r - 0.12], theta=[center], mode="text",
                text=[f"{v:,}"],
                textfont=dict(color="white", size=13, family=FONT),
                hoverinfo="skip", showlegend=False,
            )
        )

    angles = [180] if n == 1 else [100 + (160 / (n - 1)) * i for i in range(n)]
    fig.add_trace(
        go.Scatterpolar(
            r=[0.9] * n, theta=angles, mode="markers+text",
            text=[f"{_pct(v, base):.0f}%" for v in values],
            marker=dict(size=40, color="white", line=dict(color=colors, width=3)),
            textfont=dict(color=colors, size=11, family=FONT),
            hovertext=labels, hoverinfo="text", showlegend=False,
        )
    )

    fig.update_layout(
        height=height,
        margin=dict(t=10, b=46, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            hole=0.16,
            radialaxis=dict(visible=False, range=[0, 1.12]),
            angularaxis=dict(visible=False, rotation=0, direction="counterclockwise"),
        ),
        legend=dict(
            orientation="h", yanchor="top", y=-0.04, xanchor="center", x=0.5,
            font=dict(size=11), bgcolor="rgba(255,255,255,.6)", bordercolor="#9aaccb", borderwidth=1,
        ),
        annotations=[
            dict(
                x=0.5, y=0.5, xref="paper", yref="paper",
                text="<b>REPORT</b>", showarrow=False,
                font=dict(size=10, color=MUTED),
            )
        ],
    )
    return fig


def tube_chart(labels, values, base, height=320):
    """กราฟหลอดแท่งเงา + เส้นประเปอร์เซ็นต์ด้านบน"""
    n = len(labels)
    colors = [RAINBOW[i % len(RAINBOW)] for i in range(n)]
    xs = list(range(n))
    maxv = max(values) if max(values) > 0 else 1
    bg_max = maxv * 1.08
    pcts = [_pct(v, base) for v in values]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=xs, y=[bg_max] * n, width=0.68,
            marker=dict(color="rgba(255,255,255,0.95)", line=dict(color="#7f93b5", width=3)),
            hoverinfo="skip", showlegend=False,
        )
    )
    fig.add_trace(
        go.Bar(
            x=xs, y=values, width=0.52,
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,.7)", width=1)),
            text=[f"{v:,}" for v in values],
            textposition="inside", insidetextanchor="middle", textangle=-90,
            textfont=dict(color="white", size=13, family=FONT),
            customdata=[[lb, p] for lb, p in zip(labels, pcts)],
            hovertemplate="%{customdata[0]}<br>%{y:,} Pallets (%{customdata[1]:.1f}%)<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Bar(
            x=[x - 0.17 for x in xs], y=[v * 0.95 for v in values], width=0.07,
            marker=dict(color="rgba(255,255,255,0.38)", line=dict(width=0)),
            hoverinfo="skip", showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=xs, y=pcts, yaxis="y2", mode="lines+markers",
            line=dict(color="#5b6b8c", width=2, dash="dash"),
            marker=dict(size=12, symbol="square", color=colors, line=dict(color="white", width=2)),
            hovertemplate="%{y:.1f}%<extra></extra>", showlegend=False,
        )
    )
    lo, hi = min(pcts), max(pcts)
    span = max(hi - lo, 10)
    annotations = [
        dict(
            x=x, y=p, xref="x", yref="y2", text=f"<b>{p:.0f}%</b>",
            showarrow=False, yshift=28, bgcolor="white",
            bordercolor="#5f77a6", borderwidth=1.5, borderpad=3,
            font=dict(size=11, color=INK, family=FONT),
        )
        for x, p in zip(xs, pcts)
    ]

    fig.update_layout(
        height=height, barmode="overlay",
        margin=dict(t=24, b=14, l=14, r=14),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK), showlegend=False,
        annotations=annotations,
        xaxis=dict(
            tickmode="array", tickvals=xs,
            ticktext=[lb.replace(" ", "<br>", 1) if len(lb) > 12 else lb for lb in labels],
            tickfont=dict(size=11), range=[-0.6, n - 0.4],
            showgrid=False, zeroline=False,
        ),
        yaxis=dict(domain=[0, 0.62], range=[0, bg_max], showgrid=False, showticklabels=False, zeroline=False),
        yaxis2=dict(
            domain=[0.74, 0.96], range=[lo - span * 0.6, hi + span * 0.9],
            showgrid=False, showticklabels=False, zeroline=False,
        ),
    )
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
NAV = [
    "สรุปงานรับและงานค้างส่ง(ย้อนหลัง)",
    "สถานการณ์การรับ(กะเช้าปัจจุบัน)",
]
NAV_ICON = {NAV[0]: "🕘", NAV[1]: "🌅"}

st.sidebar.markdown(
    '<div class="sb-brand"><div class="sb-logo"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.8 20 7v10l-8 4.2L4 17V7z"/><path d="M4 7l8 4.2L20 7"/><path d="M12 11.2v10"/><path d="M8 4.9 16 9.1" stroke-opacity=".6"/></svg></div><div>'
    '<div class="sb-name">DCSB Warehouse</div>'
    '<div class="sb-sub">REPORT SYSTEM</div></div></div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown('<div class="sb-label">เมนูรายงาน</div>', unsafe_allow_html=True)
sheet_selection = st.sidebar.radio(
    "เลือกชีต:",
    NAV,
    format_func=lambda s: f"{NAV_ICON[s]}  {s}",
    label_visibility="collapsed",
)

st.sidebar.markdown('<div class="sb-label">วันที่รายงาน</div>', unsafe_allow_html=True)
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

st.sidebar.markdown(
    '<div class="sb-label">Import ไฟล์รายงานระบบ</div>', unsafe_allow_html=True
)
uploaded_rp01 = st.sidebar.file_uploader(
    "อัปโหลดรายงาน RP01", type=["xlsx", "xls", "csv"], key="rp01"
)
uploaded_rp03 = st.sidebar.file_uploader(
    "อัปโหลดรายงาน RP03", type=["xlsx", "xls", "csv"], key="rp03"
)
uploaded_rp42 = st.sidebar.file_uploader(
    "อัปโหลดรายงาน RP42", type=["xlsx", "xls", "csv"], key="rp42"
)
_chips = "".join(
    f'<span class="sb-chip{" on" if f is not None else ""}">{n}</span>'
    for n, f in (("RP01", uploaded_rp01), ("RP03", uploaded_rp03), ("RP42", uploaded_rp42))
)
st.sidebar.markdown(f'<div class="sb-foot">{_chips}</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><div class="hero-kicker">DCSB WAREHOUSE · REPORT SYSTEM</div>'
    '<div class="hero-title">📊 รายงานการรับสินค้าประจำวัน</div>'
    '<div class="hero-subtitle">ระบบสรุปยอดงานรับสินค้าและงานค้างรับคงเหลือ</div>'
    '<div class="hero-bar"></div></div>',
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

    with st.expander("✏️ ปรับปรุงข้อมูลรายงานประจำวัน", expanded=False):
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
                    height=320,
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
                    height=320,
                ),
                use_container_width=True,
            )

    with st.expander("✏️ ปรับปรุงข้อมูลสรุปงานรับและงานค้างส่ง(ย้อนหลัง)", expanded=False):
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
