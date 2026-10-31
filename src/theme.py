"""Security-console visual theme for the Firewall Traffic Analyzer.

Call apply_theme() once at the top of app.py (after st.set_page_config).
All CSS selectors live here — nowhere else in the codebase.
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Palette constants (also imported by app.py for inline HTML badges)
# ---------------------------------------------------------------------------
BG_PAGE      = "#0A0E17"
BG_PANEL     = "#101826"
BG_PANEL_ALT = "#0D1521"
BORDER       = "#1F2C44"
ACCENT_CYAN  = "#22D3EE"
ACCENT_GREEN = "#34D399"
TEXT_PRIMARY = "#E6EDF7"
TEXT_MUTED   = "#8FA3BF"
ACCENT_CYAN_DIM = "#1AA8C4"   # hover / active states

# Action colours — brightness-adjusted for dark bg, hues preserved
ACTION_BADGE: dict[str, str] = {
    "allow":      "#2ecc71",
    "deny":       "#e74c3c",
    "drop":       "#f39c12",
    "reset-both": "#9b59b6",
}

# ---------------------------------------------------------------------------
# Google Fonts — degrades gracefully offline (preconnect + swap)
# ---------------------------------------------------------------------------
_FONTS = "@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');"

# ---------------------------------------------------------------------------
# Full CSS block.
# Tokens __FONTS__, __BG_PAGE__, __BG_PANEL__, __BG_PANEL_ALT__, __BORDER__,
# __CYAN__, __GREEN__, __TEXT__, __MUTED__, __CYAN_DIM__ are substituted by
# apply_theme() via str.replace().  This avoids any str.format / f-string on
# the CSS text (which would conflict with the many literal { } in CSS rules).
# ---------------------------------------------------------------------------
_CSS = """
/* ── Reset / base ─────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* Google Fonts — loaded once; fails silently offline */
__FONTS__

/* ── CSS custom properties ────────────────────────────────────────────── */
:root {
  --bg-page:      __BG_PAGE__;
  --bg-panel:     __BG_PANEL__;
  --bg-panel-alt: __BG_PANEL_ALT__;
  --border:       __BORDER__;
  --cyan:         __CYAN__;
  --green:        __GREEN__;
  --text:         __TEXT__;
  --muted:        __MUTED__;
  --mono: 'JetBrains Mono', 'Fira Code', ui-monospace, Menlo, Consolas, monospace;
  --sans: 'Inter', system-ui, 'Segoe UI', Roboto, sans-serif;
  --radius: 6px;
  --glow: 0 0 12px rgba(34,211,238,.18);
}

/* ── Page background + static grid ───────────────────────────────────── */
[data-testid="stAppViewContainer"] > .main {
  background-color: var(--bg-page);
  background-image:
    linear-gradient(rgba(34,211,238,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34,211,238,.04) 1px, transparent 1px);
  background-size: 40px 40px;
  color: var(--text);
  font-family: var(--sans);
}

/* ── Block container padding ─────────────────────────────────────────── */
[data-testid="stAppViewContainer"] .block-container {
  padding-top: 1.6rem !important;
  padding-bottom: 3rem !important;
  max-width: 1400px;
}

/* ── Hide default Streamlit chrome ───────────────────────────────────── */
#MainMenu { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; border: none !important; }

/* ══════════════════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: #080D16 !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 1rem 0.8rem;
}

/* Sidebar text colours */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--text) !important;
  font-family: var(--mono) !important;
  letter-spacing: .03em;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
  color: var(--muted) !important;
  font-family: var(--sans) !important;
  font-size: 0.82rem;
}
[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
  margin: 0.6rem 0;
}

/* ── Sidebar radio (console-menu) ─────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  display: flex;
  align-items: center;
  padding: 0.42rem 0.75rem;
  margin: 1px 0;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background .15s;
  font-family: var(--mono) !important;
  font-size: 0.83rem !important;
  color: var(--muted) !important;
  position: relative;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(34,211,238,.07);
  color: var(--text) !important;
}
/* Hide the native radio button circle */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
  font-family: var(--mono) !important;
  font-size: 0.83rem !important;
  color: inherit !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
  display: none;
}
/* Active item: cyan left bar via sibling trick — works on checked state */
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"]:checked + div {
  border-left: 3px solid var(--cyan);
  padding-left: 0.6rem;
  color: var(--cyan) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] {
  color: var(--cyan) !important;
  border-left: 3px solid var(--cyan);
  padding-left: 0.55rem;
  background: rgba(34,211,238,.06);
}

