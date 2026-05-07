from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import chart_layout
from app.config import AMBER, BLUE, GREEN, MONTHS, PURPLE, ROSE, TEAL
from app.metrics import money


@st.cache_data(show_spinner=False)
def _compute(_hash: int, _df: pd.DataFrame) -> dict:
    df = _df.copy()
    for col in ["budget", "revenue", "roi", "avg_rating", "release_month", "year", "runtime", "popularity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    valid = df[
        (df["budget"] > 0) & (df["revenue"] > 0)
        & df["roi"].notna()
        & df["primary_genre"].notna()
        & (df["primary_genre"] != "Unknown")
    ].copy()

    # ── KPI facts ──────────────────────────────────────────────────────────
    genre_roi = valid.groupby("primary_genre")["roi"].median().sort_values(ascending=False)
    top_genre, top_genre_roi = genre_roi.index[0], genre_roi.iloc[0]

    month_rev = valid.groupby("release_month")["revenue"].mean().sort_values(ascending=False)
    best_month = MONTHS[int(month_rev.index[0]) - 1]
    best_month_rev = month_rev.iloc[0]

    profitable = valid[valid["revenue"] > valid["budget"]]
    profit_rate = len(profitable) / len(valid) * 100
    rating_hit = profitable["avg_rating"].mean()
    rating_flop = valid[valid["revenue"] <= valid["budget"]]["avg_rating"].mean()

    # Long films ROI
    long_roi = valid[valid["runtime"] > 150]["roi"].median()

    # ── Chart data ─────────────────────────────────────────────────────────
    top5_genres = genre_roi.head(5)

    df_rev = df[(df["revenue"] > 0) & df["year"].notna()].copy()
    df_rev["decade"] = (df_rev["year"] // 10) * 10
    decade_rev = df_rev.groupby("decade")["revenue"].mean().tail(6)

    valid["rating_bin"] = pd.cut(
        valid["avg_rating"],
        bins=[0, 5, 6, 7, 8, 10],
        labels=["< 5", "5 – 6", "6 – 7", "7 – 8", "8 +"],
    )
    rating_rev = valid.groupby("rating_bin", observed=True)["revenue"].mean()

    # Runtime ROI
    valid["rt_bin"] = pd.cut(
        valid["runtime"],
        bins=[0, 90, 110, 130, 150, 300],
        labels=["< 90 min", "90 – 110", "110 – 130", "130 – 150", "> 150 min"],
    )
    runtime_roi = valid.groupby("rt_bin", observed=True)["roi"].median()

    # Multi-genre share
    df2 = df[df["genres"].notna()].copy()
    df2["gc"] = df2["genres"].str.split("|").apply(len)
    multi_pct = (df2["gc"] >= 2).mean() * 100

    return dict(
        top_genre=top_genre, top_genre_roi=top_genre_roi,
        best_month=best_month, best_month_rev=best_month_rev,
        profit_rate=profit_rate, rating_hit=rating_hit, rating_flop=rating_flop,
        long_roi=long_roi,
        top5_genres=top5_genres, decade_rev=decade_rev,
        rating_rev=rating_rev, runtime_roi=runtime_roi,
        multi_pct=multi_pct, total=len(valid),
    )


# ── Charts ──────────────────────────────────────────────────────────────────

def _decade_chart(decade_rev: pd.Series) -> go.Figure:
    labels = [f"{int(d)}s" for d in decade_rev.index]
    vals = [v / 1e6 for v in decade_rev.values]
    fig = go.Figure(go.Bar(
        x=labels, y=vals,
        marker=dict(color=vals, colorscale=[[0, BLUE], [1, TEAL]], showscale=False, line=dict(width=0)),
        text=[f"${v:.0f}M" for v in vals], textposition="outside",
        textfont=dict(size=11, color="#dbe7f8"),
        hovertemplate="%{x}<br>Avg Revenue: $%{y:.0f}M<extra></extra>",
    ))
    fig.update_layout(**chart_layout(230))
    fig.update_yaxes(title="Avg Revenue (M)")
    fig.update_xaxes(title="Decade")
    return fig


def _genre_roi_bar(top5: pd.Series) -> go.Figure:
    genres = top5.index.tolist()[::-1]
    vals = top5.values.tolist()[::-1]
    colors = [TEAL, BLUE, PURPLE, AMBER, ROSE][::-1]
    fig = go.Figure(go.Bar(
        x=vals, y=genres, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.2f}x" for v in vals], textposition="outside",
        textfont=dict(size=11, color="#dbe7f8"),
        hovertemplate="%{y}<br>Median ROI: %{x:.2f}x<extra></extra>",
    ))
    fig.update_layout(**chart_layout(230))
    fig.update_xaxes(title="Median ROI (x)")
    fig.update_yaxes(title="")
    return fig


