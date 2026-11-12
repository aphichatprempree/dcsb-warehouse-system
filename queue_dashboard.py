import os, json, sqlite3, datetime as dt
import os, json, sqlite3, datetime as dt, html
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="DCSB • Queue Control", page_icon="◈", layout="wide")
theme_mode = st.sidebar.radio("ธีมหน้าจอ", ["🌙 โหมดมืด", "☀️ โหมดสว่าง"], horizontal=True, label_visibility="visible")
light_theme = theme_mode == "☀️ โหมดสว่าง"
theme_vars = ("--bg:#edf3fa;--panel:#ffffff;--panel2:#f5f8fc;--line:#cbd7e5;--text:#14263a;--muted:#52677e;--accent:#087e9b;--shadow:0 16px 36px #23405a24;" if light_theme else "--bg:#07111f;--panel:#0d1a2b;--panel2:#102137;--line:#23405c;--text:#eef7ff;--muted:#b4c7d8;--accent:#2de2e6;--shadow:0 18px 40px #0006;")

DEFAULT_QUEUES = {
    "1": {"name": "SAHAPAT", "readAs": "ขอเชิญคิวที่ 1 บริษัท สหพัฒน์"},
    "2": {"name": "DKSH", "readAs": "ขอเชิญคิวที่ 2 บริษัท ดีเคเอสเอช"},
    "3": {"name": "CROSSDOCK", "readAs": "ขอเชิญคิวที่ 3 บริษัท ครอสคอร์ส"},
    "4": {"name": "PEPSI", "readAs": "ขอเชิญคิวที่ 4 บริษัท เป๊ปซี่"},
    "5": {"name": "SINO", "readAs": "ขอเชิญคิวที่ 5 บริษัท ชิโน"},
}

st.markdown("<style>:root{" + theme_vars + "}" + """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=Orbitron:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family:'IBM Plex Sans Thai',sans-serif; }
.stApp { background:radial-gradient(ellipse at 80% -10%,#16749b44 0%,var(--bg) 55%); color:var(--text); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] h4,[data-testid="stMarkdownContainer"] p { color:var(--text); }
.block-container { max-width:1540px; padding:1.6rem 2rem 2.5rem; }
section[data-testid="stSidebar"] { background:var(--panel); border-right:1px solid var(--line); }
section[data-testid="stSidebar"] * { color:var(--text); }
.hero { padding:25px 30px; border:1px solid var(--line); border-radius:20px; background:linear-gradient(130deg,var(--panel),var(--panel2)); box-shadow:var(--shadow),inset 0 1px 0 #ffffff20; margin-bottom:22px; }
.eyebrow { color:var(--accent); font-family:Orbitron,sans-serif; letter-spacing:2px; font-size:12px; font-weight:700; }
.hero h1 { margin:8px 0 3px; font-size:30px; color:var(--text); }
.subtle { color:var(--muted); font-size:13px; }
.current { border-radius:22px; padding:26px; text-align:center; background:linear-gradient(140deg,#08789b,#1c3d83 65%,#39337c); border:1px solid #56eaf0; box-shadow:0 18px 38px #006a8744,inset 0 2px 0 #ffffff35,inset 0 -12px 35px #050d2833; }
.current .label { color:#c7fbff; letter-spacing:2.4px; font-size:12px; font-weight:700; }
.current .number { font-family:Orbitron,sans-serif; font-size:clamp(58px,7vw,84px); line-height:1.08; color:#fff; text-shadow:0 3px 0 #09274b,0 0 26px #8ffcff88; }
.current .company { font-size:23px; font-weight:700; color:#fff; }
.card { border:1px solid var(--line); border-radius:16px; background:linear-gradient(150deg,var(--panel2),var(--panel)); padding:17px 15px; min-height:148px; margin-bottom:10px; box-shadow:0 8px 20px #0002,inset 0 1px 0 #ffffff18; transition:transform .18s ease,box-shadow .18s ease; }
.card:hover { transform:translateY(-4px); box-shadow:0 16px 28px #0003,inset 0 1px 0 #ffffff22; }
.card.active { border-color:#14cbd2; box-shadow:0 0 0 1px #14cbd255,0 12px 25px #07bac233; }
.card.done { border-color:#159e7c; }
.card.off { opacity:.62; }
.card .q { font:700 11px Orbitron,sans-serif; color:var(--accent); letter-spacing:1.2px; }
.card .nm { font-size:17px; font-weight:700; color:var(--text); margin:7px 0 9px; overflow-wrap:anywhere; }
.card .st { color:var(--muted); font-size:12px; font-weight:600; }
div[data-testid="stButton"] button { border-radius:11px; font-weight:700; min-height:43px; color:var(--text)!important; background:linear-gradient(180deg,var(--panel2),var(--panel))!important; border:1px solid var(--line)!important; box-shadow:0 4px 0 color-mix(in srgb,var(--line),transparent 15%),0 8px 15px #0002!important; }
div[data-testid="stButton"] button:hover { transform:translateY(-2px); border-color:var(--accent)!important; color:var(--accent)!important; }
div[data-testid="stButton"] button[kind="primary"] { background:linear-gradient(135deg,#0795b3,#2563c9)!important; color:white!important; border-color:#56eaf0!important; box-shadow:0 5px 0 #074b78,0 12px 22px #05699b55!important; }
[data-testid="stMetric"] { background:linear-gradient(145deg,var(--panel2),var(--panel)); border:1px solid var(--line); border-radius:15px; padding:14px 17px; box-shadow:0 9px 20px #0002,inset 0 1px 0 #ffffff16; }
[data-testid="stMetricLabel"] { color:var(--muted)!important; }
[data-testid="stMetricValue"] { color:var(--text)!important; }
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input { background:var(--panel2)!important; color:var(--text)!important; border:1px solid var(--line)!important; border-radius:10px!important; }
[data-testid="stRadio"] label,[data-testid="stWidgetLabel"] p { color:var(--text)!important; font-weight:600; }
[data-testid="stAlert"] { border-radius:12px; }
hr { border-color:var(--line); }
</style>
""", unsafe_allow_html=True)