/* ── Sidebar system-status panel ─────────────────────────────────────── */
.fw-status-panel {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.6rem 0.8rem;
  margin: 0.4rem 0;
}
.fw-status-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0.2rem 0;
}
.fw-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}
.fw-dot-green  { background: #2ecc71; box-shadow: 0 0 6px #2ecc71aa; }
.fw-dot-amber  { background: #f39c12; box-shadow: 0 0 6px #f39c12aa; }
.fw-dot-red    { background: #e74c3c; box-shadow: 0 0 6px #e74c3caa; }
.fw-status-label { color: var(--text); }

/* ══════════════════════════════════════════════════════════════════════
   PAGE HEADERS
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] .block-container h1 {
  font-family: var(--mono) !important;
  font-size: 1.55rem !important;
  font-weight: 600;
  color: var(--text) !important;
  letter-spacing: .04em;
  padding-left: 0.9rem;
  border-left: 3px solid var(--cyan);
  margin-bottom: 0.1rem !important;
  text-shadow: 0 0 20px rgba(34,211,238,.25);
}

/* Glowing page-header divider — injected via st.markdown with class fw-page-divider */
.fw-page-divider {
  height: 1px;
  margin: 0.35rem 0 1rem 0;
  background: linear-gradient(90deg, var(--cyan) 0%, rgba(34,211,238,.15) 60%, transparent 100%);
  box-shadow: 0 0 8px rgba(34,211,238,.35);
  border: none;
}

[data-testid="stAppViewContainer"] .block-container h2 {
  font-family: var(--mono) !important;
  font-size: 1.1rem !important;
  color: var(--text) !important;
  letter-spacing: .03em;
  margin-top: 1.4rem !important;
}
[data-testid="stAppViewContainer"] .block-container h3 {
  font-family: var(--mono) !important;
  font-size: 0.97rem !important;
  color: var(--cyan) !important;
}

/* caption / small text */
[data-testid="stAppViewContainer"] .block-container [data-testid="stCaptionContainer"] p,
[data-testid="stAppViewContainer"] .block-container small {
  color: var(--muted) !important;
  font-size: 0.8rem !important;
}

/* ══════════════════════════════════════════════════════════════════════
   METRIC CARDS
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-top: 2px solid var(--cyan) !important;
  border-radius: var(--radius) !important;
  padding: 14px 16px !important;
  transition: box-shadow .2s;
}
[data-testid="stMetric"]:hover {
  box-shadow: var(--glow) !important;
}
[data-testid="stMetricLabel"] p {
  font-family: var(--sans) !important;
  font-size: 0.75rem !important;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--mono) !important;
  font-size: 1.5rem !important;
  font-weight: 600;
  color: var(--text) !important;
}
[data-testid="stMetricDelta"] {
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
}

/* ══════════════════════════════════════════════════════════════════════
   CALLOUTS (info / warning / error / success)
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
  background: var(--bg-panel) !important;
  border-radius: var(--radius) !important;
  border-top: none !important;
  border-right: none !important;
  border-bottom: none !important;
  padding: 0.7rem 1rem !important;
}
/* info */
[data-testid="stAlert"][data-baseweb="notification"][kind="info"],
div[data-testid^="stNotification"][class*="info"],
[data-testid="stAlert"]:has(svg[data-testid*="info"]) {
  border-left: 3px solid #22D3EE !important;
}
/* warning */
[data-testid="stAlert"][kind="warning"],
[data-testid="stAlert"]:has(svg[data-testid*="warning"]) {
  border-left: 3px solid #f39c12 !important;
}
/* error */
[data-testid="stAlert"][kind="error"],
[data-testid="stAlert"]:has(svg[data-testid*="error"]) {
  border-left: 3px solid #e74c3c !important;
}
/* success */
[data-testid="stAlert"][kind="success"],
[data-testid="stAlert"]:has(svg[data-testid*="success"]) {
  border-left: 3px solid #2ecc71 !important;
}
/* Fallback: style all stAlert with a generic left border */
[data-testid="stAlert"] {
  border-left: 3px solid var(--cyan) !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div {
  color: var(--text) !important;
  font-family: var(--sans) !important;
  font-size: 0.875rem !important;
}

/* ══════════════════════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  color: var(--muted) !important;
  font-family: var(--mono) !important;
  font-size: 0.82rem !important;
  padding: 0.5rem 1rem !important;
  margin-bottom: -1px;
  transition: color .15s, border-color .15s;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
  color: var(--text) !important;
  border-bottom-color: var(--cyan) !important;
  background: rgba(34,211,238,.04) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
  background: rgba(34,211,238,.06) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  padding: 1rem 0 0 0 !important;
  background: transparent !important;
}

/* ══════════════════════════════════════════════════════════════════════
   EXPANDERS
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  margin-bottom: 0.5rem;
}
[data-testid="stExpander"] summary {
  font-family: var(--mono) !important;
  font-size: 0.85rem !important;
  color: var(--text) !important;
  padding: 0.6rem 0.8rem !important;
}
[data-testid="stExpander"] summary:hover {
  background: rgba(34,211,238,.05) !important;
  color: var(--cyan) !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  padding: 0.2rem 0.8rem 0.8rem 0.8rem !important;
  border-top: 1px solid var(--border) !important;
}

/* ══════════════════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════════════════ */
/* Primary */
[data-testid="stBaseButton-primary"],
button[kind="primary"] {
  background: linear-gradient(135deg, var(--cyan) 0%, __CYAN_DIM__ 100%) !important;
  color: #070C16 !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-family: var(--mono) !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  letter-spacing: .04em;
  transition: filter .15s, box-shadow .15s;
}
[data-testid="stBaseButton-primary"]:hover,
button[kind="primary"]:hover {
  filter: brightness(1.1);
  box-shadow: 0 0 14px rgba(34,211,238,.4) !important;
}
[data-testid="stBaseButton-primary"]:focus-visible,
button[kind="primary"]:focus-visible {
  outline: 2px solid var(--cyan) !important;
  outline-offset: 2px !important;
}

/* Secondary / default */
[data-testid="stBaseButton-secondary"],
button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
  font-family: var(--mono) !important;
  font-size: 0.84rem !important;
  transition: border-color .15s, color .15s;
}
[data-testid="stBaseButton-secondary"]:hover,
button[kind="secondary"]:hover {
  border-color: var(--cyan) !important;
  color: var(--cyan) !important;
  background: rgba(34,211,238,.06) !important;
}
[data-testid="stBaseButton-secondary"]:focus-visible,
button[kind="secondary"]:focus-visible {
  outline: 2px solid var(--cyan) !important;
  outline-offset: 2px !important;
}

/* Download button same as secondary */
[data-testid="stDownloadButton"] button {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
  font-family: var(--mono) !important;
  font-size: 0.82rem !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--cyan) !important;
  color: var(--cyan) !important;
}
[data-testid="stDownloadButton"] button:focus-visible {
  outline: 2px solid var(--cyan) !important;
  outline-offset: 2px !important;
}

/* ══════════════════════════════════════════════════════════════════════
   FORM INPUTS (text, number, select, multiselect, slider, toggle)
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--mono) !important;
  font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 2px rgba(34,211,238,.2) !important;
  outline: none !important;
}
[data-testid="stTextInput"] input:disabled,
[data-testid="stNumberInput"] input:disabled {
  background: var(--bg-panel-alt) !important;
  color: var(--muted) !important;
  border-style: dashed !important;
}

/* Labels for inputs */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stSlider"] label,
[data-testid="stToggle"] label,
[data-testid="stCheckbox"] label {
  font-family: var(--sans) !important;
  font-size: 0.8rem !important;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: .06em;
}

/* Selectbox */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] {
  background: var(--bg-panel) !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
  font-family: var(--mono) !important;
  font-size: 0.85rem !important;
  border-radius: var(--radius) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 2px rgba(34,211,238,.18) !important;
}
/* Multiselect */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background: var(--bg-panel) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--mono) !important;
  font-size: 0.83rem !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
  background: rgba(34,211,238,.15) !important;
  border: 1px solid var(--cyan) !important;
  color: var(--cyan) !important;
  font-family: var(--mono) !important;
  font-size: 0.75rem !important;
  border-radius: 4px !important;
}

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderThumb"] {
  background: var(--cyan) !important;
  border-color: var(--cyan) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="progressbar"] {
  background: var(--cyan) !important;
}

