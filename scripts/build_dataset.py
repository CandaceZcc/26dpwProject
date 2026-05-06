"""Build the analysis-ready movie dataset from the exported TMDB SQL files.

The Streamlit dashboard should be easy for every group member to run, so this
script avoids requiring a local MySQL/MariaDB server. It parses the core SQL
INSERT statements directly and writes a compact CSV used by the app.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "tmdb.sql"
DATA_DIR = ROOT / "data"
OUTPUT_CSV = DATA_DIR / "processed_movies.csv"
SUMMARY_JSON = DATA_DIR / "dataset_summary.json"


def split_sql_tuples(values_sql: str) -> Iterable[list[str]]:
    """Yield tuple fields from a MySQL VALUES block."""

    in_quote = False
    escape = False
    depth = 0
    tuple_text: list[str] = []

    for char in values_sql:
        if escape:
            if depth:
                tuple_text.append("\\" + char)
            escape = False
            continue

        if char == "\\" and in_quote:
            escape = True
            continue

        if char == "'":
            in_quote = not in_quote
            if depth:
                tuple_text.append(char)
            continue

        if not in_quote and char == "(":
            if depth == 0:
                tuple_text = []
            else:
                tuple_text.append(char)
            depth += 1
            continue

        if not in_quote and char == ")":
            depth -= 1
            if depth == 0:
                yield split_fields("".join(tuple_text))
                tuple_text = []
            else:
                tuple_text.append(char)
            continue

        if depth:
            tuple_text.append(char)


def split_fields(tuple_sql: str) -> list[str]:
    fields: list[str] = []
    current: list[str] = []
    in_quote = False
    escape = False

    for char in tuple_sql:
        if escape:
            current.append("\\" + char)
            escape = False
            continue

        if char == "\\" and in_quote:
            escape = True
            continue

        if char == "'":
            in_quote = not in_quote
            current.append(char)
            continue

        if char == "," and not in_quote:
            fields.append("".join(current).strip())
            current = []
            continue

        current.append(char)

    fields.append("".join(current).strip())
    return fields


def decode_value(token: str):
    token = token.strip()
    if token.upper() == "NULL":
        return None

    if len(token) >= 2 and token[0] == "'" and token[-1] == "'":
        value = token[1:-1]
        output: list[str] = []
        index = 0
        while index < len(value):
            char = value[index]
            if char == "\\" and index + 1 < len(value):
                output.append(value[index + 1])
                index += 2
            else:
                output.append(char)
                index += 1
        return html.unescape("".join(output))

    if "." in token:
        try:
            return float(token)
        except ValueError:
            return token

    try:
        return int(token)
    except ValueError:
        return token


def iter_insert_rows(sql_file: Path, table_name: str) -> Iterable[list]:
    prefix = f"INSERT INTO `{table_name}`"
    collecting = False
    statement: list[str] = []

    with sql_file.open("r", encoding="utf-8") as file:
        for line in file:
            if not collecting and line.startswith(prefix):
                collecting = True
                statement = [line]
                if line.rstrip().endswith(";"):
                    collecting = False
                    yield from rows_from_statement("".join(statement))
                continue

            if collecting:
                statement.append(line)
                if line.rstrip().endswith(";"):
                    collecting = False
                    yield from rows_from_statement("".join(statement))


def rows_from_statement(statement: str) -> Iterable[list]:
    values_index = statement.index("VALUES") + len("VALUES")
    values_sql = statement[values_index:].strip().rstrip(";")
    for fields in split_sql_tuples(values_sql):
        yield [decode_value(field) for field in fields]


def safe_int(value, default=0) -> int:
    if value in (None, ""):
        return default
    return int(value)


def safe_float(value, default=0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def build_dataset(sql_dir: Path = SQL_DIR, output_csv: Path = OUTPUT_CSV) -> dict:
    movies = {}
    for row in iter_insert_rows(sql_dir / "tmdb_table_movie.sql", "movie"):
        release_date = row[9]
        year = None
        month = None
        if release_date:
            try:
                parsed_date = datetime.strptime(str(release_date), "%Y-%m-%d")
                year = parsed_date.year
                month = parsed_date.month
            except ValueError:
                pass

        movies[safe_int(row[0])] = {
            "movie_id": safe_int(row[0]),
            "title": row[5] or "Untitled",
            "language": row[4] or "",
            "budget": safe_int(row[2]),
            "revenue": safe_int(row[10]),
            "release_date": release_date or "",
            "year": year,
            "release_month": month,
            "runtime": safe_int(row[11]),
            "popularity": safe_float(row[7]),
            "tmdb_vote_count": safe_int(row[15]),
        }

    genres = {
        safe_int(row[0]): row[1]
        for row in iter_insert_rows(sql_dir / "tmdb_table_genres.sql", "genres")
        if row[1]
    }

    movie_genres: dict[int, set[str]] = defaultdict(set)
    for tmdbid, genre_id in iter_insert_rows(
        sql_dir / "tmdb_table_link_genres.sql", "link_genres"
    ):
        genre_name = genres.get(safe_int(genre_id))
        if genre_name:
            movie_genres[safe_int(tmdbid)].add(genre_name)

    rating_sum: dict[int, float] = defaultdict(float)
    rating_count: dict[int, int] = defaultdict(int)
    for _, tmdbid, rating, _ in iter_insert_rows(sql_dir / "tmdb_table_rate.sql", "rate"):
        movie_id = safe_int(tmdbid)
        rating_sum[movie_id] += safe_float(rating)
        rating_count[movie_id] += 1

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    skipped_no_year = 0
    for movie_id, movie in movies.items():
        if movie["year"] is None or movie["release_month"] is None:
            skipped_no_year += 1
            continue

        budget = movie["budget"]
        revenue = movie["revenue"]
        roi = revenue / budget if budget > 0 and revenue > 0 else ""
        avg_rating = (
            (rating_sum[movie_id] / rating_count[movie_id]) * 2
            if rating_count[movie_id]
            else ""
        )
        genres_joined = "|".join(sorted(movie_genres.get(movie_id, [])))
        primary_genre = genres_joined.split("|")[0] if genres_joined else "Unknown"

        rows.append(
            {
                **movie,
                "genres": genres_joined,
                "primary_genre": primary_genre,
                "avg_rating": round(avg_rating, 2) if avg_rating != "" else "",
                "rating_count": rating_count[movie_id],
                "analysis_vote_count": max(movie["tmdb_vote_count"], rating_count[movie_id]),
                "roi": round(roi, 4) if roi != "" else "",
            }
        )

    fieldnames = [
        "movie_id",
        "title",
        "language",
        "budget",
        "revenue",
        "release_date",
        "year",
        "release_month",
        "runtime",
        "popularity",
        "tmdb_vote_count",
        "rating_count",
        "analysis_vote_count",
        "avg_rating",
        "roi",
        "genres",
        "primary_genre",
    ]
    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    valid_roi = sum(1 for row in rows if row["roi"] != "")
    valid_ratings = sum(1 for row in rows if row["avg_rating"] != "")
    summary = {
        "source": "tmdb.sql",
        "movies_loaded": len(movies),
        "movies_written": len(rows),
        "movies_skipped_no_year": skipped_no_year,
        "movies_with_roi": valid_roi,
        "movies_with_rating": valid_ratings,
        "rating_note": "rate.rating is stored on a 0.5-5 scale and converted to 0-10.",
        "generated_file": str(output_csv.relative_to(ROOT)),
    }
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql-dir", type=Path, default=SQL_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    args = parser.parse_args()
    summary = build_dataset(args.sql_dir, args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