# Shared backend is Supabase (Postgres). If credentials are not configured, use local SQLite for preview.
def setting(name):
    try:
        return st.secrets.get(name, os.getenv(name, ""))
    except Exception:
        return os.getenv(name, "")

USE_SUPABASE = bool(setting("SUPABASE_URL") and setting("SUPABASE_KEY"))

class Store:
    def __init__(self):
        self.remote = USE_SUPABASE
        if self.remote:
            from supabase import create_client
            url = setting("SUPABASE_URL")
            key = setting("SUPABASE_KEY")
            self.client = create_client(url, key)
            self.client = create_client(setting("SUPABASE_URL"), setting("SUPABASE_KEY"))
        else:
            self.path = Path(__file__).with_name("queue_local.db")
            with sqlite3.connect(self.path) as con:
                con.execute("CREATE TABLE IF NOT EXISTS queue_config (id INTEGER PRIMARY KEY CHECK(id=1), current_queue INTEGER NOT NULL, active_queues TEXT NOT NULL, nicknames TEXT NOT NULL, custom_names TEXT NOT NULL, updated_by TEXT, updated_at TEXT)")
                con.execute("INSERT OR IGNORE INTO queue_config VALUES (1,1,?,?,?,?,?)", (json.dumps({str(i):True for i in range(1,6)}), json.dumps({str(i):"" for i in range(1,6)}), "{}", "System Init", dt.datetime.now(dt.timezone.utc).isoformat()))
                con.execute("CREATE TABLE IF NOT EXISTS queue_config (id INTEGER PRIMARY KEY CHECK(id=1), current_queue INTEGER NOT NULL, active_queues TEXT NOT NULL, nicknames TEXT NOT NULL, custom_names TEXT NOT NULL, queue_labels TEXT NOT NULL DEFAULT '{}', updated_by TEXT, updated_at TEXT)")
                columns = {row[1] for row in con.execute("PRAGMA table_info(queue_config)")}
                if "queue_labels" not in columns:
                    con.execute("ALTER TABLE queue_config ADD COLUMN queue_labels TEXT NOT NULL DEFAULT '{}'")
                con.execute("INSERT OR IGNORE INTO queue_config (id,current_queue,active_queues,nicknames,custom_names,queue_labels,updated_by,updated_at) VALUES (1,1,?,?,?,?,?,?)", (json.dumps({str(i):True for i in range(1,6)}), json.dumps({str(i):"" for i in range(1,6)}), "{}", json.dumps({str(i):f"QUEUE 0{i}" for i in range(1,6)}), "System Init", dt.datetime.now(dt.timezone.utc).isoformat()))

    def load(self):
        if self.remote:
            row = self.client.table("queue_config").select("*").eq("id", 1).single().execute().data
            return row
            return self.client.table("queue_config").select("*").eq("id", 1).single().execute().data
        with sqlite3.connect(self.path) as con:
            row = con.execute("SELECT current_queue,active_queues,nicknames,custom_names,updated_by,updated_at FROM queue_config WHERE id=1").fetchone()
        return {"current_queue":row[0], "active_queues":json.loads(row[1]), "nicknames":json.loads(row[2]), "custom_names":json.loads(row[3]), "updated_by":row[4], "updated_at":row[5]}
            row = con.execute("SELECT current_queue,active_queues,nicknames,custom_names,queue_labels,updated_by,updated_at FROM queue_config WHERE id=1").fetchone()
        return {"current_queue":row[0], "active_queues":json.loads(row[1]), "nicknames":json.loads(row[2]), "custom_names":json.loads(row[3]), "queue_labels":json.loads(row[4]), "updated_by":row[5], "updated_at":row[6]}

    def save(self, data, editor):
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        if self.remote:
            self.client.table("queue_config").update({"current_queue":data["current_queue"], "active_queues":data["active_queues"], "nicknames":data["nicknames"], "custom_names":data["custom_names"], "updated_by":editor, "updated_at":now}).eq("id",1).execute()
            self.client.table("queue_config").update({"current_queue":data["current_queue"], "active_queues":data["active_queues"], "nicknames":data["nicknames"], "custom_names":data["custom_names"], "queue_labels":data["queue_labels"], "updated_by":editor, "updated_at":now}).eq("id",1).execute()
        else:
            with sqlite3.connect(self.path) as con:
                con.execute("UPDATE queue_config SET current_queue=?,active_queues=?,nicknames=?,custom_names=?,updated_by=?,updated_at=? WHERE id=1", (data["current_queue"],json.dumps(data["active_queues"]),json.dumps(data["nicknames"]),json.dumps(data["custom_names"]),editor,now))

                con.execute("UPDATE queue_config SET current_queue=?,active_queues=?,nicknames=?,custom_names=?,queue_labels=?,updated_by=?,updated_at=? WHERE id=1", (data["current_queue"],json.dumps(data["active_queues"]),json.dumps(data["nicknames"]),json.dumps(data["custom_names"]),json.dumps(data["queue_labels"]),editor,now))
