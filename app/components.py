from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from app.config import DEFAULT_MIN_VOTES, DEFAULT_VIEW, SidebarState, VIEW_OPTIONS
from app.data import apply_filters
from app.metrics import best_worst_genre


def reset_filters(min_year: int, max_year: int, all_genres: list[str]) -> None:
    st.session_state["view_mode"] = st.session_state.get("view_mode", DEFAULT_VIEW)
    st.session_state["year_range"] = (min_year, max_year)
    st.session_state["genres"] = all_genres[:8]
    st.session_state["quick_range"] = "All"
    st.session_state["min_votes"] = DEFAULT_MIN_VOTES
    st.session_state["metric_choice"] = "ROI"
    st.session_state["top_n"] = 12


def keyed_widget_value(key: str, default):
    return {} if key in st.session_state else {"value": default}


def keyed_widget_default(key: str, default):
    return {} if key in st.session_state else {"default": default}


def keyed_select_index(key: str, options: list, default):
    return {} if key in st.session_state else {"index": options.index(default)}


def render_sidebar(df: pd.DataFrame, min_year: int, max_year: int, all_genres: list[str]) -> SidebarState:
    default_year_range = (min_year, max_year)
    default_genres = all_genres[:8]

    with st.sidebar:
        st.title("IMDB")
        view = st.radio(
            "View",
            VIEW_OPTIONS,
            key="view_mode",
            **keyed_select_index("view_mode", VIEW_OPTIONS, DEFAULT_VIEW),
        )

        st.divider()
        st.subheader("Filters")
        year_range = st.slider(
            "Year Range",
            min_year,
            max_year,
            key="year_range",
            **keyed_widget_value("year_range", default_year_range),
        )
        selected_genres = st.multiselect(
            "Genres",
            all_genres,
            key="genres",
            **keyed_widget_default("genres", default_genres),
        )
        quick_range = st.radio(
            "Quick Range",
            ["1Y", "3Y", "6Y", "10Y", "All"],
            horizontal=True,
            key="quick_range",
            **keyed_select_index("quick_range", ["1Y", "3Y", "6Y", "10Y", "All"], "All"),
        )
        if quick_range != "All":
            span = int(quick_range.replace("Y", ""))
            year_range = (max(min_year, max_year - span + 1), max_year)
        min_votes = st.number_input(
            "Min Votes",
            min_value=0,
            max_value=int(df["analysis_vote_count"].max()),
            step=100,
            key="min_votes",
            **keyed_widget_value("min_votes", DEFAULT_MIN_VOTES),
        )

        preview = apply_filters(df, year_range, selected_genres, min_votes)
        best, worst = best_worst_genre(preview)
        st.markdown(
            f"""
            <div class="small-stat"><span>Best Genre</span><strong class="good">{best}</strong></div>
            <div class="small-stat"><span>Worst Genre</span><strong class="bad">{worst}</strong></div>
            <div class="filter-note">All filters update KPI cards and charts together.</div>
            """,
            unsafe_allow_html=True,
        )

        metric_choice = st.selectbox(
            "Genre Metric",
            ["ROI", "Revenue"],
            key="metric_choice",
            **keyed_select_index("metric_choice", ["ROI", "Revenue"], "ROI"),
        )
        top_n = st.selectbox(
            "Top Genres",
            [8, 10, 12, 15],
            key="top_n",
            **keyed_select_index("top_n", [8, 10, 12, 15], 12),
        )

        st.button(
            "Reset Filters",
            on_click=reset_filters,
            args=(min_year, max_year, all_genres),
            width="stretch",
        )

    return SidebarState(
        view=view,
        year_range=year_range,
        selected_genres=selected_genres,
        quick_range=quick_range,
        min_votes=int(min_votes),
        metric_choice=metric_choice,
        top_n=int(top_n),
    )


def render_header(year_range: tuple[int, int]) -> None:
    left, right = st.columns([1, 0.28])
    with left:
        st.markdown(
            """
            <div class="title">
              <h1>IMDB Movie Analytics Dashboard</h1>
              <p>Revenue, Genre, Release Timing and Rating Insights • Based on 4000+ movies dataset</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f'<div class="pill">Calendar&nbsp; {year_range[0]} - {year_range[1]}</div>',
            unsafe_allow_html=True,
        )


def sparkline_svg(values: list[float], color: str) -> str:
    clean = [float(v) for v in values if pd.notna(v)]
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


def render_kpi_grid(kpis: list[dict]) -> None:
    st.html(
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
        + "</div>"
    )


def render_chart_panel(title: str, fig, insight: str) -> None:
    with st.container(border=True):
        st.markdown(f'<div class="panel-title">{title}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown(f'<div class="insight">{insight}</div>', unsafe_allow_html=True)


def current_filtered_csv(filtered: pd.DataFrame) -> bytes:
    return filtered.to_csv(index=False).encode("utf-8-sig")


def render_export(filtered: pd.DataFrame) -> None:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Export Current Selection</div>', unsafe_allow_html=True)
        st.write(f"当前筛选结果：{len(filtered):,} movies")
        st.download_button(
            "Download CSV",
            data=current_filtered_csv(filtered),
            file_name="filtered_movies.csv",
            mime="text/csv",
            width="stretch",
        )
        st.dataframe(
            filtered[
                [
                    "title",
                    "year",
                    "budget",
                    "revenue",
                    "roi",
                    "avg_rating",
                    "analysis_vote_count",
                    "genres",
                ]
            ].head(80),
            width="stretch",
            height=420,
        )


def render_footer() -> None:
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
