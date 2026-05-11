from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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

VIEW_OPTIONS = ["Overview", "Revenue", "Genres", "Time", "Chi-Square", "Insights", "Regression", "Export"]
DEFAULT_VIEW = "Overview"
DEFAULT_MIN_VOTES = 1000


@dataclass(frozen=True)
class SidebarState:
    view: str
    year_range: tuple[int, int]
    selected_genres: list[str]
    quick_range: str
    min_votes: int
    metric_choice: str
    top_n: int
