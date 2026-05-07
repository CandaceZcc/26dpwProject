from __future__ import annotations

import pandas as pd

from app.config import AMBER, BLUE, GREEN, PURPLE, TEAL
from app.data import explode_genres


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


def compute_kpis(filtered: pd.DataFrame) -> list[dict]:
    valid_revenue = filtered[filtered["revenue"] > 0]
    valid_budget = filtered[filtered["budget"] > 0]
    valid_roi = filtered.dropna(subset=["roi"])
    valid_rating = filtered.dropna(subset=["avg_rating"])

    by_year = filtered.groupby("year", as_index=False).agg(
        movies=("movie_id", "count"),
        revenue=("revenue", lambda values: values[values > 0].mean()),
        roi=("roi", "median"),
        rating=("avg_rating", "mean"),
        budget=("budget", lambda values: values[values > 0].sum()),
    )

    # Meaningful per-KPI subtitles
    profitable_pct = (
        (valid_roi["roi"] > 1).sum() / len(valid_roi) * 100
        if not valid_roi.empty else 0
    )
    avg_budget_per_film = (
        valid_budget["budget"].mean() if not valid_budget.empty else 0
    )
    avg_rev_per_film = (
        valid_revenue["revenue"].mean() if not valid_revenue.empty else 0
    )
    high_rating_pct = (
        (valid_rating["avg_rating"] >= 7).sum() / len(valid_rating) * 100
        if not valid_rating.empty else 0
    )
    roi_gt2_pct = (
        (valid_roi["roi"] >= 2).sum() / len(valid_roi) * 100
        if not valid_roi.empty else 0
    )
    rev_median = valid_revenue["revenue"].median() if not valid_revenue.empty else 0

    kpi_meta = [
        {
            "label": "Total Movies",
            "display": compact_number(len(filtered)),
            "change": f"{profitable_pct:.1f}% profitable",
            "tone": "pos" if profitable_pct >= 50 else "neg",
            "accent": BLUE,
            "series": by_year["movies"].tolist(),
        },
        {
            "label": "Avg Revenue",
            "display": money(avg_rev_per_film),
            "change": f"median {money(rev_median)}",
            "tone": "neu",
            "accent": TEAL,
            "series": by_year["revenue"].tolist(),
        },
        {
            "label": "Avg ROI",
            "display": f"{valid_roi['roi'].median():.1f}x" if not valid_roi.empty else "0.0x",
            "change": f"{roi_gt2_pct:.1f}% exceed 2x",
            "tone": "pos" if roi_gt2_pct >= 30 else "neu",
            "accent": PURPLE,
            "series": by_year["roi"].tolist(),
        },
        {
            "label": "Avg Rating",
            "display": f"{valid_rating['avg_rating'].mean():.1f}" if not valid_rating.empty else "0.0",
            "change": f"{high_rating_pct:.1f}% rated 7+",
            "tone": "pos" if high_rating_pct >= 30 else "neu",
            "accent": AMBER,
            "series": by_year["rating"].tolist(),
        },
        {
            "label": "Total Budget",
            "display": money(valid_budget["budget"].sum()),
            "change": f"avg {money(avg_budget_per_film)} / film",
            "tone": "neu",
            "accent": "#94a3b8",
            "series": by_year["budget"].tolist(),
        },
        {
            "label": "Total Revenue",
            "display": money(valid_revenue["revenue"].sum()),
            "change": f"avg {money(avg_rev_per_film)} / film",
            "tone": "pos" if avg_rev_per_film > avg_budget_per_film else "neg",
            "accent": GREEN,
            "series": by_year["revenue"].tolist(),
        },
    ]
    return kpi_meta


def best_worst_genre(filtered: pd.DataFrame) -> tuple[str, str]:
    genre_df = explode_genres(filtered.dropna(subset=["roi"]))
    if genre_df.empty:
        return "N/A", "N/A"
    grouped = genre_df.groupby("genre")["roi"].median().sort_values(ascending=False)
    return f"{grouped.index[0]} ({grouped.iloc[0]:.1f}x)", f"{grouped.index[-1]} ({grouped.iloc[-1]:.1f}x)"
