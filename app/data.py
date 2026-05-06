from __future__ import annotations

import subprocess
import sys

import pandas as pd
import streamlit as st

from app.config import CORE_GENRES, DATA_FILE, ROOT


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


def available_genres(df: pd.DataFrame) -> list[str]:
    return sorted(
        genre
        for genre in set("|".join(df["genres"].dropna()).split("|"))
        if genre and genre in CORE_GENRES
    )


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    genre_df = df.copy()
    genre_df["genre"] = genre_df["genres"].str.split("|")
    genre_df = genre_df.explode("genre")
    genre_df["genre"] = genre_df["genre"].replace("", pd.NA)
    return genre_df.dropna(subset=["genre"])


def apply_filters(
    df: pd.DataFrame,
    year_range: tuple[int, int],
    selected_genres: list[str],
    min_votes: int,
) -> pd.DataFrame:
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


def previous_period(
    df: pd.DataFrame,
    year_range: tuple[int, int],
    selected_genres: list[str],
    min_votes: int,
) -> pd.DataFrame:
    span = year_range[1] - year_range[0] + 1
    prev_range = (year_range[0] - span, year_range[0] - 1)
    return apply_filters(df, prev_range, selected_genres, min_votes)
