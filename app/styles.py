from __future__ import annotations

import streamlit as st

from app.config import BG, BLUE, BORDER, CARD, MUTED, PANEL, PURPLE, ROSE, TEAL, TEXT


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg: {BG};
            --panel: {PANEL};
            --card: {CARD};
            --border: {BORDER};
            --text: {TEXT};
            --muted: {MUTED};
            --blue: {BLUE};
            --teal: {TEAL};
            --purple: {PURPLE};
            --rose: {ROSE};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background: radial-gradient(circle at top left, rgba(59,130,246,.16), transparent 28%),
                        linear-gradient(135deg, #07111f 0%, #081423 45%, #050b14 100%);
            color: var(--text);
            font-family: Inter, sans-serif;
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none; }}
        .block-container {{
            max-width: 1760px;
            padding: .9rem 1.2rem .8rem;
        }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0b1728 0%, #07111f 100%);
            border-right: 1px solid var(--border);
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
            padding: 1.1rem .95rem;
        }}
        .title h1 {{
            margin: 0;
            font-size: 30px;
            line-height: 1.05;
            letter-spacing: -.02em;
            color: #f7fbff;
        }}
        .title p {{ margin: .35rem 0 0; color: var(--muted); font-size: 13px; }}
        .pill {{
            display: inline-flex;
            align-items: center;
            min-height: 40px;
            padding: 0 1rem;
            border-radius: 10px;
            background: rgba(18,32,51,.86);
            border: 1px solid var(--border);
            color: #e9f2ff;
            white-space: nowrap;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(6, minmax(150px, 1fr));
            gap: .75rem;
            margin: .8rem 0 .95rem;
        }}
        .kpi-card {{
            min-height: 100px;
            padding: .82rem .82rem .68rem;
            background: linear-gradient(145deg, rgba(18,32,51,.98), rgba(13,26,43,.98));
            border: 1px solid var(--border);
            border-radius: 10px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 35px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.04);
        }}
        .kpi-card::before {{
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 2px;
            background: var(--accent);
            box-shadow: 0 0 22px var(--accent);
        }}
        .kpi-label {{ color: #dbe7f8; font-weight: 700; font-size: 11px; }}
        .kpi-value {{ font-size: 23px; font-weight: 800; margin-top: .34rem; color: #fff; }}
        .kpi-foot {{ display: flex; justify-content: space-between; align-items: end; gap: .42rem; margin-top: .18rem; }}
        .kpi-change.pos {{ color: var(--teal); }}
        .kpi-change.neg {{ color: var(--rose); }}
        .kpi-change.neu {{ color: #fbbf24; }}
        .sparkline {{ width: 78px; height: 30px; opacity: .95; }}
        .panel-title {{ color: #f7fbff; font-size: 15px; font-weight: 800; margin: 0 0 .45rem; }}
        .filter-note, .insight {{
            color: #c8d4e6;
            font-size: 12px;
            line-height: 1.45;
            background: rgba(255,255,255,.035);
            border-top: 1px solid rgba(255,255,255,.06);
            padding: .62rem .72rem;
            border-radius: 8px;
            margin-top: .55rem;
        }}
        .small-stat {{
            display: flex;
            justify-content: space-between;
            gap: .5rem;
            color: #dbe7f8;
            border-top: 1px solid rgba(255,255,255,.06);
            padding-top: .75rem;
            margin-top: .75rem;
        }}
        .good {{ color: var(--teal); }}
        .bad {{ color: var(--rose); }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(145deg, rgba(18,32,51,.96), rgba(11,24,40,.96));
            border: 1px solid var(--border);
            border-radius: 10px;
            box-shadow: 0 16px 35px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.035);
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{ padding: .72rem .82rem; }}
        div[data-testid="stPlotlyChart"] {{ border-radius: 10px; overflow: hidden; }}
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background: rgba(255,255,255,.08);
            border-color: rgba(255,255,255,.12);
        }}
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {{
            max-height: 132px;
            overflow-y: auto;
        }}
        .footer {{
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: center;
            margin-top: .9rem;
            padding: .8rem 1rem;
            color: var(--muted);
            font-size: 12px;
            background: rgba(18,32,51,.78);
            border: 1px solid var(--border);
            border-radius: 10px;
        }}
        @media (max-width: 1200px) {{
            .kpi-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
            .title h1 {{ font-size: 26px; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
