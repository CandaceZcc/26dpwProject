import pandas as pd
import json
import os

# ==============================
# 文件路径
# ==============================
folder = os.path.dirname(os.path.abspath(__file__))

keywords_path = os.path.join(folder, "keywords.csv")
output_long = os.path.join(folder, "keywords_long_format.csv")
output_wide = os.path.join(folder, "keywords_wide_format.csv")

print("开始处理 keywords...")

# ==============================
# 读取数据
# ==============================
df = pd.read_csv(keywords_path)


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
# 🎯 long 格式（关系表）
# ==============================
rows = []

for _, row in df.iterrows():
    tmdb_id = row["id"]
    keywords = parse_json(row["keywords"])

    for k in keywords:
        rows.append({
            "tmdbId": tmdb_id,
            "kw_id": k.get("id"),  # ✅ 改这里
            "kw_name": k.get("name")  # ✅ 改这里
        })

long_df = pd.DataFrame(rows)

# ==============================
# 清洗
# ==============================
long_df = long_df.dropna(subset=["kw_id"])
long_df = long_df.drop_duplicates()

long_df["tmdbId"] = long_df["tmdbId"].astype(int)
long_df["kw_id"] = long_df["kw_id"].astype(int)

# 排序
long_df = long_df.sort_values(
    ["tmdbId", "kw_id"]
).reset_index(drop=True)

# 保存
long_df.to_csv(output_long, index=False)

print("✅ 已生成 keywords_long_format.csv")

# ==============================
# 🎯 wide 格式（关键词表）
# ==============================
wide_df = long_df[["kw_id", "kw_name"]].drop_duplicates()

wide_df = wide_df.sort_values("kw_id").reset_index(drop=True)

wide_df.to_csv(output_wide, index=False)

print("✅ 已生成 keywords_wide_format.csv")

print("处理完成！")