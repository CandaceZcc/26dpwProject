import os
import ast
import csv
import pandas as pd


# =========================================================
# 1. CONFIG
# =========================================================

BASE_DIR = r"C:\Users\sdfgh\OneDrive\Desktop\DPW\cleaned_dataset"
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_tmdb_imports")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# 2. HELPERS
# =========================================================

def find_input_file(base_name: str) -> str:
    """
    Find a file by base name, even if Windows hides the extension.
    Tries csv, xlsx, xls.
    """
    candidates = [
        f"{base_name}.csv",
        f"{base_name}.xlsx",
        f"{base_name}.xls",
        base_name
    ]
    for name in candidates:
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"Cannot find file for base name: {base_name}")


def read_table(base_name: str) -> pd.DataFrame:
    path = find_input_file(base_name)
    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path, low_memory=False)
    elif lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")


def safe_literal_eval(value):
    if pd.isna(value):
        return None
    if isinstance(value, (list, dict)):
        return value
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    try:
        return ast.literal_eval(text)
    except Exception:
        return None


def clean_text(value):
    if pd.isna(value):
        return None
    text = str(value)
    text = text.replace("\n", " ").replace("\r", " ").strip()
    return text if text != "" else None


def write_csv(df: pd.DataFrame, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
    print(f"Generated: {path} | rows = {len(df)}")


def to_bool_int(value):
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return int(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return 1
    if text in {"false", "0", "no"}:
        return 0
    return None


def gender_to_int(value):
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text == "female":
        return 1
    if text == "male":
        return 2
    try:
        return int(float(text))
    except Exception:
        return 0


def parse_date_column(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    return dt.dt.strftime("%Y-%m-%d")


# =========================================================
# 3. LOAD SOURCE FILES
# =========================================================

movies_df = read_table("movies_metadata_cleaned")
cast_df = read_table("cast_cleaned")
links_df = read_table("links_cleaned")
keywords_long_df = read_table("keywords_long_format")
ratings_tmdb_df = read_table("ratings_cleaned_simple_tmdb")

# Standardize column names where needed
movies_df.columns = [str(c).strip() for c in movies_df.columns]
cast_df.columns = [str(c).strip() for c in cast_df.columns]
links_df.columns = [str(c).strip() for c in links_df.columns]
keywords_long_df.columns = [str(c).strip() for c in keywords_long_df.columns]
ratings_tmdb_df.columns = [str(c).strip() for c in ratings_tmdb_df.columns]


# =========================================================
# 4. ENTITY TABLES
# =========================================================

# -------------------------
# movie
# -------------------------
movie_out = pd.DataFrame({
    "tmdbid": pd.to_numeric(movies_df["id"], errors="coerce"),
    "adult": movies_df["adult"].apply(to_bool_int),
    "budget": pd.to_numeric(movies_df["budget"], errors="coerce"),
    "homepage": movies_df["homepage"].apply(clean_text),
    "original_language": movies_df["original_language"].apply(clean_text),
    "original_title": movies_df["original_title"].apply(clean_text),
    "overview": movies_df["overview"].apply(clean_text),
    "popularity": pd.to_numeric(movies_df["popularity"], errors="coerce"),
    "poster_path": movies_df["poster_path"].apply(clean_text),
    "release_date": parse_date_column(movies_df["release_date"]),
    "revenue": pd.to_numeric(movies_df["revenue"], errors="coerce"),
    "runtime": pd.to_numeric(movies_df["runtime"], errors="coerce"),
    "status": movies_df["status"].apply(clean_text),
    "tagline": movies_df["tagline"].apply(clean_text),
    "video": movies_df["video"].apply(to_bool_int),
    "vote_count": pd.to_numeric(movies_df["vote_count"], errors="coerce")
})
movie_out = movie_out.dropna(subset=["tmdbid"]).drop_duplicates(subset=["tmdbid"])
write_csv(movie_out, "movie.csv")


# -------------------------
# collection
# -------------------------
collection_rows = []
belong_to_rows = []

for _, row in movies_df.iterrows():
    tmdbid = pd.to_numeric(row.get("id"), errors="coerce")
    parsed = safe_literal_eval(row.get("belongs_to_collection"))
    if isinstance(parsed, dict) and parsed:
        collection_id = parsed.get("id")
        collection_rows.append({
            "collection_id": collection_id,
            "collection_name": clean_text(parsed.get("name")),
            "collection_poster_path": clean_text(parsed.get("poster_path")),
            "backdrop_path": clean_text(parsed.get("backdrop_path"))
        })
        if pd.notna(tmdbid) and pd.notna(collection_id):
            belong_to_rows.append({
                "tmdbid": int(tmdbid),
                "collection_id": int(collection_id)
            })

collection_out = pd.DataFrame(collection_rows).dropna(subset=["collection_id"]).drop_duplicates(subset=["collection_id"])
belong_to_out = pd.DataFrame(belong_to_rows).drop_duplicates()
write_csv(collection_out, "collection.csv")
write_csv(belong_to_out, "belong_to.csv")


# -------------------------
# genres + link_genres
# -------------------------
genre_rows = []
link_genres_rows = []

for _, row in movies_df.iterrows():
    tmdbid = pd.to_numeric(row.get("id"), errors="coerce")
    parsed = safe_literal_eval(row.get("genres"))
    if isinstance(parsed, list):
        for item in parsed:
            gid = item.get("id")
            gname = clean_text(item.get("name"))
            genre_rows.append({
                "genres_id": gid,
                "genres_name": gname
            })
            if pd.notna(tmdbid) and pd.notna(gid):
                link_genres_rows.append({
                    "tmdbid": int(tmdbid),
                    "genres_id": int(gid)
                })

genres_out = pd.DataFrame(genre_rows).dropna(subset=["genres_id"]).drop_duplicates(subset=["genres_id"])
link_genres_out = pd.DataFrame(link_genres_rows).drop_duplicates()
write_csv(genres_out, "genres.csv")
write_csv(link_genres_out, "link_genres.csv")


# -------------------------
# keywords + have
# -------------------------
keywords_long_df = keywords_long_df.rename(columns={
    "id": "tmdbid",
    "kw_id": "keyword_id",
    "kw_name": "keyword_name"
})

keywords_out = keywords_long_df[["keyword_id", "keyword_name"]].copy()
keywords_out["keyword_name"] = keywords_out["keyword_name"].apply(clean_text)
keywords_out["keyword_id"] = pd.to_numeric(keywords_out["keyword_id"], errors="coerce")
keywords_out = keywords_out.dropna(subset=["keyword_id"]).drop_duplicates(subset=["keyword_id"])

have_out = keywords_long_df[["tmdbid", "keyword_id"]].copy()
have_out["tmdbid"] = pd.to_numeric(have_out["tmdbid"], errors="coerce")
have_out["keyword_id"] = pd.to_numeric(have_out["keyword_id"], errors="coerce")
have_out = have_out.dropna(subset=["tmdbid", "keyword_id"]).drop_duplicates()

write_csv(keywords_out, "keywords.csv")
write_csv(have_out, "have.csv")


# -------------------------
# production_companies + produced_by
# -------------------------
company_rows = []
produced_by_rows = []

for _, row in movies_df.iterrows():
    tmdbid = pd.to_numeric(row.get("id"), errors="coerce")
    parsed = safe_literal_eval(row.get("production_companies"))
    if isinstance(parsed, list):
        for item in parsed:
            cid = item.get("id")
            cname = clean_text(item.get("name"))
            company_rows.append({
                "company_id": cid,
                "company_name": cname
            })
            if pd.notna(tmdbid) and pd.notna(cid):
                produced_by_rows.append({
                    "tmdbid": int(tmdbid),
                    "company_id": int(cid)
                })

companies_out = pd.DataFrame(company_rows).dropna(subset=["company_id"]).drop_duplicates(subset=["company_id"])
produced_by_out = pd.DataFrame(produced_by_rows).drop_duplicates()
write_csv(companies_out, "production_companies.csv")
write_csv(produced_by_out, "produced_by.csv")


# -------------------------
# production_countries + produced_in
# -------------------------
country_rows = []
produced_in_rows = []

for _, row in movies_df.iterrows():
    tmdbid = pd.to_numeric(row.get("id"), errors="coerce")
    parsed = safe_literal_eval(row.get("production_countries"))
    if isinstance(parsed, list):
        for item in parsed:
            code = clean_text(item.get("iso_3166_1"))
            cname = clean_text(item.get("name"))
            country_rows.append({
                "iso_3166_1": code,
                "country_name": cname
            })
            if pd.notna(tmdbid) and code:
                produced_in_rows.append({
                    "tmdbid": int(tmdbid),
                    "iso_3166_1": code
                })

countries_out = pd.DataFrame(country_rows).dropna(subset=["iso_3166_1"]).drop_duplicates(subset=["iso_3166_1"])
produced_in_out = pd.DataFrame(produced_in_rows).drop_duplicates()
write_csv(countries_out, "production_countries.csv")
write_csv(produced_in_out, "produced_in.csv")


# -------------------------
# spoken_languages + speak
# -------------------------
language_rows = []
speak_rows = []

for _, row in movies_df.iterrows():
    tmdbid = pd.to_numeric(row.get("id"), errors="coerce")
    parsed = safe_literal_eval(row.get("spoken_languages"))
    if isinstance(parsed, list):
        for item in parsed:
            code = clean_text(item.get("iso_639_1"))
            lname = clean_text(item.get("name"))
            language_rows.append({
                "iso_639_1": code,
                "lang_name": lname
            })
            if pd.notna(tmdbid) and code:
                speak_rows.append({
                    "tmdbid": int(tmdbid),
                    "iso_639_1": code
                })

languages_out = pd.DataFrame(language_rows).dropna(subset=["iso_639_1"]).drop_duplicates(subset=["iso_639_1"])
speak_out = pd.DataFrame(speak_rows).drop_duplicates()
write_csv(languages_out, "spoken_languages.csv")
write_csv(speak_out, "speak.csv")


# -------------------------
# person
# -------------------------
person_out = cast_df[["id", "name", "gender", "profile_path"]].copy()
person_out = person_out.rename(columns={
    "id": "person_id"
})
person_out["person_id"] = pd.to_numeric(person_out["person_id"], errors="coerce")
person_out["name"] = person_out["name"].apply(clean_text)
person_out["gender"] = person_out["gender"].apply(gender_to_int)
person_out["profile_path"] = person_out["profile_path"].apply(clean_text)
person_out = person_out.dropna(subset=["person_id"]).drop_duplicates(subset=["person_id"])
write_csv(person_out, "person.csv")


# -------------------------
# cast
# -------------------------
cast_out = cast_df[["cast_id", "character", "order"]].copy()
cast_out = cast_out.rename(columns={
    "character": "character_name"
})
cast_out["cast_id"] = pd.to_numeric(cast_out["cast_id"], errors="coerce")
cast_out["character_name"] = cast_out["character_name"].apply(clean_text)
cast_out["order"] = pd.to_numeric(cast_out["order"], errors="coerce")
cast_out = cast_out.dropna(subset=["cast_id"]).drop_duplicates(subset=["cast_id"])
write_csv(cast_out, "cast.csv")


# -------------------------
# credit (empty: no source columns for department/job)
# -------------------------
credit_out = pd.DataFrame(columns=["credit_id", "department", "job"])
write_csv(credit_out, "credit.csv")


# -------------------------
# user
# -------------------------
user_out = ratings_tmdb_df[["userId"]].copy().rename(columns={"userId": "user_id"})
user_out["user_id"] = pd.to_numeric(user_out["user_id"], errors="coerce")
user_out = user_out.dropna(subset=["user_id"]).drop_duplicates(subset=["user_id"])
write_csv(user_out, "user.csv")


# =========================================================
# 5. RELATION TABLES
# =========================================================

# -------------------------
# made_by (movie-person)
# -------------------------
made_by_out = cast_df[["movie_id", "id"]].copy().rename(columns={
    "movie_id": "tmdbid",
    "id": "person_id"
})
made_by_out["tmdbid"] = pd.to_numeric(made_by_out["tmdbid"], errors="coerce")
made_by_out["person_id"] = pd.to_numeric(made_by_out["person_id"], errors="coerce")
made_by_out = made_by_out.dropna(subset=["tmdbid", "person_id"]).drop_duplicates()
write_csv(made_by_out, "made_by.csv")


# -------------------------
# rate (user-movie-rating)
# -------------------------
rate_out = ratings_tmdb_df[["userId", "tmdbId", "rating", "timestamp"]].copy().rename(columns={
    "userId": "user_id",
    "tmdbId": "tmdbid"
})
rate_out["user_id"] = pd.to_numeric(rate_out["user_id"], errors="coerce")
rate_out["tmdbid"] = pd.to_numeric(rate_out["tmdbid"], errors="coerce")
rate_out["rating"] = pd.to_numeric(rate_out["rating"], errors="coerce")
rate_out["timestamp"] = pd.to_numeric(rate_out["timestamp"], errors="coerce")
rate_out = rate_out.dropna(subset=["user_id", "tmdbid"]).drop_duplicates(subset=["user_id", "tmdbid"])
write_csv(rate_out, "rate.csv")


# -------------------------
# isa_cast
# -------------------------
isa_cast_out = cast_df[["id", "cast_id"]].copy().rename(columns={
    "id": "person_id"
})
isa_cast_out["person_id"] = pd.to_numeric(isa_cast_out["person_id"], errors="coerce")
isa_cast_out["cast_id"] = pd.to_numeric(isa_cast_out["cast_id"], errors="coerce")
isa_cast_out = isa_cast_out.dropna(subset=["person_id", "cast_id"]).drop_duplicates()
write_csv(isa_cast_out, "isa_cast.csv")


# -------------------------
# isa_credit (empty: no crew/credit source)
# -------------------------
isa_credit_out = pd.DataFrame(columns=["person_id", "credit_id"])
write_csv(isa_credit_out, "isa_credit.csv")


# =========================================================
# 6. OPTIONAL QA SUMMARY
# =========================================================

summary_rows = [
    ("movie", len(movie_out)),
    ("collection", len(collection_out)),
    ("genres", len(genres_out)),
    ("keywords", len(keywords_out)),
    ("production_companies", len(companies_out)),
    ("production_countries", len(countries_out)),
    ("spoken_languages", len(languages_out)),
    ("person", len(person_out)),
    ("cast", len(cast_out)),
    ("credit", len(credit_out)),
    ("user", len(user_out)),
    ("belong_to", len(belong_to_out)),
    ("link_genres", len(link_genres_out)),
    ("have", len(have_out)),
    ("produced_by", len(produced_by_out)),
    ("produced_in", len(produced_in_out)),
    ("speak", len(speak_out)),
    ("made_by", len(made_by_out)),
    ("rate", len(rate_out)),
    ("isa_cast", len(isa_cast_out)),
    ("isa_credit", len(isa_credit_out)),
]

summary_df = pd.DataFrame(summary_rows, columns=["table_name", "row_count"])
write_csv(summary_df, "import_summary.csv")

print("\nAll import CSV files have been generated.")
print(f"Output folder: {OUTPUT_DIR}")