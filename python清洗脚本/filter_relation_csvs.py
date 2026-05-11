import os
import pandas as pd
import csv

BASE = r"C:\Users\sdfgh\OneDrive\Desktop\DPW\cleaned_dataset\generated_tmdb_imports"

def read_csv(name):
    return pd.read_csv(os.path.join(BASE, name), low_memory=False)

def write_csv(df, name):
    df.to_csv(os.path.join(BASE, name), index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
    print(f"filtered: {name} -> {len(df)} rows")

# -------------------------
# parent ids
# -------------------------
movie_ids = set(pd.to_numeric(read_csv("movie.csv")["tmdbid"], errors="coerce").dropna().astype("int64"))
collection_ids = set(pd.to_numeric(read_csv("collection.csv")["collection_id"], errors="coerce").dropna().astype("int64"))
genre_ids = set(pd.to_numeric(read_csv("genres.csv")["genres_id"], errors="coerce").dropna().astype("int64"))
keyword_ids = set(pd.to_numeric(read_csv("keywords.csv")["keyword_id"], errors="coerce").dropna().astype("int64"))
company_ids = set(pd.to_numeric(read_csv("production_companies.csv")["company_id"], errors="coerce").dropna().astype("int64"))
country_ids = set(read_csv("production_countries.csv")["iso_3166_1"].dropna().astype(str))
language_ids = set(read_csv("spoken_languages.csv")["iso_639_1"].dropna().astype(str))
person_ids = set(pd.to_numeric(read_csv("person.csv")["person_id"], errors="coerce").dropna().astype("int64"))
cast_ids = set(pd.to_numeric(read_csv("cast.csv")["cast_id"], errors="coerce").dropna().astype("int64"))
credit_df = read_csv("credit.csv")
credit_ids = set()
if "credit_id" in credit_df.columns:
    credit_ids = set(pd.to_numeric(credit_df["credit_id"], errors="coerce").dropna().astype("int64"))
user_ids = set(pd.to_numeric(read_csv("user.csv")["user_id"], errors="coerce").dropna().astype("int64"))

# -------------------------
# belong_to
# -------------------------
df = read_csv("belong_to.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["collection_id"] = pd.to_numeric(df["collection_id"], errors="coerce")
df = df[df["tmdbid"].isin(movie_ids) & df["collection_id"].isin(collection_ids)].drop_duplicates()
write_csv(df, "belong_to.csv")

# -------------------------
# link_genres
# -------------------------
df = read_csv("link_genres.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["genres_id"] = pd.to_numeric(df["genres_id"], errors="coerce")
df = df[df["tmdbid"].isin(movie_ids) & df["genres_id"].isin(genre_ids)].drop_duplicates()
write_csv(df, "link_genres.csv")

# -------------------------
# have
# -------------------------
df = read_csv("have.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["keyword_id"] = pd.to_numeric(df["keyword_id"], errors="coerce")
df = df[df["tmdbid"].isin(movie_ids) & df["keyword_id"].isin(keyword_ids)].drop_duplicates()
write_csv(df, "have.csv")

# -------------------------
# produced_by
# -------------------------
df = read_csv("produced_by.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["company_id"] = pd.to_numeric(df["company_id"], errors="coerce")
df = df[df["tmdbid"].isin(movie_ids) & df["company_id"].isin(company_ids)].drop_duplicates()
write_csv(df, "produced_by.csv")

# -------------------------
# produced_in
# -------------------------
df = read_csv("produced_in.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["iso_3166_1"] = df["iso_3166_1"].astype(str)
df = df[df["tmdbid"].isin(movie_ids) & df["iso_3166_1"].isin(country_ids)].drop_duplicates()
write_csv(df, "produced_in.csv")

# -------------------------
# speak
# -------------------------
df = read_csv("speak.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["iso_639_1"] = df["iso_639_1"].astype(str)
df = df[df["tmdbid"].isin(movie_ids) & df["iso_639_1"].isin(language_ids)].drop_duplicates()
write_csv(df, "speak.csv")

# -------------------------
# made_by
# -------------------------
df = read_csv("made_by.csv")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df["person_id"] = pd.to_numeric(df["person_id"], errors="coerce")
df = df[df["tmdbid"].isin(movie_ids) & df["person_id"].isin(person_ids)].drop_duplicates()
write_csv(df, "made_by.csv")

# -------------------------
# rate
# -------------------------
df = read_csv("rate.csv")
df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
df["tmdbid"] = pd.to_numeric(df["tmdbid"], errors="coerce")
df = df[df["user_id"].isin(user_ids) & df["tmdbid"].isin(movie_ids)].drop_duplicates()
write_csv(df, "rate.csv")

# -------------------------
# isa_cast
# -------------------------
df = read_csv("isa_cast.csv")
df["person_id"] = pd.to_numeric(df["person_id"], errors="coerce")
df["cast_id"] = pd.to_numeric(df["cast_id"], errors="coerce")
df = df[df["person_id"].isin(person_ids) & df["cast_id"].isin(cast_ids)].drop_duplicates()
write_csv(df, "isa_cast.csv")

# -------------------------
# isa_credit
# -------------------------
df = read_csv("isa_credit.csv")
if len(df) > 0 and "person_id" in df.columns and "credit_id" in df.columns:
    df["person_id"] = pd.to_numeric(df["person_id"], errors="coerce")
    df["credit_id"] = pd.to_numeric(df["credit_id"], errors="coerce")
    df = df[df["person_id"].isin(person_ids) & df["credit_id"].isin(credit_ids)].drop_duplicates()
write_csv(df, "isa_credit.csv")

print("All relation CSVs filtered successfully.")