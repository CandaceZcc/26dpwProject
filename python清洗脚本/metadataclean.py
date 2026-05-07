import pandas as pd
import json
import os

# ==============================
# 文件路径
# ==============================
folder = os.path.dirname(os.path.abspath(__file__))

movies_path = os.path.join(folder, "movies_metadata.csv")

# 输出文件
movies_out = os.path.join(folder, "movies.csv")
genres_out = os.path.join(folder, "genres.csv")
movie_genres_out = os.path.join(folder, "movie_genres.csv")

print("开始处理 movies_metadata...")

# ==============================
# 读取数据
# ==============================
df = pd.read_csv(movies_path, low_memory=False)

# ==============================
# 清洗基础字段
# ==============================

# 删除无效 id
df = df[df["id"].notna()]
df = df[df["id"].astype(str).str.isnumeric()]

df["id"] = df["id"].astype(int)

# 去重
df = df.drop_duplicates(subset=["id"])

# ==============================
# 🎬 movies 主表
# ==============================
movies = df[[
    "id",
    "title",
    "original_title",
    "overview",
    "popularity",
    "release_date",
    "runtime",
    "revenue",
    "vote_count",
    "poster_path",
    "homepage",
    "original_language",
    "status",
    "tagline",
    "adult",
    "video"
]].copy()

# 重命名
movies = movies.rename(columns={"id": "tmdbId"})

# 类型处理
movies["tmdbId"] = movies["tmdbId"].astype(int)

# 排序
movies = movies.sort_values("tmdbId").reset_index(drop=True)

# 保存
movies.to_csv(movies_out, index=False)

print("✅ movies.csv 已生成")


# ==============================
# JSON解析函数
# ==============================
def parse_json(text):
    if pd.isna(text) or text in ["", "[]"]:
        return []
    try:
        return json.loads(text.replace("'", '"'))
    except:
        return []


# ==============================
# 🎯 拆 genres
# ==============================
rows = []

for _, row in df.iterrows():
    tmdb_id = row["id"]
    genres = parse_json(row["genres"])

    for g in genres:
        rows.append({
            "tmdbId": tmdb_id,
            "genre_id": g.get("id"),
            "genre_name": g.get("name")
        })

genre_df = pd.DataFrame(rows)

# 清洗
genre_df = genre_df.dropna(subset=["genre_id"])
genre_df = genre_df.drop_duplicates()

genre_df["tmdbId"] = genre_df["tmdbId"].astype(int)
genre_df["genre_id"] = genre_df["genre_id"].astype(int)

# ==============================
# 🎬 genres 表（字典）
# ==============================
genres = genre_df[["genre_id", "genre_name"]].drop_duplicates()
genres = genres.sort_values("genre_id").reset_index(drop=True)

genres.to_csv(genres_out, index=False)

print("✅ genres.csv 已生成")

# ==============================
# 🎬 movie_genres（关系表）
# ==============================
movie_genres = genre_df[["tmdbId", "genre_id"]]
movie_genres = movie_genres.sort_values(["tmdbId", "genre_id"]).reset_index(drop=True)

movie_genres.to_csv(movie_genres_out, index=False)

print("✅ movie_genres.csv 已生成")

print("🎉 所有处理完成！")