/* Toggle */
[data-testid="stToggle"] input:checked + div {
  background: var(--cyan) !important;
}

/* Checkbox */
[data-testid="stCheckbox"] input:checked + div {
  background: var(--cyan) !important;
  border-color: var(--cyan) !important;
}

/* ══════════════════════════════════════════════════════════════════════
   FILE UPLOADER
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploadDropzone"] {
  background: var(--bg-panel) !important;
  border: 1px dashed var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--muted) !important;
}
[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--cyan) !important;
}

/* ══════════════════════════════════════════════════════════════════════
   DATAFRAMES / TABLES
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden;
}
/* Header row */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"] {
  background: #0D1521 !important;
  color: var(--cyan) !important;
  font-family: var(--mono) !important;
  font-size: 0.76rem !important;
  text-transform: uppercase;
  letter-spacing: .07em;
  border-bottom: 1px solid var(--border) !important;
  padding: 6px 10px !important;
}
/* Data cells */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] [role="gridcell"] {
  background: var(--bg-panel) !important;
  color: var(--text) !important;
  font-family: var(--mono) !important;
  font-size: 0.82rem !important;
  border-bottom: 1px solid rgba(31,44,68,.6) !important;
  padding: 5px 10px !important;
}
[data-testid="stDataFrame"] tr:hover td,
[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {
  background: rgba(34,211,238,.04) !important;
}

/* Code blocks */
[data-testid="stCodeBlock"] pre,
[data-testid="stCodeBlock"] code {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--green) !important;
  font-family: var(--mono) !important;
  font-size: 0.82rem !important;
}

