from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "26dpwProject_final_submission.zip"
LIMIT = 100 * 1024 * 1024

FILES = [
    "README.md",
    "requirements.txt",
    "run_windows.bat",
    "run_unix.sh",
    "streamlit_app.py",
    "PREDICT_MODULE.md",
    "DPW_PPT_metric_check.md",
    "Speaker3_Changelog.md",
    "演讲分工明细.md",
    "Final_Report.docx",
    "DPW_PPT_Final.pptx",
    "ERmodel.pdf",
    "ER关系.pdf",
    "GUI.png",
    "movie_dashboard.html",
    "data/processed_movies.csv",
    "data/dataset_summary.json",
]

DIRS = [
    "app",
    "python清洗脚本",
]

SCRIPT_FILES = [
    "scripts/build_dataset.py",
    "scripts/finalize_submission_assets.py",
    "scripts/finalize_report.py",
    "scripts/repair_report_toc.py",
    "scripts/package_submission.py",
]

EXCLUDE_PARTS = {"__pycache__"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return True


def add_file(zf: zipfile.ZipFile, path: Path):
    rel = path.relative_to(ROOT).as_posix()
    zf.write(path, rel)


def main() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in FILES:
            path = ROOT / rel
            if path.exists():
                add_file(zf, path)
            else:
                raise FileNotFoundError(rel)

        for dirname in DIRS:
            for path in sorted((ROOT / dirname).rglob("*")):
                if path.is_file() and should_include(path):
                    add_file(zf, path)

        for rel in SCRIPT_FILES:
            path = ROOT / rel
            if path.exists():
                add_file(zf, path)

    size = ZIP_PATH.stat().st_size
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        blocked = [
            n for n in names
            if n.startswith((".git/", ".venv/", ".vs/", "tmdb.sql/"))
            or "ppt_debug" in n
            or "ppt_rendered" in n
            or n.endswith(".before_final_cleanup.pptx")
            or n.endswith(".before_final_cleanup.docx")
        ]
    if blocked:
        raise SystemExit("Blocked files entered archive:\n" + "\n".join(blocked[:50]))
    if size > LIMIT:
        raise SystemExit(f"Archive exceeds 100MB: {size / 1024 / 1024:.2f} MB")
    print(f"Created {ZIP_PATH.name}: {size / 1024 / 1024:.2f} MB, {len(names)} files")


if __name__ == "__main__":
    main()