@st.cache_resource
def store(): return Store()

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key="queue_refresh")
except ImportError:
    pass

db = store()
data = db.load()

with st.sidebar:
    st.markdown("### ◈ ศูนย์ควบคุม")
    editor = st.text_input("ชื่อผู้ปฏิบัติงาน", value="เจ้าหน้าที่ 1")
    st.caption("ผู้ชมทุกคนเห็นสถานะล่าสุดที่บันทึกไว้")
    st.markdown("---")
    st.markdown("#### อายุสินค้า")
    mode = st.radio("รูปแบบการตรวจสอบ", ["เกณฑ์ Min / Max", "Product Life"], horizontal=False)
    target = st.date_input("วันหมดอายุสินค้า", value=dt.date.today())
    c1,c2=st.columns(2)
    min_days=c1.number_input("MIN วัน", min_value=0, value=730, step=1)
    max_days=c2.number_input("MAX วัน", min_value=0, value=1095, step=1)
    if st.button("⌕ ตรวจสอบอายุสินค้า", use_container_width=True):
        if min_days > max_days:
            st.error("ค่า MIN ต้องไม่มากกว่า MAX")
        else:
            low=dt.date.today()+dt.timedelta(days=int(min_days)); high=dt.date.today()+dt.timedelta(days=int(max_days))
            st.info(f"ช่วงรับได้: {low:%d/%m/%Y} – {high:%d/%m/%Y}")
            if target < low: st.error(f"REJECT · ต่ำกว่า MIN {(low-target).days:,} วัน")
            elif target > high: st.warning(f"CHECK · เกิน MAX {(target-high).days:,} วัน")
            else: st.success("ACCEPT · อายุสินค้าผ่านเกณฑ์")
    st.markdown("---")
    st.caption("🟢 รีเฟรชอัตโนมัติทุก 3 วินาที")

