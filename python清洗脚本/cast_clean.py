import pandas as pd
import json

# 读取数据
credits = pd.read_csv("credits.csv")


# 解析 JSON 的函数
def parse_json(text):
    if pd.isna(text) or text in ["", "[]"]:
        return []
    try:
        return json.loads(text.replace("'", '"'))
    except:
        return []


# ==============================
# 提取 cast
# ==============================
cast_rows = []

for _, row in credits.iterrows():
    movie_id = row["id"]
    cast_list = parse_json(row["cast"])

    for c in cast_list:
        cast_rows.append({
            "movie_id": movie_id,
            "actor_id": c.get("id"),
            "name": c.get("name"),
            "gender": c.get("gender"),
            "order": c.get("order")
        })

# 转成 DataFrame
cast_df = pd.DataFrame(cast_rows)

# ==============================
# 清洗
# ==============================

# 1. 删除无效 actor_id
cast_df = cast_df.dropna(subset=["actor_id"])

# 2. 去重（同电影同演员）
cast_df = cast_df.drop_duplicates(subset=["movie_id", "actor_id"])

# 3. 性别映射
gender_map = {
    0: "unknown",
    1: "female",
    2: "male"
}
cast_df["gender"] = cast_df["gender"].map(gender_map).fillna("unknown")

# 4. 排序（非常重要，保证一致）
cast_df = cast_df.sort_values(["movie_id", "order"]).reset_index(drop=True)

# ==============================
# 导出
# ==============================
cast_df.to_csv("cast_cleaned.csv", index=False)

print("✅ 清洗完成，已生成 cast_cleaned.csv")