/* ══════════════════════════════════════════════════════════════════════
   DIVIDERS
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1.2rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════════════
   FOOTER BAR (injected via st.markdown in app.py)
   ══════════════════════════════════════════════════════════════════════ */
.fw-footer {
  border-top: 1px solid var(--border);
  padding: 0.6rem 0;
  margin-top: 0.8rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  color: var(--muted);
  text-align: center;
  letter-spacing: .02em;
}
.fw-footer strong {
  color: var(--text);
}

/* ══════════════════════════════════════════════════════════════════════
   ACTION PILL BADGE (injected in prediction result)
   ══════════════════════════════════════════════════════════════════════ */
.fw-action-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 4px 14px 4px 10px;
  border-radius: 20px;
  border: 1.5px solid currentColor;
  font-family: var(--mono);
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.fw-action-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}
.fw-prediction-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0 0.5rem 0;
}
.fw-prediction-label {
  font-family: var(--mono);
  font-size: 0.82rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .08em;
}

/* ══════════════════════════════════════════════════════════════════════
   SHIELD LOGO (sidebar)
   ══════════════════════════════════════════════════════════════════════ */
.fw-sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.2rem;
}
.fw-sidebar-title {
  font-family: var(--mono) !important;
  font-size: 1.0rem !important;
  font-weight: 600;
  color: var(--text) !important;
  line-height: 1.2;
}
.fw-sidebar-subtitle {
  font-family: var(--sans) !important;
  font-size: 0.72rem !important;
  color: var(--muted) !important;
  margin-top: 0.1rem;
}

/* ══════════════════════════════════════════════════════════════════════
   PLOTLY CHARTS — transparent container
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] {
  background: transparent !important;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
[data-testid="stPlotlyChart"] > div {
  background: transparent !important;
}

/* ══════════════════════════════════════════════════════════════════════
   FORM container
   ══════════════════════════════════════════════════════════════════════ */