st.markdown('<div class="hero"><div class="eyebrow">DCSB · LIVE OPERATIONS</div><h1>ระบบจัดการคิว</h1><div class="subtle">Queue Control & Product Expiry Dashboard</div></div>', unsafe_allow_html=True)

active=data["active_queues"] or {}; names=data["custom_names"] or {}; nicknames=data["nicknames"] or {}
active=data["active_queues"] or {}; names=data["custom_names"] or {}; nicknames=data["nicknames"] or {}; labels=data.get("queue_labels", {}) or {}
curr=int(data["current_queue"])
cur_name=names.get(str(curr),DEFAULT_QUEUES[str(curr)]["name"])
cur_nick=nicknames.get(str(curr),"")

left,right=st.columns([1.05,1.95], gap="large")
with left:
    st.markdown(f'<div class="current"><div class="label">NOW SERVING</div><div class="number">#{curr}</div><div class="company">{cur_name}{(" · "+cur_nick) if cur_nick else ""}</div><div class="subtle">กำลังเรียกคิวปัจจุบัน</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="current"><div class="label">NOW SERVING</div><div class="number">#{curr}</div><div class="company">{html.escape(cur_name)}{(" · "+html.escape(cur_nick)) if cur_nick else ""}</div><div class="subtle">กำลังเรียกคิวปัจจุบัน</div></div>', unsafe_allow_html=True)
    st.caption(f"อัปเดตโดย {data.get('updated_by') or '—'} · {str(data.get('updated_at') or '')[:19].replace('T',' ')} UTC")
    a,b=st.columns(2)
    if a.button("− ลดคิว", use_container_width=True):
        candidates=[i for i in range(1,6) if active.get(str(i),True)]
        if candidates:
            data["current_queue"]=max((x for x in candidates if x<curr),default=candidates[-1]); db.save(data,(editor.strip() or "เจ้าหน้าที่")+" (ลดคิว)"); st.rerun()
    if b.button("↺ รีเซ็ตคิว", use_container_width=True):
        candidates=[i for i in range(1,6) if active.get(str(i),True)]
        if candidates: data["current_queue"]=candidates[0]; db.save(data,(editor.strip() or "เจ้าหน้าที่")+" (รีเซ็ต)"); st.rerun()
    if st.button("➜ ผ่าน / เรียกคิวถัดไป", type="primary", use_container_width=True):
        candidates=[i for i in range(1,6) if active.get(str(i),True)]
        if candidates:
            data["current_queue"]=next((i for i in candidates if i>curr),candidates[0]); db.save(data,(editor.strip() or "เจ้าหน้าที่")+" (เปลี่ยนคิว)"); st.rerun()
    st.markdown("#### จัดการรายการคิว")
    with st.expander("แก้ชื่อคิว / ชื่อเรียก", expanded=False):
    with st.expander("แก้ข้อมูลคิวทั้งหมด (ป้ายคิว / บริษัท / ชื่อเล่น)", expanded=False):
        for q in range(1,6):
            key=str(q)
            st.markdown(f"**คิว #{q}**")
            n1,n2=st.columns(2)
            names[key]=n1.text_input("ชื่อบริษัท", value=names.get(key,DEFAULT_QUEUES[key]["name"]), key=f"name{q}")
            nicknames[key]=n2.text_input("ชื่อเล่น", value=nicknames.get(key,""), key=f"nick{q}")
            st.markdown(f"**ตั้งค่าคิว {q:02d}**")
            n1,n2,n3=st.columns([1,1.2,1])
            labels[key]=n1.text_input("ป้ายบนการ์ด", value=labels.get(key,f"QUEUE 0{q}"), key=f"label{q}")
            names[key]=n2.text_input("ชื่อบริษัท", value=names.get(key,DEFAULT_QUEUES[key]["name"]), key=f"name{q}")
            nicknames[key]=n3.text_input("ชื่อเล่น", value=nicknames.get(key,""), key=f"nick{q}")
            st.divider()
        if st.button("บันทึกชื่อคิว", use_container_width=True):
            data["custom_names"]=names; data["nicknames"]=nicknames; db.save(data,(editor.strip() or "เจ้าหน้าที่")+" (แก้ชื่อ)"); st.rerun()
        if st.button("บันทึกข้อมูลคิวทั้งหมด", use_container_width=True):
            data["queue_labels"]=labels; data["custom_names"]=names; data["nicknames"]=nicknames
            db.save(data,(editor.strip() or "เจ้าหน้าที่")+" (แก้ข้อมูลคิว)"); st.success("บันทึกข้อมูลคิวแล้ว"); st.rerun()

