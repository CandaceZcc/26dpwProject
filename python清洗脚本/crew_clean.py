import pandas as pd
import json

# 读取数据
credits = pd.read_csv("credits.csv")


# JSON解析函数
def parse_json(text):
    if pd.isna(text) or text in ["", "[]"]:
        return []
    try:
        return json.loads(text.replace("'", '"'))
    except:
        return []


# ==============================
# 提取 crew
# ==============================
crew_rows = []

for _, row in credits.iterrows():
    movie_id = row["id"]
    crew_list = parse_json(row["crew"])

    for c in crew_list:
        crew_rows.append({
            "movie_id": movie_id,
            "crew_id": c.get("id"),
            "name": c.get("name"),
            "job": c.get("job"),
            "department": c.get("department")
        })

# 转 DataFrame
crew_df = pd.DataFrame(crew_rows)

# ==============================
# 清洗
# ==============================

# 1. 删除无效 crew_id
crew_df = crew_df.dropna(subset=["crew_id"])

# 2. 去重
crew_df = crew_df.drop_duplicates(subset=["movie_id", "crew_id", "job"])

# 3. 排序（保证一致性）
crew_df = crew_df.sort_values(["movie_id", "crew_id"]).reset_index(drop=True)

# ==============================
# 导出 crew 表
# ==============================
crew_df.to_csv("crew_cleaned.csv", index=False)

print("✅ crew_cleaned.csv 已生成")

# ==============================
# 🎬 提取 directors 表（可选但强烈建议）
# ==============================
directors_df = crew_df[crew_df["job"] == "Director"][["crew_id", "name"]]

# 去重
directors_df = directors_df.drop_duplicates()

# 排序
directors_df = directors_df.sort_values("crew_id").reset_index(drop=True)

directors_df.to_csv("directors.csv", index=False)

print("✅ directors.csv 已生成")