import pandas as pd
import os

# 当前目录
folder = os.path.dirname(os.path.abspath(__file__))

ratings_path = os.path.join(folder, "ratings.csv")
links_path = os.path.join(folder, "links.csv")

print("开始读取数据...")

# ==============================
# 分块读取（防止文件太大）
# ==============================
chunksize = 100000
chunks = []

# 先读 links（只读一次）
links = pd.read_csv(links_path)[["movieId", "tmdbId"]]

for chunk in pd.read_csv(ratings_path, chunksize=chunksize):

    # ==============================
    # movieId → tmdbId
    # ==============================
    chunk = chunk.merge(links, on="movieId", how="left")

    # 删除没有 tmdbId 的
    chunk = chunk.dropna(subset=["tmdbId"])

    # 类型处理
    chunk["tmdbId"] = chunk["tmdbId"].astype(int)
    chunk["userId"] = chunk["userId"].astype(int)
    chunk["rating"] = chunk["rating"].astype(float)
    chunk["timestamp"] = chunk["timestamp"].astype(int)

    # 去重
    chunk = chunk.drop_duplicates()

    # 评分过滤（和你之前一致）
    chunk = chunk[
        (chunk["rating"] >= 0.5) &
        (chunk["rating"] <= 5.0) &
        ((chunk["rating"] * 2) % 1 == 0)
    ]

    # 删除旧列 movieId
    chunk = chunk.drop(columns=["movieId"])

    # 调整列顺序（tmdbId 第二列）
    chunk = chunk[["userId", "tmdbId", "rating", "timestamp"]]

    chunks.append(chunk)

# ==============================
# 合并
# ==============================
df = pd.concat(chunks, ignore_index=True)

# 排序（保证一致）
df = df.sort_values(["userId", "tmdbId"]).reset_index(drop=True)

# ==============================
# 保存
# ==============================
output_path = os.path.join(folder, "ratings_cleaned_tmdb.csv")
df.to_csv(output_path, index=False)

print("✅ 完成！文件已生成：ratings_cleaned_tmdb.csv")
print("最终行数:", len(df))