with right:
    st.markdown("#### ภาพรวมคิว")
    cols=st.columns(5, gap="small")
    for q in range(1,6):
        key=str(q); is_on=active.get(key,True)
        status="ปิดใช้งาน" if not is_on else "กำลังเรียก" if q==curr else "ผ่านแล้ว" if q<curr else "รอคิว"
        cls="off" if not is_on else "active" if q==curr else "done" if q<curr else ""
        with cols[q-1]:
            st.markdown(f'<div class="card {cls}"><div class="q">QUEUE 0{q}</div><div class="nm">{names.get(key,DEFAULT_QUEUES[key]["name"])}</div><div class="st">● {status}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card {cls}"><div class="q">{html.escape(labels.get(key,f"QUEUE 0{q}"))}</div><div class="nm">{html.escape(names.get(key,DEFAULT_QUEUES[key]["name"]))}</div><div class="st">● {status}</div></div>', unsafe_allow_html=True)
            if st.button("ปิดคิว" if is_on else "เปิดคิว", key=f"toggle{q}", use_container_width=True):
                active[key]=not is_on
                if not active[key] and curr==q:
                    candidates=[i for i in range(1,6) if active.get(str(i),True)]
                    if candidates: data["current_queue"]=candidates[0]
                data["active_queues"]=active; db.save(data,(editor.strip() or "เจ้าหน้าที่")+f" (สลับคิว #{q})"); st.rerun()
    enabled=sum(1 for q in range(1,6) if active.get(str(q),True))
    m1,m2,m3=st.columns(3)
    m1.metric("คิวที่เปิดใช้งาน",f"{enabled} / 5")
    m2.metric("คิวปัจจุบัน",f"#{curr}")
    m3.metric("ระบบ", "LIVE" if USE_SUPABASE else "LOCAL PREVIEW")
    if not USE_SUPABASE:
        st.warning("ขณะนี้กำลังใช้ฐานข้อมูลในเครื่องสำหรับทดลอง ผู้ใช้ที่เปิดคนละเครื่องจะยังไม่เห็นข้อมูลร่วมกัน จนกว่าจะตั้งค่า Supabase ตาม README")






