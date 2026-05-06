# 26dpwProject

这是一个围绕 TMDB/IMDB 电影数据展开的数据库与数据可视化项目。当前项目主要包含数据库 ER 设计、MariaDB/MySQL 建表脚本、静态电影数据分析看板，以及一个可交互的 Streamlit 电影数据 demo。

本 README 主要给组员同步项目结构、运行方式和下一步任务。

## 项目内容

- 电影数据库的 ER 模型与关系设计文档。
- `tmdb` 数据库及相关表的 SQL 建表脚本。
- 一个基于 HTML、CSS、JavaScript 和 Chart.js 的静态电影分析 dashboard。
- 一个位于 `demo-movies/` 目录下的 Streamlit 电影数据探索 demo。

## 文件结构

```text
.
├── ERmodel.pdf                 # ER 模型文档
├── ER关系.pdf                  # ER 关系文档
├── movie_dashboard.html        # 静态电影数据分析 dashboard
├── tmdb.sql/                   # TMDB 数据库和数据表 SQL 脚本
└── demo-movies/                # Streamlit 电影数据探索 demo
```

## 如何运行

### 1. 查看静态 Dashboard

直接用浏览器打开根目录下的 `movie_dashboard.html`。

### 2. 运行 Streamlit Demo

进入 `demo-movies/` 目录后运行：

```sh
uv venv
.venv/bin/activate
uv sync
streamlit run streamlit_app.py
```

如果没有安装 `uv`，需要先安装，或者改用自己熟悉的 Python 虚拟环境方式安装依赖。

### 3. 导入数据库脚本

`tmdb.sql/` 目录中的 SQL 文件来自 MariaDB/MySQL 环境。建议先导入 `tmdb_database.sql`，再根据需要导入各个 table 脚本。

## 当前进度

- 已整理电影数据库的 ER 设计文件。
- 已准备 `tmdb` 数据库相关 SQL 脚本。
- 已完成一个静态版电影数据分析 dashboard 页面。
- 已加入 Streamlit demo，方便后续参考交互式数据展示方式。

## 接下来的 TODO

- 核对 ER 图和 SQL 表结构，确认实体、主键、外键和关系是否一致。
- 整理数据库导入顺序，补充清晰的建库和导入步骤。
- 准备一份小规模测试数据，方便组员本地验证 SQL 和 dashboard。
- 把静态 dashboard 中的示例数据替换为真实数据库查询结果。
- 设计后端接口，用于电影搜索、筛选、评分统计、类型统计等功能。
- 补充数据库连接配置说明，例如用户名、密码、host、端口和环境变量。
- 优化 dashboard 的移动端显示和交互细节。
- 为 dashboard 和 Streamlit demo 添加截图，方便汇报和文档展示。
- 增加基础测试或检查脚本，用来验证表是否创建成功、关键字段是否存在。
- 清理临时文件、重复文件和实验性内容，准备最终提交版本。
- 撰写项目报告，说明数据库设计思路、实现过程、遇到的问题和后续改进方向。

## 组员协作建议

- 数据库部分：优先确认 ER 图、SQL 表结构和测试数据。
- 前端部分：继续完善 `movie_dashboard.html` 的页面展示和交互。
- 后端部分：规划 API，后续连接数据库和前端页面。
- 文档部分：维护 README、截图、运行说明和最终项目报告。