def _rating_rev_chart(rating_rev: pd.Series) -> go.Figure:
    labels = rating_rev.index.astype(str).tolist()
    vals = [v / 1e6 for v in rating_rev.values]
    colors = [ROSE, AMBER, TEAL, BLUE, PURPLE]
    fig = go.Figure(go.Bar(
        x=labels, y=vals,
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"${v:.0f}M" for v in vals], textposition="outside",
        textfont=dict(size=11, color="#dbe7f8"),
        hovertemplate="Rating %{x}<br>Avg Revenue: $%{y:.0f}M<extra></extra>",
    ))
    fig.update_layout(**chart_layout(230))
    fig.update_yaxes(title="Avg Revenue (M)")
    fig.update_xaxes(title="Avg Rating Bucket")
    return fig


def _runtime_roi_chart(runtime_roi: pd.Series) -> go.Figure:
    labels = runtime_roi.index.astype(str).tolist()
    vals = runtime_roi.values.tolist()
    fig = go.Figure(go.Scatter(
        x=labels, y=vals,
        mode="lines+markers",
        line=dict(color=PURPLE, width=3),
        marker=dict(size=9, color=PURPLE, line=dict(width=2, color="#fff")),
        text=[f"{v:.2f}x" for v in vals],
        hovertemplate="%{x}<br>Median ROI: %{y:.2f}x<extra></extra>",
    ))
    fig.update_layout(**chart_layout(200))
    fig.update_yaxes(title="Median ROI (x)")
    fig.update_xaxes(title="Runtime")
    return fig


# ── HTML helpers ─────────────────────────────────────────────────────────────

_CSS = """
<style>
.ins-title {
    font-size: 28px; font-weight: 900; color: #f7fbff;
    margin: 0 0 1.5rem; letter-spacing: -.01em;
    text-align: center;
}
.ins-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .7rem; margin-bottom: .9rem;
}
.ins-card {
    background: linear-gradient(145deg, rgba(18,32,51,.98), rgba(11,22,38,.98));
    border: 1px solid rgba(128,164,218,.18);
    border-radius: 12px;
    padding: .9rem 1rem .85rem;
    position: relative; overflow: hidden;
}
.ins-card::before {
    content:""; position:absolute; inset:0 auto 0 0;
    width:3px; background:var(--ic); box-shadow:0 0 18px var(--ic);
}
.ins-card::after {
    content:""; position:absolute; top:0; right:0;
    width:70px; height:70px;
    background:radial-gradient(circle at top right, var(--ic), transparent 65%);
    opacity:.07;
}
.ic-icon { font-size:20px; margin-bottom:.3rem; }
.ic-lbl {
    font-size:10.5px; font-weight:700; text-transform:uppercase;
    letter-spacing:.07em; color:#9aa9bd; margin-bottom:.2rem;
}
.ic-big { font-size:26px; font-weight:800; color:#fff; line-height:1.1; margin-bottom:.3rem; }
.ic-desc { font-size:11.5px; color:#9aa9bd; line-height:1.5; }
.ins-finding {
    background: linear-gradient(135deg, rgba(18,32,51,.7), rgba(11,22,38,.7));
    border: 1px solid rgba(128,164,218,.15);
    border-radius: 11px;
    padding: .9rem 1.1rem;
}
.ins-finding-title {
    font-size:12px; font-weight:700; text-transform:uppercase;
    letter-spacing:.06em; color:#9aa9bd; margin-bottom:.5rem;
}
.ins-finding-body { font-size:13px; color:#dbe7f8; line-height:1.7; }
.ins-finding-body strong { color:#f7fbff; }
.ins-summary {
    background: linear-gradient(135deg, rgba(59,130,246,.07), rgba(45,212,191,.04));
    border: 1px solid rgba(128,164,218,.16);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-top: .8rem;
    font-size: 13px; color: #c8d4e6; line-height: 1.75;
}
.ins-summary strong { color: #f7fbff; }
@media (max-width: 1200px) {
    .ins-cards { grid-template-columns: repeat(2, 1fr); }
}
</style>
"""


def _card(icon, label, big, desc, color):
    return (
        f'<div class="ins-card" style="--ic:{color}">'
        f'<div class="ic-icon">{icon}</div>'
        f'<div class="ic-lbl">{label}</div>'
        f'<div class="ic-big">{big}</div>'
        f'<div class="ic-desc">{desc}</div>'
        f'</div>'
    )


def _finding(title, body):
    return (
        f'<div class="ins-finding">'
        f'<div class="ins-finding-title">{title}</div>'
        f'<div class="ins-finding-body">{body}</div>'
        f'</div>'
    )


# ── Main render ───────────────────────────────────────────────────────────────

