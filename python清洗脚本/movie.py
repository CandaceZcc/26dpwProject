import pandas as pd
import ast
import csv
import os

# ------------------ 设置文件夹 ------------------
data_folder = r"C:\xampp\mysql\data\cleaned_dataset"

# ------------------ 读取 movies_metadata_cleaned.csv ------------------
movies_file = os.path.join(data_folder, "movies_metadata_cleaned.csv")
movies_df = pd.read_csv(movies_file)

# ------------------ collection ------------------
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
collection_clean_csv = os.path.join(data_folder, "collection_clean.csv")
collection_df.to_csv(collection_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"collection_clean.csv generated: {len(collection_df)} records")

# ------------------ movie ------------------
def extract_collection_id(val):
    if pd.isna(val) or val == '' or val == 'None':
        return None
    try:
        js = ast.literal_eval(val)
        return js.get('id')
    except:
        return None

movies_df['collection_id'] = movies_df['belongs_to_collection'].apply(extract_collection_id)

# 清理换行符，防止 CSV 导入错误
text_cols = ['original_title', 'overview', 'poster_path', 'status', 'tagline']
for col in text_cols:
    movies_df[col] = movies_df[col].astype(str).str.replace('\n',' ').str.replace('\r',' ')

movie_columns = ['id', 'original_title', 'overview', 'release_date',
                 'poster_path', 'budget', 'revenue', 'adult', 'runtime',
                 'original_language', 'popularity', 'vote_count', 'status',
                 'tagline', 'collection_id']
movie_df = movies_df[movie_columns]
movie_df.drop_duplicates(subset='id', inplace=True)

# 保存初版 movie CSV
movie_clean_csv = os.path.join(data_folder, "movie_clean.csv")
movie_df.to_csv(movie_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"movie_clean.csv generated: {len(movie_df)} records")

# ------------------ movie 外键安全 CSV ------------------
valid_collection_ids = collection_df['collection_id'].dropna().unique()
movie_df_safe = movie_df[movie_df['collection_id'].isin(valid_collection_ids) | movie_df['collection_id'].isna()]

movie_safe_csv = os.path.join(data_folder, "movie_clean_fk_safe.csv")
movie_df_safe.to_csv(movie_safe_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"movie_clean_fk_safe.csv generated: {len(movie_df_safe)} records")

# ------------------ genres ------------------
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
genres_clean_csv = os.path.join(data_folder, "genres_clean.csv")
genres_df.to_csv(genres_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"genres_clean.csv generated: {len(genres_df)} records")

# ------------------ production_companies ------------------
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
company_clean_csv = os.path.join(data_folder, "production_companies_clean.csv")
company_df.to_csv(company_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"production_companies_clean.csv generated: {len(company_df)} records")

# ------------------ production_countries ------------------
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
country_clean_csv = os.path.join(data_folder, "production_countries_clean.csv")
country_df.to_csv(country_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"production_countries_clean.csv generated: {len(country_df)} records")

# ------------------ spoken_languages ------------------
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
language_clean_csv = os.path.join(data_folder, "spoken_languages_clean.csv")
language_df.to_csv(language_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"spoken_languages_clean.csv generated: {len(language_df)} records")

# ------------------ keywords ------------------
keywords_file = os.path.join(data_folder, "links_cleaned.csv")
keywords_df = pd.read_csv(keywords_file)
keywords_df.drop_duplicates(subset='kw_id', inplace=True)
keywords_df = keywords_df[keywords_df['kw_id'].notna()]
keywords_clean_csv = os.path.join(data_folder, "keywords_clean.csv")
keywords_df.to_csv(keywords_clean_csv, index=False, quoting=csv.QUOTE_ALL)
print(f"keywords_clean.csv generated: {len(keywords_df)} records")

print("All cleaned and foreign-key-safe CSV files generated successfully.")