from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "processed_movies.csv"

BG = "#07111f"
PANEL = "#0f1c2d"
CARD = "#122033"
BORDER = "rgba(128, 164, 218, 0.18)"
TEXT = "#f2f6ff"
MUTED = "#9aa9bd"
BLUE = "#3b82f6"
TEAL = "#2dd4bf"
PURPLE = "#a855f7"
AMBER = "#fbbf24"
ROSE = "#fb7185"
GREEN = "#86efac"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CORE_GENRES = [
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Thriller",
    "Science Fiction",
    "Horror",
    "Romance",
    "Crime",
    "Fantasy",
    "Animation",
    "Family",
    "Mystery",
]


st.set_page_config(
    page_title="IMDB Movie Analytics Dashboard",
    page_icon="IMDB",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
            --amber: {AMBER};
            --rose: {ROSE};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background: radial-gradient(circle at top left, rgba(59,130,246,.16), transparent 28%),
                        linear-gradient(135deg, #07111f 0%, #081423 45%, #050b14 100%);
            color: var(--text);
            font-family: Inter, sans-serif;
        }}

        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"] {{ display: none; }}
        [data-testid="stDecoration"] {{ display: none; }}
        .block-container {{
            padding: 1.05rem 1.25rem .8rem 1.25rem;
            max-width: 1660px;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0b1728 0%, #07111f 100%);
            border-right: 1px solid var(--border);
            width: 108px !important;
            min-width: 108px !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
            padding: 1rem .75rem;
        }}
        .nav-logo {{
            width: 48px; height: 48px; margin: .25rem auto .7rem auto;
            border-radius: 12px; display: grid; place-items: center;
            background: rgba(59,130,246,.15);
            border: 1px solid rgba(59,130,246,.45);
            box-shadow: 0 0 26px rgba(59,130,246,.22);
            color: #8fd3ff; font-weight: 800;
        }}
        .nav-item {{
            height: 72px; margin: .22rem auto; border-radius: 12px;
            display: flex; flex-direction: column; gap: 6px; align-items: center; justify-content: center;
            color: #b8c4d8; font-size: 12px;
        }}
        .nav-item.active {{
            background: rgba(59,130,246,.15); color: #8fd3ff;
            border: 1px solid rgba(59,130,246,.28);
        }}
        .nav-icon svg {{ width: 21px; height: 21px; stroke: currentColor; fill: none; stroke-width: 1.8; }}

        .topbar {{
            display: flex; justify-content: space-between; align-items: flex-start;
            gap: 1rem; margin-bottom: 1rem;
        }}
        .title h1 {{
            margin: 0; font-size: 32px; line-height: 1.05; letter-spacing: -.02em; color: #f7fbff;
        }}
        .title p {{ margin: .35rem 0 0 0; color: var(--muted); font-size: 16px; }}
        .top-controls {{ display: flex; gap: .75rem; align-items: center; }}
        .pill {{
            display: inline-flex; align-items: center; gap: .55rem;
            min-height: 44px; padding: 0 1rem; border-radius: 10px;
            background: rgba(18,32,51,.86); border: 1px solid var(--border);
            color: #e9f2ff; box-shadow: inset 0 0 24px rgba(255,255,255,.015);
            white-space: nowrap;
        }}

        .kpi-grid {{
            display: grid; grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: .9rem; margin-bottom: .9rem;
        }}
        .kpi-card {{
            min-height: 118px; padding: 1rem 1rem .85rem;
            background: linear-gradient(145deg, rgba(18,32,51,.98), rgba(13,26,43,.98));
            border: 1px solid var(--border); border-radius: 10px; position: relative; overflow: hidden;
            box-shadow: 0 16px 35px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.04);
        }}
        .kpi-card::before {{
            content: ""; position: absolute; inset: 0 auto 0 0; width: 2px; background: var(--accent);
            box-shadow: 0 0 22px var(--accent);
        }}
        .kpi-label {{ color: #dbe7f8; font-weight: 700; font-size: 13px; }}
        .kpi-value {{ font-size: 27px; font-weight: 800; margin-top: .45rem; color: #fff; letter-spacing: -.02em; }}
        .kpi-foot {{ display: flex; justify-content: space-between; align-items: end; gap: .5rem; margin-top: .3rem; }}
        .kpi-change.pos {{ color: var(--teal); }}
        .kpi-change.neg {{ color: var(--rose); }}
        .kpi-change.neu {{ color: var(--amber); }}
        .sparkline {{ width: 94px; height: 34px; opacity: .95; }}

        .panel {{
            background: linear-gradient(145deg, rgba(18,32,51,.98), rgba(11,24,40,.98));
            border: 1px solid var(--border); border-radius: 10px;
            box-shadow: 0 16px 35px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.035);
            padding: 1rem;
        }}
        .panel-title {{
            color: #f7fbff; font-size: 17px; font-weight: 800; margin: 0 0 .65rem 0;
        }}
        .filter-note, .insight {{
            color: #c8d4e6; font-size: 13px; line-height: 1.5;
            background: rgba(255,255,255,.035); border-top: 1px solid rgba(255,255,255,.06);
            padding: .72rem .8rem; border-radius: 8px; margin-top: .8rem;
        }}
        .small-stat {{
            display: flex; justify-content: space-between; color: #dbe7f8;
            border-top: 1px solid rgba(255,255,255,.06); padding-top: .75rem; margin-top: .75rem;
        }}
        .good {{ color: var(--teal); }}
        .bad {{ color: var(--rose); }}

        div[data-testid="stMetric"] {{
            background: var(--card); border: 1px solid var(--border); padding: .8rem;
            border-radius: 10px;
        }}
        div[data-testid="stPlotlyChart"] {{
            border-radius: 10px; overflow: hidden;
        }}
        .stSlider, .stMultiSelect, .stNumberInput, .stRadio, .stSelectbox {{
            color: var(--text);
        }}
        label, [data-testid="stWidgetLabel"] {{ color: #dbe7f8 !important; font-weight: 600; }}
        .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq {{ justify-content: center; }}

        .footer {{
            display: flex; justify-content: space-between; gap: 1rem; align-items: center;
            margin-top: .8rem; padding: .8rem 1rem; color: var(--muted); font-size: 12px;
            background: rgba(18,32,51,.78); border: 1px solid var(--border); border-radius: 10px;
        }}

        @media (max-width: 1200px) {{
            .kpi-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
            .title h1 {{ font-size: 26px; }}
            .topbar {{ flex-direction: column; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def svg_icon(kind: str) -> str:
    icons = {
        "home": '<svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-6h5v6"/></svg>',
        "grid": '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="6" height="6"/><rect x="14" y="4" width="6" height="6"/><rect x="4" y="14" width="6" height="6"/><rect x="14" y="14" width="6" height="6"/></svg>',
        "star": '<svg viewBox="0 0 24 24"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg>',
        "clock": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 7v5l3.5 2"/></svg>',
        "gear": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.4 1a8 8 0 0 0-1.7-1L14.5 3h-5l-.3 3.1a8 8 0 0 0-1.7 1l-2.4-1-2 3.4 2 1.5a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.4-1a8 8 0 0 0 1.7 1l.3 3.1h5l.3-3.1a8 8 0 0 0 1.7-1l2.4 1 2-3.4-2-1.5c.1-.3.1-.7.1-1Z"/></svg>',
        "export": '<svg viewBox="0 0 24 24"><path d="M14 4h6v6"/><path d="m20 4-9 9"/><path d="M20 14v5H5V4h5"/></svg>',
    }
    return icons[kind]


def render_sidebar() -> None:
    items = [
        ("home", "Overview", True),
        ("grid", "Revenue", False),
        ("star", "Genres", False),
        ("clock", "Time", False),
        ("gear", "Settings", False),
        ("export", "Export", False),
    ]
    with st.sidebar:
        st.markdown('<div class="nav-logo">IM</div>', unsafe_allow_html=True)
        for icon, label, active in items:
            st.markdown(
                f"""
                <div class="nav-item {'active' if active else ''}">
                  <div class="nav-icon">{svg_icon(icon)}</div>
                  <div>{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_dataset.py")],
            check=True,
            cwd=ROOT,
        )
    df = pd.read_csv(DATA_FILE)
    numeric_cols = [
        "budget",
        "revenue",
        "year",
        "release_month",
        "runtime",
        "popularity",
        "tmdb_vote_count",
        "rating_count",
        "analysis_vote_count",
        "avg_rating",
        "roi",
    ]
    for column in numeric_cols:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["genres"] = df["genres"].fillna("")
    df["primary_genre"] = df["primary_genre"].fillna("Unknown")
    return df


def money(value: float) -> str:
    if pd.isna(value):
        return "0"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def compact_number(value: float) -> str:
    if pd.isna(value):
        return "0"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def metric_delta(current: float, previous: float, suffix: str = "%") -> tuple[str, str]:
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return "0.0%", "neu"
    delta = ((current - previous) / abs(previous)) * 100
    return f"{delta:+.1f}{suffix}", "pos" if delta >= 0 else "neg"


def sparkline_svg(values: list[float], color: str) -> str:
    clean = [float(v) for v in values if not pd.isna(v)]
    if len(clean) < 2:
        clean = [0, 0]
    min_value = min(clean)
    max_value = max(clean)
    spread = max(max_value - min_value, 1)
    points = []
    for index, value in enumerate(clean[-12:]):
        x = 4 + index * (86 / max(len(clean[-12:]) - 1, 1))
        y = 30 - ((value - min_value) / spread) * 24
        points.append(f"{x:.1f},{y:.1f}")
    return (
        f'<svg class="sparkline" viewBox="0 0 96 36">'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M4 32 L{" L".join(points)} L92 34 L4 34Z" fill="{color}" opacity=".13"/></svg>'
    )


def kpi_card(label: str, value: str, change: str, tone: str, accent: str, series: list[float]) -> str:
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-foot">
        <div class="kpi-change {tone}">{change}</div>
        {sparkline_svg(series, accent)}
      </div>
    </div>
    """


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    genre_df = df.copy()
    genre_df["genre"] = genre_df["genres"].str.split("|")
    genre_df = genre_df.explode("genre")
    genre_df["genre"] = genre_df["genre"].replace("", np.nan)
    return genre_df.dropna(subset=["genre"])


def apply_filters(df: pd.DataFrame, year_range, selected_genres, min_votes: int) -> pd.DataFrame:
    filtered = df[
        (df["year"] >= year_range[0])
        & (df["year"] <= year_range[1])
        & (df["analysis_vote_count"].fillna(0) >= min_votes)
    ].copy()
    if selected_genres:
        selected = set(selected_genres)
        genre_mask = filtered["genres"].apply(
                lambda value: bool(selected.intersection(str(value).split("|")))
            ).astype(bool)
        filtered = filtered[genre_mask]
    return filtered


def previous_period(df: pd.DataFrame, year_range, selected_genres, min_votes: int) -> pd.DataFrame:
    span = year_range[1] - year_range[0] + 1
    prev_range = (year_range[0] - span, year_range[0] - 1)
    return apply_filters(df, prev_range, selected_genres, min_votes)


def chart_layout(height: int = 300) -> dict:
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#dbe7f8", "family": "Inter"},
        "margin": {"l": 52, "r": 24, "t": 16, "b": 46},
        "xaxis": {
            "gridcolor": "rgba(154,169,189,.18)",
            "zerolinecolor": "rgba(154,169,189,.16)",
            "linecolor": "rgba(154,169,189,.35)",
        },
        "yaxis": {
            "gridcolor": "rgba(154,169,189,.18)",
            "zerolinecolor": "rgba(154,169,189,.16)",
            "linecolor": "rgba(154,169,189,.35)",
        },
        "legend": {"orientation": "h", "y": 1.12, "x": 0},
    }


def empty_chart(message: str, height: int = 300) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        showarrow=False,
        font={"color": MUTED, "size": 15},
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
    )
    fig.update_layout(**chart_layout(height))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def scatter_with_trend(df: pd.DataFrame, x: str, y: str, color: str, height: int, y_cap=None) -> go.Figure:
    clean = df[[x, y, "title", "primary_genre"]].dropna()
    clean = clean[(clean[x] > 0) & (clean[y] > 0)]
    if y_cap is not None and not clean.empty:
        clean = clean[clean[y] <= y_cap]
    if len(clean) < 3:
        return empty_chart("当前筛选条件下数据不足", height)

    fig = px.scatter(
        clean,
        x=x,
        y=y,
        hover_name="title",
        hover_data={"primary_genre": True, x: ":,.0f", y: ":,.2f"},
        color_discrete_sequence=[color],
        trendline="ols",
    )
    fig.update_traces(marker={"size": 7, "opacity": 0.72, "line": {"width": 0}})
    for trace in fig.data:
        if trace.mode == "lines":
            trace.line.color = "#dceaff"
            trace.line.width = 2
    fig.update_layout(**chart_layout(height))
    return fig


def genre_roi_chart(df: pd.DataFrame, metric: str, top_n: int) -> go.Figure:
    genre_df = explode_genres(df)
    if genre_df.empty:
        return empty_chart("当前筛选条件下没有类型数据", 300)

    if metric == "ROI":
        valid = genre_df.dropna(subset=["roi"])
        grouped = valid.groupby("genre", as_index=False)["roi"].median()
        y_col = "roi"
        y_title = "ROI (x)"
    else:
        valid = genre_df[genre_df["revenue"] > 0]
        grouped = valid.groupby("genre", as_index=False)["revenue"].mean()
        y_col = "revenue"
        y_title = "Avg Revenue"

    grouped = grouped.sort_values(y_col, ascending=False).head(top_n)
    if grouped.empty:
        return empty_chart("当前筛选条件下没有可展示的收益数据", 300)

    fig = px.bar(
        grouped,
        x="genre",
        y=y_col,
        color=y_col,
        color_continuous_scale=[BLUE, PURPLE],
        text=grouped[y_col].map(lambda value: f"{value:.1f}x" if metric == "ROI" else money(value)),
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(**chart_layout(300), coloraxis_showscale=False)
    fig.update_xaxes(title="Genres")
    fig.update_yaxes(title=y_title)
    return fig


def revenue_month_chart(df: pd.DataFrame) -> go.Figure:
    valid = df[(df["revenue"] > 0) & df["release_month"].notna()]
    if valid.empty:
        return empty_chart("当前筛选条件下没有月份收入数据", 242)
    grouped = valid.groupby("release_month", as_index=False)["revenue"].mean()
    grouped["month"] = grouped["release_month"].map(lambda month: MONTHS[int(month) - 1])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=grouped["month"],
            y=grouped["revenue"],
            mode="lines+markers",
            line={"color": TEAL, "width": 3},
            marker={"size": 7, "color": "#6ee7b7"},
            fill="tozeroy",
            fillcolor="rgba(45,212,191,.18)",
            hovertemplate="%{x}<br>Avg revenue: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(**chart_layout(242))
    fig.update_yaxes(title="Revenue (USD)")
    fig.update_xaxes(title="Month")
    return fig


def rating_box_chart(df: pd.DataFrame) -> go.Figure:
    genre_df = explode_genres(df.dropna(subset=["avg_rating"]))
    genre_df = genre_df[genre_df["genre"].isin(CORE_GENRES)]
    if genre_df.empty:
        return empty_chart("当前筛选条件下没有评分分布数据", 242)
    order = (
        genre_df.groupby("genre")["avg_rating"]
        .median()
        .sort_values(ascending=False)
        .head(11)
        .index.tolist()
    )
    genre_df = genre_df[genre_df["genre"].isin(order)]
    fig = px.box(
        genre_df,
        x="genre",
        y="avg_rating",
        color="genre",
        category_orders={"genre": order},
        color_discrete_sequence=[BLUE, PURPLE, TEAL, AMBER, ROSE],
        points="outliers",
    )
    fig.update_layout(**chart_layout(242), showlegend=False)
    fig.update_yaxes(title="Rating", range=[0, 10])
    fig.update_xaxes(title="Genre")
    return fig


def compute_kpis(filtered: pd.DataFrame, previous: pd.DataFrame) -> list[dict]:
    valid_revenue = filtered[filtered["revenue"] > 0]
    valid_budget = filtered[filtered["budget"] > 0]
    valid_roi = filtered.dropna(subset=["roi"])
    valid_rating = filtered.dropna(subset=["avg_rating"])
    prev_revenue = previous[previous["revenue"] > 0]
    prev_roi = previous.dropna(subset=["roi"])
    prev_rating = previous.dropna(subset=["avg_rating"])

    by_year = filtered.groupby("year", as_index=False).agg(
        movies=("movie_id", "count"),
        revenue=("revenue", lambda values: values[values > 0].mean()),
        roi=("roi", "median"),
        rating=("avg_rating", "mean"),
        budget=("budget", lambda values: values[values > 0].sum()),
    )

    values = [
        (
            "Total Movies",
            compact_number(len(filtered)),
            len(filtered),
            len(previous),
            BLUE,
            by_year["movies"].tolist(),
        ),
        (
            "Avg Revenue",
            money(valid_revenue["revenue"].mean()),
            valid_revenue["revenue"].mean(),
            prev_revenue["revenue"].mean(),
            TEAL,
            by_year["revenue"].tolist(),
        ),
        (
            "Avg ROI",
            f"{valid_roi['roi'].median():.1f}x" if not valid_roi.empty else "0.0x",
            valid_roi["roi"].median() if not valid_roi.empty else 0,
            prev_roi["roi"].median() if not prev_roi.empty else 0,
            PURPLE,
            by_year["roi"].tolist(),
        ),
        (
            "Avg Rating",
            f"{valid_rating['avg_rating'].mean():.1f}" if not valid_rating.empty else "0.0",
            valid_rating["avg_rating"].mean() if not valid_rating.empty else 0,
            prev_rating["avg_rating"].mean() if not prev_rating.empty else 0,
            AMBER,
            by_year["rating"].tolist(),
        ),
        (
            "Total Budget",
            money(valid_budget["budget"].sum()),
            valid_budget["budget"].sum(),
            previous[previous["budget"] > 0]["budget"].sum(),
            "#94a3b8",
            by_year["budget"].tolist(),
        ),
        (
            "Total Revenue",
            money(valid_revenue["revenue"].sum()),
            valid_revenue["revenue"].sum(),
            prev_revenue["revenue"].sum(),
            GREEN,
            by_year["revenue"].tolist(),
        ),
    ]

    result = []
    for label, display, current, prev, accent, series in values:
        change, tone = metric_delta(current, prev)
        result.append(
            {
                "label": label,
                "display": display,
                "change": change,
                "tone": tone,
                "accent": accent,
                "series": series,
            }
        )
    return result


def best_worst_genre(filtered: pd.DataFrame) -> tuple[str, str]:
    genre_df = explode_genres(filtered.dropna(subset=["roi"]))
    if genre_df.empty:
        return "N/A", "N/A"
    grouped = genre_df.groupby("genre")["roi"].median().sort_values(ascending=False)
    return f"{grouped.index[0]} ({grouped.iloc[0]:.1f}x)", f"{grouped.index[-1]} ({grouped.iloc[-1]:.1f}x)"


def reset_filters(min_year: int, max_year: int, all_genres: list[str]) -> None:
    st.session_state["year_range"] = (min_year, max_year)
    st.session_state["genres"] = all_genres[:8]
    st.session_state["quick_range"] = "All"
    st.session_state["min_votes"] = 1000
    st.session_state["metric_choice"] = "ROI"
    st.session_state["top_n"] = 12


def keyed_widget_value(key: str, default):
    """Return kwargs that avoid Streamlit's default/session_state warning."""

    return {} if key in st.session_state else {"value": default}


def keyed_widget_default(key: str, default):
    return {} if key in st.session_state else {"default": default}


def keyed_select_index(key: str, options: list, default):
    return {} if key in st.session_state else {"index": options.index(default)}


def main() -> None:
    inject_css()
    render_sidebar()
    df = load_data()

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    all_genres = sorted(
        genre
        for genre in set("|".join(df["genres"].dropna()).split("|"))
        if genre and genre in CORE_GENRES
    )
    default_year_range = (min_year, max_year)
    default_genres = all_genres[:8]

    top_left, top_right = st.columns([1, 0.42])
    with top_left:
        st.markdown(
            """
            <div class="title">
              <h1>IMDB Movie Analytics Dashboard</h1>
              <p>Revenue, Genre, Release Timing and Rating Insights  •  Based on 4000+ movies dataset</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right:
        c1, c2 = st.columns([1, 0.55])
        with c1:
            active_year_range = st.session_state.get("year_range", default_year_range)
            st.markdown(
                f'<div class="pill">Calendar&nbsp; {active_year_range[0]} - {active_year_range[1]}</div>',
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Reset", width="stretch"):
                reset_filters(min_year, max_year, all_genres)
                st.rerun()

    filter_col, chart_col = st.columns([0.20, 0.80], gap="medium")

    with filter_col:
        st.markdown('<div class="panel"><div class="panel-title">Filters</div>', unsafe_allow_html=True)
        year_range = st.slider(
            "Year Range",
            min_year,
            max_year,
            key="year_range",
            **keyed_widget_value("year_range", default_year_range),
        )
        selected_genres = st.multiselect(
            "Genres (Included)",
            all_genres,
            key="genres",
            **keyed_widget_default("genres", default_genres),
        )
        quick = st.radio(
            "Quick Range",
            ["1Y", "3Y", "6Y", "10Y", "All"],
            horizontal=True,
            key="quick_range",
            **keyed_select_index("quick_range", ["1Y", "3Y", "6Y", "10Y", "All"], "All"),
        )
        if quick != "All":
            span = int(quick.replace("Y", ""))
            year_range = (max(min_year, max_year - span + 1), max_year)
        min_votes = st.number_input(
            "Min Votes",
            min_value=0,
            max_value=int(df["analysis_vote_count"].max()),
            step=100,
            key="min_votes",
            **keyed_widget_value("min_votes", 1000),
        )
        filtered_preview = apply_filters(df, year_range, selected_genres, min_votes)
        best, worst = best_worst_genre(filtered_preview)
        st.markdown(
            f"""
            <div class="small-stat"><span>Best Genre</span><strong class="good">{best}</strong></div>
            <div class="small-stat"><span>Worst Genre</span><strong class="bad">{worst}</strong></div>
            <div class="filter-note">All filters update KPI cards and charts together.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    filtered = apply_filters(df, year_range, selected_genres, min_votes)
    previous = previous_period(df, year_range, selected_genres, min_votes)
    kpis = compute_kpis(filtered, previous)

    with chart_col:
        st.markdown(
            '<div class="kpi-grid">'
            + "".join(
                kpi_card(
                    item["label"],
                    item["display"],
                    item["change"],
                    item["tone"],
                    item["accent"],
                    item["series"],
                )
                for item in kpis
            )
            + "</div>",
            unsafe_allow_html=True,
        )

        upper_left, upper_right = st.columns([0.56, 0.44], gap="medium")
        with upper_left:
            st.markdown('<div class="panel"><div class="panel-title">Box Office Success Analysis</div>', unsafe_allow_html=True)
            fig = scatter_with_trend(filtered, "budget", "revenue", BLUE, 300)
            corr_df = filtered[["budget", "revenue"]].dropna()
            corr_df = corr_df[(corr_df["budget"] > 0) & (corr_df["revenue"] > 0)]
            corr = corr_df["budget"].corr(corr_df["revenue"]) if len(corr_df) > 2 else np.nan
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            st.markdown(
                f'<div class="insight">Correlation: {corr:.2f} · Higher budgets generally show better box office success, but variance increases with budget size.</div></div>',
                unsafe_allow_html=True,
            )
        with upper_right:
            st.markdown('<div class="panel"><div class="panel-title">Genre Profitability (ROI)</div>', unsafe_allow_html=True)
            metric_col, top_col = st.columns(2)
            with metric_col:
                metric_choice = st.selectbox(
                    "Metric",
                    ["ROI", "Revenue"],
                    key="metric_choice",
                    **keyed_select_index("metric_choice", ["ROI", "Revenue"], "ROI"),
                )
            with top_col:
                top_n = st.selectbox(
                    "Top",
                    [8, 10, 12, 15],
                    key="top_n",
                    **keyed_select_index("top_n", [8, 10, 12, 15], 12),
                )
            st.plotly_chart(genre_roi_chart(filtered, metric_choice, int(top_n)), width="stretch", config={"displayModeBar": False})
            st.markdown('<div class="insight">Adventure, Action and high-performing genre groups can be compared after filtering.</div></div>', unsafe_allow_html=True)

        lower_left, lower_mid, lower_right = st.columns([0.31, 0.31, 0.38], gap="medium")
        with lower_left:
            st.markdown('<div class="panel"><div class="panel-title">Revenue by Release Month</div>', unsafe_allow_html=True)
            st.plotly_chart(revenue_month_chart(filtered), width="stretch", config={"displayModeBar": False})
            st.markdown('<div class="insight">Summer and winter holiday months often show visible revenue peaks.</div></div>', unsafe_allow_html=True)
        with lower_mid:
            st.markdown('<div class="panel"><div class="panel-title">Budget vs ROI</div>', unsafe_allow_html=True)
            roi_cap = filtered["roi"].dropna().quantile(0.98) if filtered["roi"].notna().any() else None
            roi_fig = scatter_with_trend(filtered, "budget", "roi", "#a3e635", 242, y_cap=roi_cap)
            roi_corr_df = filtered[["budget", "roi"]].dropna()
            roi_corr_df = roi_corr_df[(roi_corr_df["budget"] > 0) & (roi_corr_df["roi"] > 0)]
            if roi_cap is not None:
                roi_corr_df = roi_corr_df[roi_corr_df["roi"] <= roi_cap]
            roi_corr = roi_corr_df["budget"].corr(roi_corr_df["roi"]) if len(roi_corr_df) > 2 else np.nan
            st.plotly_chart(roi_fig, width="stretch", config={"displayModeBar": False})
            st.markdown(
                f'<div class="insight">Correlation: {roi_corr:.2f} · ROI outliers are capped visually at the 98th percentile.</div></div>',
                unsafe_allow_html=True,
            )
        with lower_right:
            st.markdown('<div class="panel"><div class="panel-title">Rating Distribution by Genre</div>', unsafe_allow_html=True)
            st.plotly_chart(rating_box_chart(filtered), width="stretch", config={"displayModeBar": False})
            st.markdown('<div class="insight">Ratings are aggregated from user ratings and converted to a 10-point scale.</div></div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="footer">
          <span>Source: TMDB SQL dataset, processed locally for Streamlit dashboard</span>
          <span>All values are aggregated and anonymized</span>
          <span>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
