from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.config import BLUE, CORE_GENRES, MONTHS, MUTED, PURPLE, TEAL
from app.data import explode_genres
from app.metrics import money


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
    fig.update_xaxes(title="Genres", tickangle=-40)
    fig.update_yaxes(title=y_title)
    return fig


def revenue_month_chart(df: pd.DataFrame) -> go.Figure:
    valid = df[(df["revenue"] > 0) & df["release_month"].notna()]
    if valid.empty:
        return empty_chart("当前筛选条件下没有月份收入数据", 245)
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
    fig.update_layout(**chart_layout(245))
    fig.update_yaxes(title="Revenue (USD)")
    fig.update_xaxes(title="Month")
    return fig


def rating_box_chart(df: pd.DataFrame) -> go.Figure:
    genre_df = explode_genres(df.dropna(subset=["avg_rating"]))
    genre_df = genre_df[genre_df["genre"].isin(CORE_GENRES)]
    if genre_df.empty:
        return empty_chart("当前筛选条件下没有评分分布数据", 245)
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
        color_discrete_sequence=[BLUE, PURPLE, TEAL, "#fbbf24", "#fb7185"],
        points="outliers",
    )
    fig.update_layout(**chart_layout(245), showlegend=False)
    fig.update_yaxes(title="Rating", range=[0, 10])
    fig.update_xaxes(title="Genre", tickangle=-40)
    return fig
