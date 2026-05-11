import pandas as pd
import json

# CSV 文件路径
movies_file = r"C:\xampp\mysql\data\cleaned_dataset\movies_metadata_cleaned.csv"

# 读取 CSV
movies_df = pd.read_csv(movies_file)

# 输出列名，检查列名是否匹配脚本
print("Columns in movies_metadata_cleaned.csv:")
print(movies_df.columns.tolist())
print("-" * 50)

# 需要检查的字段
json_columns = [
    'belongs_to_collection',
    'genres',
    'production_companies',
    'production_countries',
    'spoken_languages'
]

# 统计每个字段有效 JSON 的行数
def count_valid_json(column):
    count = 0
    for val in movies_df[column].dropna():
        try:
            js = json.loads(val)
            if js:  # 非空 JSON 才算有效
                count += 1
        except:
            continue
    return count

print("Valid JSON row counts:")
for col in json_columns:
    valid_count = count_valid_json(col)
    print(f"{col}: {valid_count} valid rows")

# 简单统计空值情况
print("-" * 50)
print("Empty values count for each JSON column:")
print(movies_df[json_columns].isna().sum())
