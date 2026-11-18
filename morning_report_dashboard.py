import json
import hashlib
import math
import re
from pathlib import Path
from datetime import date, datetime, time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def _norm_key(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    return value[:-2] if value.endswith(".0") else value


def _read_report(upload, required_headers):
    """Find the report header row from its known fields, then read its detail rows."""
    if upload is None:
        return None
    raw = pd.read_excel(upload, header=None, dtype=object)
    required = [str(x).strip().casefold() for x in required_headers]
    header_idx = None
    for i, row in raw.head(30).iterrows():
        labels = {str(v).strip().casefold() for v in row if pd.notna(v)}
        if all(any(req in label for label in labels) for req in required):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("หารายการหัวคอลัมน์ที่ต้องใช้ไม่พบ กรุณาตรวจว่าเลือกไฟล์รายงานถูกประเภท")
    upload.seek(0)
    frame = pd.read_excel(upload, header=header_idx, dtype=object)
    frame.columns = [str(c).strip() for c in frame.columns]
    frame = frame.loc[:, ~frame.columns.str.startswith("Unnamed:")]
    return frame.dropna(how="all").reset_index(drop=True)


def _column(frame, name):
    matches = [c for c in frame.columns if c.strip().casefold() == name.casefold()]
    if not matches:
        raise ValueError(f"ไม่พบคอลัมน์ {name}")
    return matches[0]


def _sum_numeric(frame, name, mask=None):
    col = _column(frame, name)
    values = pd.to_numeric(frame[col], errors="coerce").fillna(0)
    total = values[mask].sum() if mask is not None else values.sum()
    total = float(total)
    return int(total) if total.is_integer() else total


def _format_quantity(value):
    number = float(value)
    return f"{int(number):,}" if number.is_integer() else f"{number:,.2f}".rstrip("0").rstrip(".")


def _minutes_since_midnight(value):
    if pd.isna(value):
        return None
    if isinstance(value, (datetime, pd.Timestamp, time)):
        return value.hour * 60 + value.minute
    if isinstance(value, (int, float)) and 0 <= float(value) < 1:
        return int(round(float(value) * 24 * 60))
    match = re.search(r"(\d{1,2}):(\d{2})", str(value).strip())
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    return hour * 60 + minute if hour <= 24 and minute < 60 else None


def _window_mask(frame, shift):
    col = _column(frame, "Window Time")
    minutes = frame[col].map(_minutes_since_midnight)
    if shift == "night":
        return minutes.notna() & (minutes < 5 * 60)
    return minutes.notna() & (minutes >= 5 * 60) & (minutes < 24 * 60)


def _load_morning_metrics(files):
    result = {}
    try:
        rp01_file = files["rp01_1610"] if files["rp01_1610"] is not None else files["rp01_2200"]
        if rp01_file is not None:
            rp01 = _read_report(rp01_file, ["Pallets Qty", "P/O", "Window Time"])
            result["report_date"] = _report_date_from_frame(rp01)
            result["inv_all"] = _sum_numeric(rp01, "Pallets Qty")
            result["night_received"] = _sum_numeric(rp01, "Pallets Qty", _window_mask(rp01, "night"))
            result["morning_received"] = _sum_numeric(rp01, "Pallets Qty", _window_mask(rp01, "morning"))
        if files["rp42"] is not None:
            rp42 = _read_report(files["rp42"], ["Pallets Qty", "ASN_STATUS_DESC", "Window Time", "CHECK_IN_USER"])
            status = rp42[_column(rp42, "ASN_STATUS_DESC")].astype(str).str.strip().str.casefold()
            verified = status.isin({"verified", "receiving verified"})
            started = status.eq("receiving started")
            in_transit = status.eq("intransit")
            user = rp42[_column(rp42, "CHECK_IN_USER")]
            checked_in = user.notna() & user.astype(str).str.strip().ne("")
            result["complete_night"] = _sum_numeric(rp42, "Pallets Qty", verified & _window_mask(rp42, "night"))
            result["complete_morning"] = _sum_numeric(rp42, "Pallets Qty", verified & _window_mask(rp42, "morning"))
            result["recv_start"] = _sum_numeric(rp42, "Pallets Qty", started)
            result["in_transit"] = _sum_numeric(rp42, "Pallets Qty", in_transit & checked_in)
            result["sup_night_missing"] = _sum_numeric(
                rp42, "Pallets Qty", in_transit & ~checked_in & _window_mask(rp42, "night")
            )
            result["sup_morning_missing"] = _sum_numeric(
                rp42, "Pallets Qty", in_transit & ~checked_in & _window_mask(rp42, "morning")
            )
        if files["rp03"] is not None and result.get("report_date"):
            rp03 = _read_report(files["rp03"], ["Total Case Qty (iLPNs)", "Purchase Order", "Schedule Date"])
            schedule = pd.to_datetime(rp03[_column(rp03, "Schedule Date")], dayfirst=True, errors="coerce").dt.date
            result["extra_work"] = _sum_numeric(rp03, "Total Case Qty (iLPNs)", schedule.notna() & schedule.ne(result["report_date"]))
        if all(k in result for k in ("recv_start", "in_transit", "sup_night_missing", "sup_morning_missing")):
            result["total_remaining"] = (
                result["recv_start"] + result["in_transit"]
                + result["sup_night_missing"] + result["sup_morning_missing"]
            )
        return result, None
    except Exception as exc:
        return result, str(exc)


def _report_date_from_frame(frame):
    """Use the most common delivery date in RP01 as the report date."""
    try:
        col = _column(frame, "Delivery Date")
    except ValueError:
        return None
    dates = pd.to_datetime(frame[col], dayfirst=True, errors="coerce").dropna()
    if dates.empty:
        return None
    return dates.dt.date.value_counts().index[0]


def _date_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    patterns = (
        r"\d{4}-\d{1,2}-\d{1,2}",
        r"\d{1,2}/\d{1,2}/\d{2,4}",
        r"\d{1,2}/[A-Za-z]{3}/\d{4}",
        r"[A-Za-z]{3}\s+\d{1,2},\s*\d{4}",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            parsed = pd.to_datetime(match.group(0), dayfirst=True, errors="coerce")
            if not pd.isna(parsed):
                return parsed.date()
    return None


def _report_metadata_date(upload):
    """Read the export/report date from the preamble above a report's table."""
    if upload is None:
        return None
    upload.seek(0)
    raw = pd.read_excel(upload, header=None, dtype=object, nrows=12)
    upload.seek(0)
    for _, row in raw.iterrows():
        values = list(row)
        for index, value in enumerate(values):
            if "report date" not in str(value).strip().casefold():
                continue
            parsed = _date_value(value)
            if parsed:
                return parsed
            for next_value in values[index + 1:]:
                parsed = _date_value(next_value)
                if parsed:
                    return parsed
    return None


def _report_date_warnings(files, rp01_date):
    if rp01_date is None:
        if files.get("rp01_1610") is not None or files.get("rp01_2200") is not None:
            return ["อ่านวันที่จาก Delivery Date ใน RP01 ไม่ได้ จึงยังตรวจสอบวันที่ของ RP03 และ RP42 ไม่ได้"]
        return []
    warnings = []
    for key, label in (("rp03", "RP03"), ("rp42", "RP42")):
        upload = files.get(key)
        if upload is None:
            continue
        try:
            source_date = _report_metadata_date(upload)
        except Exception:
            source_date = None
        if source_date is None:
            warnings.append(f"ไม่พบ Report Date ใน {label} ({upload.name}) จึงตรวจสอบวันเทียบกับ RP01 ไม่ได้")
        elif source_date != rp01_date:
            warnings.append(
                f"วันที่รายงานไม่ตรงกัน: RP01 {rp01_date:%d/%m/%Y} แต่ {label} {source_date:%d/%m/%Y} ({upload.name})"
            )
    return warnings


def _extra_complete(rp01_22, rp03):
    """Sum only RP03 case quantities absent from RP01 Pallets Qty (VLOOKUP #N/A)."""
    rp01_col = _column(rp01_22, "Pallets Qty")
    rp03_col = _column(rp03, "Total Case Qty (iLPNs)")
    rp01_qty = pd.to_numeric(rp01_22[rp01_col], errors="coerce").dropna()
    rp03_qty = pd.to_numeric(rp03[rp03_col], errors="coerce")
    unmatched = rp03_qty.notna() & ~rp03_qty.isin(set(rp01_qty.tolist()))
    missing_count = int(unmatched.sum())
    total = float(rp03_qty[unmatched].sum())
    total = int(total) if total.is_integer() else total
    return total, rp01_col, rp03_col, missing_count


def _po_values(text_value):
    values = re.split(r"[\s,;]+", str(text_value or "").strip())
    return list(dict.fromkeys(key for value in values if (key := _norm_key(value))))


def _item_column(frame, preferred):
    preferred_match = next((c for c in frame.columns if c.strip().casefold() == preferred.casefold()), None)
    if preferred_match is not None:
        return preferred_match
    aliases = {
        "item code", "item name", "item", "item number", "item no", "item no.",
        "sku", "product code",
    }
    return next((c for c in frame.columns if c.strip().casefold() in aliases), None)


def _lookup_delayed_pallets(rp01_file, po_text):
    frame = _read_report(rp01_file, ["P/O", "Pallets Qty"])
    requested = set(_po_values(po_text))
    po_col = _column(frame, "P/O")
    qty_col = _column(frame, "Pallets Qty")
    matched = frame[po_col].map(_norm_key).isin(requested)
    found = set(frame.loc[matched, po_col].map(_norm_key))
    missing = sorted(requested - found)
    total = pd.to_numeric(frame.loc[matched, qty_col], errors="coerce").fillna(0).sum()
    total = float(total)
    return (int(total) if total.is_integer() else total), missing


def _lookup_reject_pallets(rp01_file, rp03_file, item_text):
    requested = {value.casefold() for value in _po_values(item_text)}
    if not requested:
        return 0, [], []
    rp01 = _read_report(rp01_file, ["Pack Qty", "TI", "HI"])
    rp03 = _read_report(rp03_file, ["Total Pack Qty"])
    item1, item3 = _item_column(rp01, "Item Name"), _item_column(rp03, "Item Code")
    if item1 is None:
        raise ValueError("ไม่พบคอลัมน์ Item Name ใน RP01")
    if item3 is None:
        raise ValueError("ไม่พบคอลัมน์ Item Code ใน RP03")
    rp01 = rp01.assign(
        _item=rp01[item1].map(lambda value: _norm_key(value).casefold()),
        _expected=pd.to_numeric(rp01[_column(rp01, "Pack Qty")], errors="coerce").fillna(0),
        _ti=pd.to_numeric(rp01[_column(rp01, "TI")], errors="coerce"),
        _hi=pd.to_numeric(rp01[_column(rp01, "HI")], errors="coerce"),
    )
    rp03 = rp03.assign(
        _item=rp03[item3].map(lambda value: _norm_key(value).casefold()),
        _received=pd.to_numeric(rp03[_column(rp03, "Total Pack Qty")], errors="coerce").fillna(0),
    )
    rp01 = rp01[rp01["_item"].isin(requested) & rp01["_item"].ne("")]
    rp03 = rp03[rp03["_item"].isin(requested) & rp03["_item"].ne("")]
    expected = rp01.groupby("_item", as_index=False).agg(
        _expected=("_expected", "sum"), _ti=("_ti", "first"), _hi=("_hi", "first")
    )
    received = rp03.groupby("_item", as_index=False)["_received"].sum()
    ti_hi_counts = (
        rp01[["_item", "_ti", "_hi"]]
        .dropna(subset=["_ti", "_hi"])
        .drop_duplicates()
        .groupby("_item")
        .size()
    )
    ambiguous_items = set(ti_hi_counts[ti_hi_counts.gt(1)].index)
    expected = expected[~expected["_item"].isin(ambiguous_items)]
    matched_items = set(expected["_item"])
    missing = sorted(requested - matched_items - ambiguous_items)
    joined = expected.merge(received, on="_item", how="left")
    joined["_received"] = joined["_received"].fillna(0)
    valid = (
        joined["_ti"].notna() & joined["_ti"].gt(0)
        & joined["_hi"].notna() & joined["_hi"].gt(0)
    )
    invalid_items = joined.loc[~valid, "_item"].drop_duplicates().tolist()
    joined = joined.loc[valid].copy()
    joined["_reject_pack"] = (joined["_expected"] - joined["_received"]).clip(lower=0)
    total = (joined["_reject_pack"] / joined["_ti"] / joined["_hi"]).sum()
    total = math.ceil(float(total))
    invalid_items.extend(f"Item {item} มี TI/HI หลายชุด" for item in sorted(ambiguous_items))
    return total, missing, invalid_items


def _load_imported_metrics(files):
    result = {}
    try:
        if files["rp01_1610"] is not None:
            d = _read_report(files["rp01_1610"], ["Pallets Qty", "P/O"])
            result["hist_total_recv"] = _sum_numeric(d, "Pallets Qty")
            result["report_date"] = _report_date_from_frame(d)
        if files["rp01_2200"] is not None:
            d22 = _read_report(files["rp01_2200"], ["Pallets Qty", "P/O"])
            result["hist_not_billed"] = _sum_numeric(d22, "Pallets Qty")
            if not result.get("report_date"):
                result["report_date"] = _report_date_from_frame(d22)
        else:
            d22 = None
        if files["rp42"] is not None:
            d42 = _read_report(files["rp42"], ["Pallets Qty", "ASN_STATUS_DESC"])
            status = _column(d42, "ASN_STATUS_DESC")
            result["hist_complete"] = _sum_numeric(
                d42, "Pallets Qty", d42[status].astype(str).str.strip().str.casefold().eq("receiving verified")
            )
        if files["rp03"] is not None and d22 is not None:
            d03 = _read_report(files["rp03"], ["Total Case Qty (iLPNs)", "Purchase Order"])
            extra, left, right, overlap = _extra_complete(d22, d03)
            result["hist_extra"] = extra
            result["extra_join"] = (
                f"VLOOKUP {left} (RP01 22.00) ↔ {right} (RP03): "
                f"พบค่า #N/A {overlap:,} แถว นับเฉพาะแถวที่ไม่ตรงกัน"
            )
        return result, None
    except Exception as exc:
        return result, str(exc)

REPORT_DEFAULTS = {
    "hist_inv": 6126,
    "hist_total_recv": 5904,
    "hist_complete": 5722,
    "hist_extra": 138,
    "hist_delayed": 0,
    "hist_not_po": 73,
    "hist_not_billed": 250,
}
HISTORY_PO_FIELDS = ("hist_delayed_po_input", "hist_reject_item_input", "hist_po_rp01_source")
MORNING_DEFAULTS = {
    "inv_all": 6058,
    "night_received": 4240,
    "morning_received": 1818,
    "complete_night": 4475,
    "complete_morning": 0,
    "extra_work": 0,
    "total_remaining": 2425,
    "recv_start": 473,
    "in_transit": 268,
    "sup_night_missing": 239,
    "sup_morning_missing": 0,
}


REPORT_STORE_PATH = Path(__file__).with_name("daily_reports.json")


def _load_report_store():
    try:
        with REPORT_STORE_PATH.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        return data if isinstance(data.get("records"), dict) else {"records": {}}
    except (OSError, ValueError, TypeError):
        return {"records": {}}


def _get_report_record(report_date, page="history"):
    records = REPORT_STORE.get("records", {})
    return records.get(f"{page}:{report_date}") or (records.get(report_date) if page == "history" else None)


def _save_report_record(report_date, values, page="history"):
    store = _load_report_store()
    fields = MORNING_DEFAULTS if page == "morning" else REPORT_DEFAULTS
    store.setdefault("records", {})[f"{page}:{report_date}"] = {
        **{field: values.get(field, fields[field]) for field in fields},
        **({field: values.get(field, "") for field in HISTORY_PO_FIELDS} if page == "history" else {}),
        "updated_at": pd.Timestamp.now().isoformat(timespec="seconds"),
    }
    store["morning_latest_date" if page == "morning" else "latest_date"] = report_date
    temp_path = REPORT_STORE_PATH.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8") as stream:
        json.dump(store, stream, ensure_ascii=False, indent=2)
    temp_path.replace(REPORT_STORE_PATH)


def _autosave_current_report():
    report_date = st.session_state.get("h_date_input")
    if not report_date:
        return
    values = {
        field: st.session_state.get(field, REPORT_DEFAULTS[field])
        for field in REPORT_DEFAULTS
    }
    values.update({field: st.session_state.get(field, "") for field in HISTORY_PO_FIELDS})
    try:
        _save_report_record(report_date.strftime("%Y-%m-%d"), values)
        st.session_state["_autosaved_at"] = pd.Timestamp.now().strftime("%H:%M:%S")
    except OSError as exc:
        st.session_state["_autosave_error"] = str(exc)


def _autosave_morning_report():
    report_date = st.session_state.get("m_date_input")
    if not report_date:
        return
    values = {field: st.session_state.get(field, default) for field, default in MORNING_DEFAULTS.items()}
    values["total_remaining"] = sum(values[field] for field in ("recv_start", "in_transit", "sup_night_missing", "sup_morning_missing"))
    try:
        _save_report_record(report_date.strftime("%Y-%m-%d"), values, page="morning")
        st.session_state["_morning_autosaved_at"] = pd.Timestamp.now().strftime("%H:%M:%S")
    except OSError as exc:
        st.session_state["_morning_autosave_error"] = str(exc)


# ตั้งค่าหน้าเว็บแดชบอร์ดหลัก
st.set_page_config(
    page_title="DCSB Distribution Center Morning Report",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPORT_STORE = _load_report_store()

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
.report-wrap { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border-radius:20px; overflow:hidden; box-shadow:var(--sh); border:2px solid var(--line-strong); padding:5px 7px 8px; }
.report-head { color:var(--ink); text-align:left; padding:5px 10px 6px; margin-bottom:2px; border-bottom:2px solid var(--line); font-size:.98rem; font-weight:700; }
.report-date { font-size:.82rem; font-weight:500; color:var(--muted); margin-left:5px; }
.report-grid { display:grid; gap:7px; padding:2px 3px; }
.report-group { grid-column:1 / -1; color:var(--ink); font-size:.9rem; line-height:1.2; font-weight:700; padding:3px 3px 2px; border-bottom:1px solid var(--line); letter-spacing:.01em; }
.report-cell { border-radius:12px; padding:6px 6px; text-align:center; background:#f1f4f9; box-shadow:var(--sh-sm); border:1.5px solid var(--line); min-height:68px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:space-between; gap:4px; }
.report-label { color:#4d5a78; font-size:.78rem; line-height:1.25; font-weight:500; }
.report-value { color:var(--ink); font-size:1.22rem; font-weight:700; line-height:1.2; overflow-wrap:anywhere; font-variant-numeric:tabular-nums; }
.report-wrap.compact { padding:4px 6px 6px; border-radius:16px; }
.report-wrap.compact .report-head { padding:4px 8px 5px; margin-bottom:1px; }
.report-wrap.compact .report-grid { gap:5px; padding:2px; }
.report-wrap.compact .report-group { font-size:.82rem; padding:2px 2px 1px; }
.report-wrap.compact .report-cell { min-height:58px; padding:4px 5px; border-radius:10px; gap:3px; }
.report-wrap.compact .report-label { font-size:.72rem; line-height:1.16; }
.report-wrap.compact .report-value { font-size:1.1rem; }
.report-value.alert { color:var(--rose); }

/* ---------- CHART CARDS ---------- */
[class*="st-key-card"] { background:linear-gradient(145deg,#eef2f8,#e1e7f0); border-radius:26px; box-shadow:var(--sh); padding:.8rem .9rem .6rem; border:2px solid var(--line-strong); }
.chart-title { color:var(--ink); font-size:.92rem; font-weight:700; margin:0 0 4px; text-align:center; }
.chart-sub { color:var(--muted); font-size:.7rem; text-align:center; margin-bottom:6px; padding-bottom:6px; border-bottom:1.5px dashed var(--line); }
@media (max-width:1200px) { .report-grid:not(.compact-grid) { grid-template-columns:repeat(4,minmax(0,1fr)) !important; } .report-grid.compact-grid { grid-template-columns:repeat(6,minmax(0,1fr)) !important; } .focus-grid { grid-template-columns:1fr; } }
@media (max-width:900px) { .report-grid.compact-grid { grid-template-columns:repeat(3,minmax(0,1fr)) !important; } }
@media (max-width:700px) { .hero-title{font-size:1.25rem} .report-grid:not(.compact-grid){grid-template-columns:repeat(2,minmax(0,1fr)) !important} .report-grid.compact-grid{grid-template-columns:repeat(2,minmax(0,1fr)) !important} .focus-value{font-size:1.8rem} }

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


def report_table(title, date_str, time_str, items, cols, compact=False, accent_colors=None):
    rendered_cells = []
    metric_index = 0
    colors = accent_colors or RAINBOW
    for item in items:
        if len(item) == 2 and item[0] == "group":
            rendered_cells.append(f'<div class="report-group">{item[1]}</div>')
            continue
        label, value, alert = item
        rendered_cells.append(
            f'<div class="report-cell" style="border-top:4px solid {colors[metric_index % len(colors)]};">'
            f'<div class="report-label">{label.replace(chr(10), "<br>")}</div>'
            f'<div class="report-value{" alert" if alert else ""}">{value}</div></div>'
        )
        metric_index += 1
    cells = "".join(rendered_cells)
    return (
        f'<div class="report-wrap{" compact" if compact else ""}"><div class="report-head">{title} {date_str}'
        f' <span class="report-date">{time_str}</span></div>'
        f'<div class="report-grid{" compact-grid" if compact else ""}" style="grid-template-columns: repeat({cols}, minmax(0, 1fr));">'
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
NAV_ICON = {NAV[0]: "🌙", NAV[1]: "☀️"}

st.sidebar.markdown(
    '<div class="sb-brand"><div class="sb-logo"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.8 20 7v10l-8 4.2L4 17V7z"/><path d="M4 7l8 4.2L20 7"/><path d="M12 11.2v10"/><path d="M8 4.9 16 9.1" stroke-opacity=".6"/></svg></div><div>'
    '<div class="sb-name">DCSB Distribution Center</div>'
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
if sheet_selection == NAV[1]:
    RAINBOW = ["#83c89d", "#8eb7df", "#aa94d0", "#f1bd69", "#e789a9", "#efd479", "#e99c82", "#83c7c1"]
    st.markdown(
        """
<style>
body:has(.morning-theme) {
    --ink:#30363a; --muted:#7e878b; --blue:#7197bd; --blue2:#94b6d3;
    --rose:#d77e88; --grad:linear-gradient(120deg,#c9e8d2,#f5e2b5);
    --line:#e8edef; --line-strong:#dce4e6;
    --sh:0 7px 20px rgba(61,79,73,.07);
    --sh-sm:0 3px 10px rgba(61,79,73,.06);
    --sh-in:inset 0 1px 3px rgba(61,79,73,.05);
}
body:has(.morning-theme) [data-testid="stAppViewContainer"] { background:#ffffff; }
body:has(.morning-theme) .hero,
body:has(.morning-theme) .focus-card,
body:has(.morning-theme) .report-wrap,
body:has(.morning-theme) [class*="st-key-card"],
body:has(.morning-theme) [data-testid="stExpander"] { background:#ffffff; }
body:has(.morning-theme) .report-cell { background:#ffffff; }
body:has(.morning-theme) [data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #edf0f1; box-shadow:4px 0 18px rgba(48,59,55,.035); }
body:has(.morning-theme) [data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked),
body:has(.morning-theme) [data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked),
body:has(.morning-theme) [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) { background:#eef6f0; border-color:#dcebe0 !important; box-shadow:none; }
body:has(.morning-theme) [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p { color:#52715d; }
body:has(.morning-theme) .sb-brand { background:transparent; border-bottom:1px solid #e8edef; border-radius:0; padding:5px 6px 14px; margin-bottom:8px; }
body:has(.morning-theme) .sb-name { color:#30363a; }
body:has(.morning-theme) .sb-sub { color:#8a9296; }
body:has(.morning-theme) .sb-logo { background:#7eae8b; border-color:#719d7b; box-shadow:none; }
body:has(.morning-theme) .sb-label { color:#84908b; }
body:has(.morning-theme) .hero-bar { box-shadow:0 3px 8px rgba(119,168,139,.16); }
body:has(.morning-theme) .section-title::before { box-shadow:0 2px 7px rgba(119,168,139,.14); }
body:has(.morning-theme) .report-wrap { border-width:1px; }
body:has(.morning-theme) .report-cell { box-shadow:0 2px 8px rgba(54,40,83,.06); }
body:has(.morning-theme) [data-testid="stNumberInput"] [data-baseweb="input"],
body:has(.morning-theme) [data-testid="stNumberInput"] [data-baseweb="base-input"] { background:#fff !important; }
.hero { padding:8px 18px 7px; margin-bottom:4px; border-radius:20px; }
.hero-kicker { font-size:.58rem; }
.hero-title { font-size:1.25rem; margin:0; }
.hero-subtitle { font-size:.72rem; line-height:1.2; }
.hero-bar { height:3px; margin-top:5px; }
.section-title { font-size:.9rem; margin:7px 0 2px; padding-bottom:3px; }
.section-title::before { height:15px; }
.focus-grid { gap:10px; margin:3px 0; }
.focus-card { padding:8px 16px 7px 22px; border-radius:18px; }
.focus-card::before { top:9px; bottom:9px; width:4px; }
.focus-label { font-size:.76rem; }
.focus-value { font-size:1.7rem; margin:2px 0; }
.focus-unit { font-size:.68rem; }
.report-wrap.compact { padding:3px 5px 5px; }
.report-wrap.compact .report-head { padding:3px 7px 4px; font-size:.9rem; }
.report-wrap.compact .report-grid { gap:4px; }
.report-wrap.compact .report-group { font-size:.76rem; padding:1px 2px; }
.report-wrap.compact .report-cell { min-height:50px; padding:3px 4px; gap:2px; }
.report-wrap.compact .report-label { font-size:.72rem; line-height:1.14; }
.report-wrap.compact .report-value { font-size:1.02rem; }
[class*="st-key-card"] { padding:.4rem .5rem .25rem; border-radius:18px; }
.chart-title { font-size:.82rem; margin-bottom:2px; }
.chart-sub { font-size:.64rem; margin-bottom:3px; padding-bottom:3px; }
</style>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="morning-theme" aria-hidden="true"></div>', unsafe_allow_html=True)

# Keep both page-specific upload sections mounted so Streamlit preserves each
# page's selected files while the user switches between reports.
_page_id = "morning" if sheet_selection == NAV[1] else "history"


def _render_upload_section(page_id, title, expanded):
    with st.sidebar.expander(title, expanded=expanded):
        uploads = {
            "rp01_1610": st.file_uploader(
                "RP01 งานรับทั้งหมด (16.10)", type=["xlsx", "xls"], key=f"{page_id}_rp01_1610"
            ),
        }
        if page_id == "history":
            uploads["rp01_2200"] = st.file_uploader(
                "RP01 หลัง 22.00", type=["xlsx", "xls"], key=f"{page_id}_rp01_2200"
            )
        else:
            uploads["rp01_2200"] = None
        uploads.update({
            "rp03": st.file_uploader(
                "RP03 GRN", type=["xlsx", "xls"], key=f"{page_id}_rp03"
            ),
            "rp42": st.file_uploader(
                "RP42 ASN Status", type=["xlsx", "xls"], key=f"{page_id}_rp42"
            ),
        })
        return uploads


st.sidebar.markdown('<div class="sb-label">Import ไฟล์แยกตามหน้า</div>', unsafe_allow_html=True)
_page_uploads = {
    "history": _render_upload_section("history", "🕘 รายงานย้อนหลัง", _page_id == "history"),
    "morning": _render_upload_section("morning", "🌅 กะเช้าปัจจุบัน", _page_id == "morning"),
}
_active_uploads = _page_uploads[_page_id]
uploaded_rp01_1610 = _active_uploads["rp01_1610"]
uploaded_rp01_2200 = _active_uploads["rp01_2200"]
uploaded_rp03 = _active_uploads["rp03"]
uploaded_rp42 = _active_uploads["rp42"]
_uploaded_files = {
    "rp01_1610": uploaded_rp01_1610,
    "rp01_2200": uploaded_rp01_2200,
    "rp03": uploaded_rp03,
    "rp42": uploaded_rp42,
}
if sheet_selection == NAV[1]:
    imported, import_error = _load_morning_metrics(_uploaded_files)
else:
    imported, import_error = _load_imported_metrics(_uploaded_files)
report_date_warnings = _report_date_warnings(_uploaded_files, imported.get("report_date"))
_uploads = (uploaded_rp01_1610, uploaded_rp01_2200, uploaded_rp03, uploaded_rp42)
_import_signature = hashlib.sha256(
    "|".join(
        f"{f.name}:{hashlib.sha256(f.getvalue()).hexdigest()}" if f is not None else "-"
        for f in _uploads
    ).encode("utf-8")
).hexdigest()
_import_signature_key = f"_last_import_signature_{_page_id}"
_new_import = _import_signature != st.session_state.get(_import_signature_key)
if sheet_selection == "สถานการณ์การรับ(กะเช้าปัจจุบัน)":
    rp01_date = imported.get("report_date")
    if rp01_date:
        st.session_state["m_date_input"] = rp01_date
    elif "m_date_input" not in st.session_state:
        latest = REPORT_STORE.get("morning_latest_date")
        st.session_state["m_date_input"] = date.fromisoformat(latest) if latest else date.today()
    st.sidebar.markdown('<div class="sb-label">วันที่รายงาน</div>', unsafe_allow_html=True)
    morning_date = st.sidebar.date_input(
        "ประจำวันที่ (กะเช้าปัจจุบัน)", value=st.session_state["m_date_input"], key="m_date_input"
    )
    selected_morning_date = morning_date.strftime("%Y-%m-%d")
    record = _get_report_record(selected_morning_date, page="morning")
    for field, default_value in MORNING_DEFAULTS.items():
        value = record.get(field, default_value) if record else default_value
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        st.session_state[field] = value
    st.session_state["_loaded_morning_date"] = selected_morning_date
    if _new_import and any(_uploads):
        for metric, value in imported.items():
            if metric in MORNING_DEFAULTS:
                st.session_state[metric] = value
        values = {field: st.session_state.get(field, default) for field, default in MORNING_DEFAULTS.items()}
        values["total_remaining"] = sum(values[field] for field in ("recv_start", "in_transit", "sup_night_missing", "sup_morning_missing"))
        _save_report_record(selected_morning_date, values, page="morning")
        REPORT_STORE = _load_report_store()
        st.session_state[_import_signature_key] = _import_signature
        st.sidebar.success(f"จำข้อมูลหน้ากะเช้าของวันที่ {selected_morning_date} แล้ว")
    else:
        st.sidebar.caption("วันที่อิงจาก RP01 · ตัวเลขและข้อมูลหน้านี้จำอัตโนมัติ")
    if st.session_state.get("_morning_autosave_error"):
        st.sidebar.error(f"บันทึกอัตโนมัติไม่สำเร็จ: {st.session_state['_morning_autosave_error']}")
else:
    rp01_date = imported.get("report_date")
    if rp01_date:
        st.session_state["h_date_input"] = rp01_date
    elif "h_date_input" not in st.session_state:
        latest = REPORT_STORE.get("latest_date")
        st.session_state["h_date_input"] = date.fromisoformat(latest) if latest else date.today()
    st.sidebar.markdown('<div class="sb-label">วันที่รายงาน</div>', unsafe_allow_html=True)
    hist_date = st.sidebar.date_input(
        "ประจำวันที่ (ย้อนหลัง)", value=st.session_state["h_date_input"], key="h_date_input"
    )
    selected_report_date = hist_date.strftime("%Y-%m-%d")
    record = _get_report_record(selected_report_date, page="history")
    for field, default_value in REPORT_DEFAULTS.items():
        value = record.get(field, default_value) if record else default_value
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        st.session_state[field] = value
    if st.session_state.get("_loaded_history_detail_date") != selected_report_date:
        st.session_state["hist_delayed_po_input"] = record.get("hist_delayed_po_input", "") if record else ""
        st.session_state["hist_reject_item_input"] = record.get("hist_reject_item_input", "") if record else ""
        st.session_state["hist_po_rp01_source"] = record.get("hist_po_rp01_source", "RP01 16.10") if record else "RP01 16.10"
        st.session_state["_loaded_history_detail_date"] = selected_report_date
    st.session_state["_loaded_report_date"] = selected_report_date
    if _new_import:
        for metric, value in imported.items():
            if metric.startswith("hist_"):
                st.session_state[metric] = value
        st.session_state[_import_signature_key] = _import_signature
    if _new_import and any(key.startswith("hist_") for key in imported):
        _autosave_current_report()
        REPORT_STORE = _load_report_store()
        st.sidebar.success(f"นำเข้าและจำข้อมูลของวันที่ {selected_report_date} แล้ว")
    elif record:
        st.sidebar.caption("โหลดข้อมูลล่าสุดของวันที่เลือกแล้ว · บันทึกอัตโนมัติ")
    else:
        st.sidebar.caption("ข้อมูลที่แก้ไขจะถูกจำไว้โดยอัตโนมัติ")
    if st.session_state.get("_autosave_error"):
        st.sidebar.error(f"บันทึกอัตโนมัติไม่สำเร็จ: {st.session_state['_autosave_error']}")
if import_error:
    st.sidebar.error(f"อ่านไฟล์ไม่สำเร็จ: {import_error}")
if imported.get("extra_join"):
    st.sidebar.info(imported["extra_join"])
_chips = "".join(
    f'<span class="sb-chip{" on" if f is not None else ""}">{n}</span>'
    for n, f in (("RP01 16.10", uploaded_rp01_1610), ("RP01 22.00", uploaded_rp01_2200), ("RP03", uploaded_rp03), ("RP42", uploaded_rp42))
)
st.sidebar.markdown(f'<div class="sb-foot">{_chips}</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><div class="hero-kicker">DCSB DISTRIBUTION CENTER · REPORT SYSTEM</div>'
    f'<div class="hero-title">{NAV_ICON[sheet_selection]} {sheet_selection}</div>'
    '<div class="hero-subtitle">ระบบสรุปยอดงานรับสินค้าและงานค้างรับคงเหลือ</div>'
    '<div class="hero-bar"></div></div>',
    unsafe_allow_html=True,
)
for warning in report_date_warnings:
    st.warning(warning)

# =========================================================================
# ชีตที่ 1: สถานการณ์การรับ (กะเช้าปัจจุบัน)
# =========================================================================
if sheet_selection == "สถานการณ์การรับ(กะเช้าปัจจุบัน)":
    inv_all = st.session_state.get("inv_all", 6058)
    night_received = st.session_state.get("night_received", 4240)
    morning_received = st.session_state.get("morning_received", 1818)
    complete_night = st.session_state.get("complete_night", 4475)
    complete_morning = st.session_state.get("complete_morning", 0)
    extra_work = st.session_state.get("extra_work", 0)
    complete_all = complete_night + complete_morning + extra_work

    pct_night_received = (complete_night / inv_all * 100) if inv_all > 0 else 0
    recv_start = st.session_state.get("recv_start", 473)
    in_transit = st.session_state.get("in_transit", 268)
    sup_night_missing = st.session_state.get("sup_night_missing", 239)
    sup_morning_missing = st.session_state.get("sup_morning_missing", 0)
    total_remaining = recv_start + in_transit + sup_night_missing + sup_morning_missing
    st.session_state["total_remaining"] = total_remaining
    pct_remaining = ((sup_night_missing + sup_morning_missing) / inv_all * 100) if inv_all > 0 else 0

    st.markdown(
        f"""
    <div class="focus-grid">
        <div class="focus-card">
        <div class="focus-label">📦 ยอดงาน Complete รวมทั้งหมด</div>
            <div class="focus-value">{complete_all:,} <span>Pallets</span></div>
            <div class="focus-unit">รวมกะดึก + กะเช้า + งานนอกรอบ</div>
        </div>
        <div class="focus-card alert">
            <div class="focus-label">🚨 Supplier ที่ยังไม่ Check-in</div>
            <div class="focus-value">{sup_night_missing + sup_morning_missing:,} <span>Pallets</span></div>
            <div class="focus-unit">แยกช่วงเวลาไว้ในตารางสรุปด้านล่าง</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">ตารางสรุปรายงาน</div>', unsafe_allow_html=True)
    report_values = [
        ("group", "ภาพรวมยอดประมาณการและงานรับ"),
        ("ยอดงานประมาณการรับทั้งหมด", f"{inv_all:,}", False),
        ("ยอดงานรับกะดึก (ทั้งหมด)", f"{night_received:,}", False),
        ("ยอดงานรับกะเช้า (ทั้งหมด)", f"{morning_received:,}", False),
        ("group", "งาน Complete"),
        ("ยอดงาน Complete รับกะดึก", f"{complete_night:,}", False),
        ("ยอดงาน Complete รับกะเช้า", f"{complete_morning:,}", False),
        ("งาน Complete นอกรอบ (RP03)", f"{extra_work:,}", False),
        ("(%) สรุปยอดงานรับกะดึก", f"{pct_night_received:.2f}%", False),
        ("group", "งานรับคงเหลือ"),
        ("สรุปงานรับคงเหลือทั้งหมด\n(Pallets)", f"{total_remaining:,}", True),
        ("งานรับคงเหลือทั้งหมด\nกำลังลงสินค้า (Receiving Start)", f"{recv_start:,}", False),
        ("งานรับคงเหลือทั้งหมด\nInTransit ที่ Check-in แล้ว", f"{in_transit:,}", False),
        ("งานรับคงเหลือทั้งหมด\nSupplier ที่ยังไม่มาส่งกะดึก", f"{sup_night_missing:,}", False),
        ("งานรับคงเหลือทั้งหมด\nSupplier ที่ยังไม่มาส่งกะเช้า", f"{sup_morning_missing:,}", False),
        ("(%) Supplier ค้างรับรวม", f"{pct_remaining:.2f}%", True),
    ]
    st.markdown(
        report_table(
            "รายงานการรับสินค้าประจำวันที่",
            morning_date.strftime("%d/%m/%Y"),
            "(ตาม Window Time 00.00-23.59 น.)",
            report_values,
            6,
            compact=True,
            accent_colors=["#83c89d", "#8eb7df", "#aa94d0", "#f1bd69", "#e789a9", "#efd479", "#e99c82"],
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
                    height=220,
                ),
                use_container_width=True,
            )
    with c2:
        with st.container(key="card_radial_2"):
            chart_card_title("ยอดงาน Complete", "แยกตามช่วง Window Time")
            st.plotly_chart(
                radial_chart(
                    ["กะดึก", "กะเช้า", "นอกรอบ"],
                    [complete_night, complete_morning, extra_work],
                    height=220,
                ),
                use_container_width=True,
            )
    with c3:
        with st.container(key="card_radial_3"):
            chart_card_title("สรุปงานรับคงเหลือทั้งหมด", "หน่วย Pallets แยกตามสถานะ")
            st.plotly_chart(
                radial_chart(
                    ["กำลังลงสินค้า", "InTransit (Check-in แล้ว)", "Supplier กะดึก", "Supplier กะเช้า"],
                    [recv_start, in_transit, sup_night_missing, sup_morning_missing],
                    height=220,
                ),
                use_container_width=True,
            )

    with st.expander("✏️ ปรับปรุงข้อมูลรายงานประจำวัน", expanded=False):
        col_a, col_b, col_c = st.columns(3, gap="small")
        with col_a:
            inv_all = st.number_input(
                "ยอดงานประมาณการรับทั้งหมด", value=inv_all, step=1, key="inv_all", on_change=_autosave_morning_report
            )
            night_received = st.number_input(
                "ยอดงานรับกะดึก (ทั้งหมด)", value=night_received, step=1, key="night_received", on_change=_autosave_morning_report
            )
            morning_received = st.number_input(
                "ยอดงานรับกะเช้า (ทั้งหมด)", value=morning_received, step=1, key="morning_received", on_change=_autosave_morning_report
            )
        with col_b:
            complete_night = st.number_input(
                "ยอดงาน Complete รับกะดึก", value=complete_night, step=1, key="complete_night", on_change=_autosave_morning_report
            )
            complete_morning = st.number_input(
                "ยอดงาน Complete รับกะเช้า", value=complete_morning, step=1, key="complete_morning", on_change=_autosave_morning_report
            )
            extra_work = st.number_input(
                "งาน Complete - นอกรอบ", value=extra_work, step=1, key="extra_work", on_change=_autosave_morning_report
            )
        with col_c:
            recv_start = st.number_input(
                "กำลังลงสินค้า (Receiving Start)", value=recv_start, step=1, key="recv_start", on_change=_autosave_morning_report
            )
            in_transit = st.number_input(
                "InTransit ที่ Check-in แล้ว", value=in_transit, step=1, key="in_transit", on_change=_autosave_morning_report
            )
            sup_night_missing = st.number_input(
                "Supplier ยังไม่มาส่งกะดึก", value=sup_night_missing, step=1, key="sup_night_missing", on_change=_autosave_morning_report
            )
            sup_morning_missing = st.number_input(
                "Supplier ยังไม่มาส่งกะเช้า", value=sup_morning_missing, step=1, key="sup_morning_missing", on_change=_autosave_morning_report
            )
        if st.session_state.get("_morning_autosaved_at"):
            st.caption(f"จำข้อมูลล่าสุดอัตโนมัติ · {st.session_state['_morning_autosaved_at']}")

# =========================================================================
# ชีตที่ 2: สรุปงานรับและงานค้างส่ง(ย้อนหลัง)
# =========================================================================
else:
    with st.expander("📋 วาง PO สำหรับคำนวณเลื่อนส่งและ Reject", expanded=False):
        st.caption("ใส่ PO สำหรับเลื่อนส่ง และใส่รหัส Item สำหรับ Reject ระบบจะเทียบกับไฟล์ที่เลือกและจำรายการแยกตามวันที่")
        source_name = st.selectbox(
            "เลือก RP01 สำหรับเทียบ PO และ Item",
            ["RP01 16.10", "RP01 22.00"],
            key="hist_po_rp01_source",
            on_change=_autosave_current_report,
        )
        po_col1, po_col2 = st.columns(2, gap="small")
        with po_col1:
            st.text_area(
                "PO เลื่อนส่ง (หนึ่ง PO ต่อบรรทัด)",
                key="hist_delayed_po_input",
                height=110,
                placeholder="ตัวอย่าง:\n5011110177\n5011110673",
                on_change=_autosave_current_report,
            )
        with po_col2:
            st.text_area(
                "Item สำหรับ Reject (หนึ่ง Item ต่อบรรทัด)",
                key="hist_reject_item_input",
                height=110,
                placeholder="วางรหัส Item ที่ต้องตรวจ Reject",
                on_change=_autosave_current_report,
            )

        rp01_source = uploaded_rp01_1610 if source_name == "RP01 16.10" else uploaded_rp01_2200
        delayed_pos = st.session_state.get("hist_delayed_po_input", "")
        reject_items = st.session_state.get("hist_reject_item_input", "")
        lookup_changed = False
        if rp01_source is None:
            st.info(f"กรุณา Import {source_name} ก่อน ระบบจึงจะเทียบ PO ได้")
        else:
            if _po_values(delayed_pos):
                try:
                    delayed_value, delayed_missing = _lookup_delayed_pallets(rp01_source, delayed_pos)
                    if st.session_state.get("hist_delayed") != delayed_value:
                        st.session_state["hist_delayed"] = delayed_value
                        lookup_changed = True
                    delayed_count = len(_po_values(delayed_pos))
                    st.caption(f"เลื่อนส่ง: {delayed_value:,} Pallets · พบ PO {delayed_count - len(delayed_missing)}/{delayed_count}")
                    if delayed_missing:
                        st.warning("PO เลื่อนส่งที่ไม่พบใน RP01: " + ", ".join(delayed_missing))
                except Exception as exc:
                    st.error(f"คำนวณเลื่อนส่งไม่สำเร็จ: {exc}")
            else:
                st.caption("ยังไม่ได้วาง PO เลื่อนส่ง · ใช้ยอดที่บันทึกไว้หรือกรอกยอดเองในตัวแก้ไขด้านล่าง")

            if _po_values(reject_items):
                if uploaded_rp03 is None:
                    st.info("กรุณา Import RP03 เพื่อคำนวณ Reject")
                else:
                    try:
                        reject_value, reject_missing, reject_invalid = _lookup_reject_pallets(
                            rp01_source, uploaded_rp03, reject_items
                        )
                        if st.session_state.get("hist_not_po") != reject_value:
                            st.session_state["hist_not_po"] = reject_value
                            lookup_changed = True
                        reject_count = len(_po_values(reject_items))
                        st.caption(f"Reject: {_format_quantity(reject_value)} Pallets · พบ Item {reject_count - len(reject_missing)}/{reject_count}")
                        if reject_missing:
                            st.warning("Item Reject ที่ไม่พบใน RP01: " + ", ".join(reject_missing))
                        if reject_invalid:
                            st.warning("มี Item ที่ไม่มีค่า TI/HI สำหรับคำนวณ หรือมี TI/HI หลายชุด: " + ", ".join(reject_invalid))
                    except Exception as exc:
                        st.error(f"คำนวณ Reject ไม่สำเร็จ: {exc}")
            else:
                st.caption("ยังไม่ได้วาง Item Reject · ใช้ยอดที่บันทึกไว้หรือกรอกยอดเองในตัวแก้ไขด้านล่าง")
        if lookup_changed:
            _autosave_current_report()

    hist_inv = st.session_state.get("hist_inv", 6126)
    hist_total_recv = st.session_state.get("hist_total_recv", 5904)
    hist_complete = st.session_state.get("hist_complete", 5722)
    hist_extra = st.session_state.get("hist_extra", 138)
    hist_extra_chart = 0 if hist_extra is None else hist_extra
    hist_extra_label = "ตรวจสอบคีย์" if hist_extra is None else f"{hist_extra:,}"
    hist_delayed = st.session_state.get("hist_delayed", 0)
    hist_not_po = st.session_state.get("hist_not_po", 73)
    hist_not_billed = st.session_state.get("hist_not_billed", 250)

    hist_not_recv = hist_not_po + hist_not_billed
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
        ("งานนอกรอบ Complete", hist_extra_label, False),
        ("งานไม่ได้รับ (%)", f"{hist_pct_not_recv:.2f}%", True),
        ("เลื่อนส่ง", _format_quantity(hist_delayed), False),
        ("Reject / ส่งไม่ครบตาม PO", _format_quantity(hist_not_po), False),
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
                    ["งานรับทั้งหมด", "งาน Complete", "งานนอกรอบ", "งานไม่ได้รับทั้งหมด"],
                    [hist_total_recv, hist_complete, hist_extra_chart, hist_not_recv],
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
                    ["ยังไม่ยื่นบิล", "Reject / ส่งไม่ครบ PO", "เลื่อนส่ง"],
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
                "ประมาณการรับ (Inventory)", value=hist_inv, step=1, key="hist_inv", on_change=_autosave_current_report
            )
            hist_total_recv = st.number_input(
                "งานรับทั้งหมด (16.10 น.)", value=hist_total_recv, step=1, key="hist_total_recv", on_change=_autosave_current_report
            )
        with hc2:
            hist_complete = st.number_input(
                    "งาน Complete (22.00 น.)", value=hist_complete, step=1, key="hist_complete", on_change=_autosave_current_report
            )
            if hist_extra is not None:
                hist_extra = st.number_input(
                    "งานนอกรอบ Complete", value=hist_extra, step=1, key="hist_extra", on_change=_autosave_current_report
                )
            else:
                st.caption("งานนอกรอบยังไม่แสดงยอดจนกว่าจะจับคู่คีย์ RP01/RP03 ได้")
        with hc3:
            hist_delayed = st.number_input(
                "เลื่อนส่ง (Pallets)", value=float(hist_delayed), step=1.0, key="hist_delayed", on_change=_autosave_current_report
            )
            hist_not_po = st.number_input(
                "Reject / ส่งไม่ครบตาม PO (Pallets)", value=math.ceil(float(hist_not_po)), step=1, key="hist_not_po", on_change=_autosave_current_report
            )
        with hc4:
            hist_not_billed = st.number_input(
                "ยังไม่ยื่นบิล", value=hist_not_billed, step=1, key="hist_not_billed", on_change=_autosave_current_report
            )
        if st.session_state.get("_autosaved_at"):
            st.caption(f"จำข้อมูลล่าสุดอัตโนมัติ · {st.session_state['_autosaved_at']}")
