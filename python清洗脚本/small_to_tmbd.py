import pandas as pd
import os

# ==============================
# 读取文件
# ==============================
folder = os.path.dirname(os.path.abspath(__file__))

ratings = pd.read_csv(os.path.join(folder, "ratings_small.csv"))
links = pd.read_csv(os.path.join(folder, "links_small.csv"))

print("原始行数:", len(ratings))

# ==============================
# 🎯 movieId → tmdbId
# ==============================
ratings = ratings.merge(
    links[["movieId", "tmdbId"]],
    on="movieId",
    how="left"
)

# ==============================
# 清洗
# ==============================

# 1. 删除没有 tmdbId 的
ratings = ratings.dropna(subset=["tmdbId"])

# 2. 类型转换
ratings["tmdbId"] = ratings["tmdbId"].astype(int)
ratings["userId"] = ratings["userId"].astype(int)
ratings["rating"] = ratings["rating"].astype(float)
ratings["timestamp"] = ratings["timestamp"].astype(int)

# 3. 去重
ratings = ratings.drop_duplicates()

# 4. 评分过滤（和你之前R一致）
ratings = ratings[
    (ratings["rating"] >= 0.5) &
    (ratings["rating"] <= 5.0) &
    ((ratings["rating"] * 2) % 1 == 0)
]

# 5. 删除旧列 movieId
ratings = ratings.drop(columns=["movieId"])

# ==============================
# 🎯 调整列顺序（tmdbId 第二列）
# ==============================
ratings = ratings[
    ["userId", "tmdbId", "rating", "timestamp"]
]

# ==============================
# 排序（保证一致）
# ==============================
ratings = ratings.sort_values(
    ["userId", "tmdbId"]
).reset_index(drop=True)

# ==============================
# 保存
# ==============================
output_path = os.path.join(folder, "ratings_small_cleaned_tmdb.csv")
ratings.to_csv(output_path, index=False)

print("✅ 完成！已生成 ratings_small_cleaned_tmdb.csv")
print("清洗后行数:", len(ratings))