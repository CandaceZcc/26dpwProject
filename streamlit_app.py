from __future__ import annotations

import streamlit as st

from app.charts import genre_roi_chart, rating_box_chart, revenue_month_chart, scatter_with_trend
from app.config import BLUE
from app.components import (
    render_bottom,
    render_chart_panel,
    render_export,
    render_footer,
    render_header,
    render_kpi_grid,
    render_sidebar,
    resolve_sidebar_state,
)
from app.data import apply_filters, available_genres, load_data
from app.metrics import compute_kpis
from app.styles import inject_css
from app.predict import render_regression_view
from app.chi_square import render_chi2_view
from app.insights import render_insights


st.set_page_config(
    page_title="IMDB Movie Analytics Dashboard",
    page_icon="IMDB",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_dashboard_view(view: str, filtered, df, metric_choice: str, top_n: int, corr: float, roi_corr: float, roi_cap) -> None:
    if view == "Export":
        render_export(filtered)
        return
    
    if view == "Chi-Square":
        render_chi2_view(filtered)
        return

    if view == "Insights":
        render_insights(filtered)
        return

    if view == "Regression":
        render_regression_view(filtered)
        return
    
    if view == "Revenue":
        left, right = st.columns([0.60, 0.40], gap="medium")
        with left:
            render_chart_panel(
                "Box Office Success Analysis",
                scatter_with_trend(filtered, "budget", "revenue", BLUE, 300),
                f"Correlation: {corr:.2f} · Higher budgets generally show better box office success.",
            )
        with right:
            render_chart_panel(
                "Revenue by Release Month",
                revenue_month_chart(filtered),
                "Summer and winter holiday months often show visible revenue peaks.",
            )
        render_chart_panel(
            "Budget vs ROI",
            scatter_with_trend(filtered, "budget", "roi", "#a3e635", 245, y_cap=roi_cap),
            f"Correlation: {roi_corr:.2f} · ROI outliers are capped visually at the 98th percentile.",
        )
        return

    if view == "Genres":
        left, right = st.columns([0.48, 0.52], gap="medium")
        with left:
            render_chart_panel(
                "Genre Profitability (ROI)",
                genre_roi_chart(filtered, metric_choice, top_n),
                "Genre groups can be compared by ROI or average revenue after filtering.",
            )
        with right:
            render_chart_panel(
                "Rating Distribution by Genre",
                rating_box_chart(filtered),
                "Ratings are aggregated from user ratings and converted to a 10-point scale.",
            )
        return

    if view == "Time":
        render_chart_panel(
            "Revenue by Release Month",
            revenue_month_chart(filtered),
            "Use Year Range and Quick Range to inspect release timing patterns.",
        )
        return

    upper_left, upper_right = st.columns([0.60, 0.40], gap="medium")
    with upper_left:
        render_chart_panel(
            "Box Office Success Analysis",
            scatter_with_trend(filtered, "budget", "revenue", BLUE, 300),
            f"Correlation: {corr:.2f} · Higher budgets generally show better box office success, but variance increases with budget size.",
        )
    with upper_right:
        render_chart_panel(
            "Genre Profitability (ROI)",
            genre_roi_chart(filtered, metric_choice, top_n),
            "Adventure, Action and high-performing genre groups can be compared after filtering.",
        )

    lower_left, lower_mid, lower_right = st.columns([1, 1, 1], gap="medium")
    with lower_left:
        render_chart_panel(
            "Revenue by Release Month",
            revenue_month_chart(filtered),
            "Summer and winter holiday months often show visible revenue peaks.",
        )
    with lower_mid:
        render_chart_panel(
            "Budget vs ROI",
            scatter_with_trend(filtered, "budget", "roi", "#a3e635", 245, y_cap=roi_cap),
            f"Correlation: {roi_corr:.2f} · ROI outliers are capped visually at the 98th percentile.",
        )
    with lower_right:
        render_chart_panel(
            "Rating Distribution by Genre",
            rating_box_chart(filtered),
            "Ratings are aggregated from user ratings and converted to a 10-point scale.",
        )


def main() -> None:
    inject_css()

    df = load_data()
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    all_genres = available_genres(df)

    sidebar_state = resolve_sidebar_state(df, min_year, max_year, all_genres)
    filtered = apply_filters(
        df,
        sidebar_state.year_range,
        sidebar_state.selected_genres,
        sidebar_state.min_votes,
    )
    corr_df = filtered[["budget", "revenue"]].dropna()
    corr_df = corr_df[(corr_df["budget"] > 0) & (corr_df["revenue"] > 0)]
    corr = corr_df["budget"].corr(corr_df["revenue"]) if len(corr_df) > 2 else 0

    roi_cap = filtered["roi"].dropna().quantile(0.98) if filtered["roi"].notna().any() else None
    roi_corr_df = filtered[["budget", "roi"]].dropna()
    roi_corr_df = roi_corr_df[(roi_corr_df["budget"] > 0) & (roi_corr_df["roi"] > 0)]
    if roi_cap is not None:
        roi_corr_df = roi_corr_df[roi_corr_df["roi"] <= roi_cap]
    roi_corr = roi_corr_df["budget"].corr(roi_corr_df["roi"]) if len(roi_corr_df) > 2 else 0

    render_header(sidebar_state.year_range, min_year, max_year)
    render_kpi_grid(compute_kpis(filtered))

    filter_col, dashboard_col = st.columns([0.19, 0.81], gap="medium")
    with filter_col:
        sidebar_state = render_sidebar(df, min_year, max_year, all_genres)
    with dashboard_col:
        render_dashboard_view(
            sidebar_state.view,
            filtered,
            df,
            sidebar_state.metric_choice,
            sidebar_state.top_n,
            corr,
            roi_corr,
            roi_cap,
        )
    render_bottom()
    render_footer()


if __name__ == "__main__":
    main()
