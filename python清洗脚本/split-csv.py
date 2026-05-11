import pandas as pd
import ast
import os

# Folder where your CSV files are stored
data_folder = r"C:\xampp\mysql\data\cleaned_dataset"

# ---------------- movies_metadata_cleaned.csv ----------------
movies_file = os.path.join(data_folder, "movies_metadata_cleaned.csv")
movies_df = pd.read_csv(movies_file)

# ---------------- collection ----------------
collection_list = []
for val in movies_df['belongs_to_collection'].dropna():
    try:
        js = ast.literal_eval(val)
        if js:
            collection_list.append({
                'collection_id': js.get('id'),
                'collection_name': js.get('name'),
                'collection_poster_path': js.get('poster_path'),
                'backdrop_path': js.get('backdrop_path')
            })
    except:
        continue

collection_df = pd.DataFrame(collection_list)
collection_df.drop_duplicates(subset='collection_id', inplace=True)
collection_df = collection_df[collection_df['collection_id'].notna()]
collection_df.to_csv(os.path.join(data_folder, "collection_clean.csv"), index=False)

# ---------------- movie ----------------
def extract_collection_id(val):
    if pd.isna(val) or val == '' or val == 'None':
        return None
    try:
        js = ast.literal_eval(val)
        return js.get('id')
    except:
        return None

movies_df['collection_id'] = movies_df['belongs_to_collection'].apply(extract_collection_id)
movie_columns = ['id', 'original_title', 'overview', 'release_date',
                 'poster_path', 'budget', 'revenue', 'adult', 'runtime',
                 'original_language', 'popularity', 'vote_count', 'status',
                 'tagline', 'collection_id']
movie_df = movies_df[movie_columns]
movie_df.drop_duplicates(subset='id', inplace=True)
movie_df.to_csv(os.path.join(data_folder, "movie_clean.csv"), index=False)

# ---------------- genres ----------------
genres_list = []
for val in movies_df['genres'].dropna():
    try:
        js_list = ast.literal_eval(val)
        for g in js_list:
            genres_list.append({
                'genre_id': g.get('id'),
                'genre_name': g.get('name')
            })
    except:
        continue

genres_df = pd.DataFrame(genres_list)
genres_df.drop_duplicates(subset='genre_id', inplace=True)
genres_df = genres_df[genres_df['genre_id'].notna()]
genres_df.to_csv(os.path.join(data_folder, "genres_clean.csv"), index=False)

# ---------------- production_companies ----------------
company_list = []
for val in movies_df['production_companies'].dropna():
    try:
        js_list = ast.literal_eval(val)
        for c in js_list:
            company_list.append({
                'company_id': c.get('id'),
                'company_name': c.get('name')
            })
    except:
        continue

company_df = pd.DataFrame(company_list)
company_df.drop_duplicates(subset='company_id', inplace=True)
company_df = company_df[company_df['company_id'].notna()]
company_df.to_csv(os.path.join(data_folder, "production_companies_clean.csv"), index=False)

# ---------------- production_countries ----------------
country_list = []
for val in movies_df['production_countries'].dropna():
    try:
        js_list = ast.literal_eval(val)
        for c in js_list:
            country_list.append({
                'country_code': c.get('iso_3166_1'),
                'country_name': c.get('name')
            })
    except:
        continue

country_df = pd.DataFrame(country_list)
country_df.drop_duplicates(subset='country_code', inplace=True)
country_df = country_df[country_df['country_code'].notna()]
country_df.to_csv(os.path.join(data_folder, "production_countries_clean.csv"), index=False)

# ---------------- spoken_languages ----------------
language_list = []
for val in movies_df['spoken_languages'].dropna():
    try:
        js_list = ast.literal_eval(val)
        for l in js_list:
            language_list.append({
                'language_code': l.get('iso_639_1'),
                'language_name': l.get('name')
            })
    except:
        continue

language_df = pd.DataFrame(language_list)
language_df.drop_duplicates(subset='language_code', inplace=True)
language_df = language_df[language_df['language_code'].notna()]
language_df.to_csv(os.path.join(data_folder, "spoken_languages_clean.csv"), index=False)

# ---------------- keywords ----------------
keywords_file = os.path.join(data_folder, "links_cleaned.csv")
keywords_df = pd.read_csv(keywords_file)
keywords_df.drop_duplicates(subset='kw_id', inplace=True)
keywords_df = keywords_df[keywords_df['kw_id'].notna()]
keywords_df.to_csv(os.path.join(data_folder, "keywords_clean.csv"), index=False)

print("All clean CSV files have been generated successfully.")