[data-testid="stForm"] {
  background: var(--bg-panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1rem 1rem 0.5rem 1rem !important;
}

/* ══════════════════════════════════════════════════════════════════════
   REDUCED-MOTION safeguard
   ══════════════════════════════════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition: none !important;
    animation: none !important;
  }
}

/* ══════════════════════════════════════════════════════════════════════
   NARROW SCREENS (~900 px)
   ══════════════════════════════════════════════════════════════════════ */
@media (max-width: 960px) {
  [data-testid="stAppViewContainer"] .block-container {
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
  }
  [data-testid="stMetricValue"] {
    font-size: 1.15rem !important;
  }
  [data-testid="stAppViewContainer"] .block-container h1 {
    font-size: 1.2rem !important;
  }
}
"""


def apply_theme() -> None:
    """Inject the security-console CSS once per Streamlit run.

    Uses str.replace() with double-underscore tokens instead of str.format(),
    so the many literal { } braces in the CSS do not need escaping.
    """
    css = (
        _CSS
        .replace("__FONTS__",       _FONTS)
        .replace("__BG_PAGE__",     BG_PAGE)
        .replace("__BG_PANEL_ALT__", BG_PANEL_ALT)   # longer token first
        .replace("__BG_PANEL__",    BG_PANEL)
        .replace("__BORDER__",      BORDER)
        .replace("__CYAN_DIM__",    ACCENT_CYAN_DIM)  # longer token first
        .replace("__CYAN__",        ACCENT_CYAN)
        .replace("__GREEN__",       ACCENT_GREEN)
        .replace("__TEXT__",        TEXT_PRIMARY)
        .replace("__MUTED__",       TEXT_MUTED)
    )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Decorative helpers used in app.py
# ---------------------------------------------------------------------------

SHIELD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24"
  fill="none" stroke="#22D3EE" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
  aria-hidden="true" focusable="false">
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  <polyline points="9 12 11 14 15 10"/>
</svg>"""


def sidebar_header_html(model_available: bool, using_test_artifacts: bool) -> str:
    """Return the HTML for the sidebar shield header + system-status panel."""
    if using_test_artifacts:
        dot_cls = "fw-dot-red"
        status_label = "TEST ARTIFACT"
        status_color = "#e74c3c"
    elif model_available:
        dot_cls = "fw-dot-green"
        status_label = "Model available"
        status_color = "#2ecc71"
    else:
        dot_cls = "fw-dot-amber"
        status_label = "Dataset / visualization mode"
        status_color = "#f39c12"

    return f"""
<div class="fw-sidebar-header">
  {SHIELD_SVG}
  <div>
    <div class="fw-sidebar-title">🛡️ Firewall Intelligence</div>
    <div class="fw-sidebar-subtitle">Intelligent Firewall Traffic Analyzer</div>
  </div>
</div>
<div class="fw-status-panel" style="margin-top:0.6rem;">
  <div style="font-family:var(--mono,monospace);font-size:0.68rem;text-transform:uppercase;
              letter-spacing:.1em;color:{TEXT_MUTED};margin-bottom:0.3rem;">System Status</div>
  <div class="fw-status-row">
    <span class="fw-dot {dot_cls}"></span>
    <span class="fw-status-label" style="color:{status_color};">{status_label}</span>
  </div>
  <div class="fw-status-row" style="margin-top:0.15rem;">
    <span style="color:{TEXT_MUTED};font-size:0.74rem;">
      Research prototype · Historical traffic classification
    </span>
  </div>
</div>
"""


def page_divider_html() -> str:
    """Return the glowing cyan page-header divider."""
    return '<hr class="fw-page-divider" aria-hidden="true">'


def action_badge_html(action: str, color: str) -> str:
    """Return a pill badge for the predicted action."""
    return (
        f'<div class="fw-prediction-row">'
        f'  <span class="fw-prediction-label">Predicted action</span>'
        f'  <span class="fw-action-badge" style="color:{color};">'
        f'    <span class="fw-action-dot" style="background:{color};'
        f'          box-shadow:0 0 6px {color}88;"></span>'
        f'    {action.upper()}'
        f'  </span>'
        f'</div>'
    )


def footer_html(text: str) -> str:
    """Return styled footer HTML."""
    return f'<div class="fw-footer">{text}</div>'