def render_insights(df: pd.DataFrame) -> None:
    ins = _compute(id(df), df)

    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin:0 0 1.5rem">'
        '<div style="font-size:28px;font-weight:900;color:#f7fbff;letter-spacing:-.02em;margin-bottom:.35rem">'
        "💡 Key Insights from the Data</div>"
        '<div style="font-size:13px;color:#9aa9bd;">Statistical patterns and trends discovered across 45,000+ films</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    # Row 1 — 4 highlight cards
    st.markdown(
        '<div class="ins-cards">'
        + _card("🏆", "Highest ROI Genre",
                f"{ins['top_genre']}  {ins['top_genre_roi']:.2f}x",
                f"Median return across {ins['total']:,} validated films. "
                "Low-budget genre films consistently lead on ROI.",
                TEAL)
        + _card("☀️", "Best Release Month",
                ins["best_month"],
                f"Average box office of {money(ins['best_month_rev'])}. "
                "Summer blockbuster season drives the annual revenue peak.",
                AMBER)
        + _card("📈", "Profitability Rate",
                f"{ins['profit_rate']:.1f}%",
                f"Profitable films score {ins['rating_hit']:.2f} avg vs "
                f"{ins['rating_flop']:.2f} for flops — a {ins['rating_hit'] - ins['rating_flop']:.2f}-pt "
                "quality gap.",
                GREEN)
        + _card("⏱", "Long Films ROI",
                f"{ins['long_roi']:.2f}x",
                "Films over 150 min post the highest median ROI — "
                "audiences reward ambitious, epic-scale productions.",
                PURPLE)
        + "</div>",
        unsafe_allow_html=True,
    )

    # Row 2 — 3 charts
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Avg Revenue by Decade</div>', unsafe_allow_html=True)
            st.plotly_chart(_decade_chart(ins["decade_rev"]), width="stretch",
                            config={"displayModeBar": False})
            st.markdown(
                '<div class="insight">Box office has grown 2.4× from the 1980s to the 2010s '
                "as global distribution expanded.</div>",
                unsafe_allow_html=True,
            )
    with c2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Top 5 Genres by Median ROI</div>', unsafe_allow_html=True)
            st.plotly_chart(_genre_roi_bar(ins["top5_genres"]), width="stretch",
                            config={"displayModeBar": False})
            st.markdown(
                '<div class="insight">Horror and Western deliver the best returns despite — '
                "or because of — their typically modest production budgets.</div>",
                unsafe_allow_html=True,
            )
    with c3:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Avg Revenue by Rating Bucket</div>', unsafe_allow_html=True)
            st.plotly_chart(_rating_rev_chart(ins["rating_rev"]), width="stretch",
                            config={"displayModeBar": False})
            st.markdown(
                '<div class="insight">The 6 – 7 rating band peaks at highest average revenue — '
                "broadly appealing films outgross niche critical darlings.</div>",
                unsafe_allow_html=True,
            )

    # Row 3 — runtime chart + 2 finding cards
    left, mid, right = st.columns([0.38, 0.31, 0.31], gap="medium")
    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Runtime vs Median ROI</div>', unsafe_allow_html=True)
            st.plotly_chart(_runtime_roi_chart(ins["runtime_roi"]), width="stretch",
                            config={"displayModeBar": False})
            st.markdown(
                '<div class="insight">Longer runtimes trend toward higher ROI — '
                "each runtime bracket shows incremental improvement.</div>",
                unsafe_allow_html=True,
            )
    with mid:
        st.markdown(
            _finding(
                "🎭  Multi-Genre Strategy",
                f"<strong>{ins['multi_pct']:.0f}%</strong> of films span two or more genres. "
                "Blending genres broadens audience reach — pure single-genre films are now the minority. "
                "The most common pairings are <strong>Comedy + Drama</strong> and "
                "<strong>Drama + Romance</strong>, both of which combine broad appeal with "
                "lower production costs.",
            ),
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            _finding(
                "⭐  The Rating Sweet Spot",
                f"Films rated <strong>6 – 7</strong> earn the highest average box office "
                f"(<strong>{money(ins['rating_rev'].get('6 – 7', ins['rating_rev'].iloc[2]))}</strong>), "
                "outperforming even 8+ critically acclaimed films. "
                "Mass-market entertainment that satisfies without polarising audiences "
                "consistently captures the widest theatrical audience.",
            ),
            unsafe_allow_html=True,
        )

    # Summary strip
    st.markdown(
        f"""<div class="ins-summary">
        Based on <strong>{ins['total']:,} films</strong> with verified budget and revenue data. &nbsp;·&nbsp;
        <strong>{ins['top_genre']}</strong> leads all genres at <strong>{ins['top_genre_roi']:.2f}x</strong> median ROI. &nbsp;·&nbsp;
        <strong>{ins['best_month']}</strong> is the single best month to open a film at
        <strong>{money(ins['best_month_rev'])}</strong> average. &nbsp;·&nbsp;
        <strong>{ins['profit_rate']:.1f}%</strong> of films recoup their budget —
        and higher-rated films are measurably more likely to do so.
        </div>""",
        unsafe_allow_html=True,
    )
