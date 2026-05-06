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
        ("Total Movies", compact_number(len(filtered)), len(filtered), len(previous), BLUE, by_year["movies"].tolist()),
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
