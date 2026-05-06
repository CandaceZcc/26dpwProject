# 26dpwProject

这是一个围绕 TMDB/IMDB 电影数据展开的数据库与数据可视化项目。当前主应用是基于 Python + Streamlit 的交互式电影分析 dashboard，用于回答 SDS 中提出的几个核心问题：票房成功因素、类型收益、上映时间影响，以及评分分布。

项目现在只保留一个主入口：`streamlit_app.py`。

## 当前实现内容

- 从 `tmdb.sql/` 中解析 movie、genres、link_genres、rate 等核心 SQL 数据。
- 生成本地分析宽表：`data/processed_movies.csv`。
- 使用 Streamlit 实现 dashboard 主页面：`streamlit_app.py`。
- 采用模块化 dashboard 架构，将数据、指标、图表、组件和样式拆分到 `app/` 目录。
- 使用 Plotly 绘制 5 个核心图表。
- 使用自定义 CSS 尽量复刻 `GUI.png` 的深色卡片式 dashboard 效果。
- 将 `rate.rating` 从 0.5-5 分制换算为 0-10 分制，用于 GUI 中的 Rating 图表。
- 过滤器和视图切换已移入 Streamlit 原生 sidebar，主页面只展示标题、KPI 和图表。

## 文件结构

```text
.
├── streamlit_app.py            # 主 Streamlit dashboard
├── requirements.txt            # 主项目 Python 依赖
├── run_windows.bat             # Windows 一键安装并启动
├── run_unix.sh                 # macOS/Linux 一键安装并启动
├── app/
│   ├── config.py               # 常量、颜色、默认配置
│   ├── data.py                 # 数据加载和筛选
│   ├── metrics.py              # KPI 和类型表现计算
│   ├── charts.py               # Plotly 图表
│   ├── components.py           # Sidebar、KPI、图表卡片和导出
│   └── styles.py               # 全局 CSS
├── scripts/
│   └── build_dataset.py        # 从 SQL 生成分析数据
├── data/
│   ├── processed_movies.csv    # dashboard 直接读取的数据文件
│   └── dataset_summary.json    # 数据生成摘要
├── tmdb.sql/                   # 原始 TMDB SQL 导出文件
├── GUI.png                     # dashboard 视觉参考图
├── IMDB_SDS_Draft.docx         # 系统设计文档草稿
├── ERmodel.pdf                 # ER 模型文档
├── ER关系.pdf                  # ER 关系文档
└── movie_dashboard.html        # 早期 HTML 预览版本
```

## 如何运行主 Dashboard

### 最简单方式：Windows

大部分组员如果使用 Windows，可以直接双击项目根目录下的：

```text
run_windows.bat
```

它会自动完成：

- 创建 `.venv` 虚拟环境。
- 安装 `requirements.txt` 中的依赖。
- 启动 Streamlit dashboard。

如果双击后窗口一闪而过，可以在项目目录中打开 PowerShell，然后运行：

```powershell
.\run_windows.bat
```

启动成功后浏览器会打开本地页面，通常地址为：

```text
http://localhost:8501
```

### 最简单方式：macOS / Linux

```sh
chmod +x run_unix.sh
./run_unix.sh
```

## 手动安装方式

### 1. 创建虚拟环境

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 不允许激活虚拟环境，可以改用不激活的方式运行后续命令，见下面的“Windows 不激活环境运行方式”。

macOS / Linux：

```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

Windows PowerShell：

```powershell
python -m pip install -r requirements.txt
```

macOS / Linux：

```sh
python3 -m pip install -r requirements.txt
```

如果已经激活 `.venv`，也可以直接使用 `pip install -r requirements.txt`。

### 3. 生成分析数据

通常可以跳过这一步，因为仓库已经包含 `data/processed_movies.csv`，pull 下来后可以直接运行 dashboard。

如果需要重新从 SQL 生成数据：

Windows PowerShell：

```powershell
python scripts\build_dataset.py
```

macOS / Linux：

```sh
python3 scripts/build_dataset.py
```

Streamlit 启动时如果发现数据文件不存在，也会自动尝试生成。

### 4. 启动 dashboard

Windows 推荐使用下面这条命令，避免出现 `streamlit` 命令找不到：

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

macOS / Linux 推荐使用：

```sh
.venv/bin/streamlit run streamlit_app.py
```

如果已经执行过 `source .venv/bin/activate`，也可以直接运行：

```sh
streamlit run streamlit_app.py
```

启动后浏览器会打开本地页面，通常地址为：

```text
http://localhost:8501
```

## 常见问题

### 1. Windows 提示找不到 `python`

先安装 Python 3.10 或以上版本，并在安装时勾选 `Add Python to PATH`。安装后重新打开 PowerShell。

### 2. PowerShell 不允许激活 `.venv`

可以不激活虚拟环境，直接运行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

### 3. 提示 `streamlit: command not found`

不要直接运行 `streamlit run streamlit_app.py`，改用：

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

### 4. 依赖安装很慢

可以换国内网络或稍后重试。依赖只需要第一次安装，之后运行会快很多。

## Dashboard 功能

- 顶部 KPI：Total Movies、Avg Revenue、Avg ROI、Avg Rating、Total Budget、Total Revenue。
- Sidebar：视图切换、年份范围、电影类型、快捷年份范围、最低投票数、类型表现摘要和导出入口。
- 图表：
  - Box Office Success Analysis：预算与收入关系。
  - Genre Profitability：不同类型的 ROI 或平均收入。
  - Revenue by Release Month：上映月份与收入趋势。
  - Budget vs ROI：预算与投资回报率关系。
  - Rating Distribution by Genre：不同类型电影的评分分布。
- 视图：
  - Overview：显示完整 dashboard。
  - Revenue：聚焦收入、预算和 ROI 相关分析。
  - Genres：聚焦类型 ROI 和评分分布。
  - Time：聚焦上映月份与收入趋势。
  - Export：导出当前筛选后的 CSV 数据。

## 代码结构说明

- `streamlit_app.py`：应用入口，只负责页面编排。
- `app/data.py`：读取 `data/processed_movies.csv`，并按 sidebar 条件筛选数据。
- `app/metrics.py`：计算 KPI、金额格式、类型最佳/最差表现。
- `app/charts.py`：生成 Plotly 图表。
- `app/components.py`：渲染 sidebar、标题、KPI 卡片、图表卡片、导出和 footer。
- `app/styles.py`：注入 dashboard 深色主题 CSS。

## 可行性与正确性检查

- SDS 和 `GUI.png` 的目标一致，均要求单页深色电影分析 dashboard。
- SQL 数据库结构基本符合 ER 设计思路，核心表包括 `movie`、`genres`、`link_genres`、`rate`。
- 当前 SQL 中 `movie` 表没有直接的 `vote_average` 字段，因此 dashboard 使用 `rate` 表聚合平均评分。
- `rate.rating` 原始范围是 0.5-5，dashboard 中已换算为 0-10，便于匹配 SDS/GUI 的评分设计。
- ROI 计算规则为 `revenue / budget`。预算或收入为 0 的电影不会参与 ROI 相关图表和 Avg ROI。
- 现有数据中存在极端 ROI 值，图表展示时会对 Budget vs ROI 做 98 分位视觉截尾，避免坐标轴被异常值拉伸。

## 接下来的 TODO

- 继续微调 CSS，让 Streamlit 页面更接近 `GUI.png` 的像素效果，尤其是不同浏览器缩放比例下的细节。
- 增加 KPI sparkline 的真实历史趋势解释。
- 继续完善 Revenue、Genres、Time 等视图的交互细节。
- 补充 dashboard 截图，放入最终报告。
- 检查 ER 图与 SQL 外键是否完全一致，并在报告中说明差异。
- 根据老师要求决定是否保留早期 `movie_dashboard.html`。
- 如果后续需要数据库演示，可增加 MySQL 连接模式，但默认仍建议使用本地 CSV。

## 组员协作建议

- 数据库同学：检查 `tmdb.sql/` 和 ER 图的一致性，补充数据导入说明。
- 前端/可视化同学：继续对照 `GUI.png` 调整 Streamlit 页面效果。
- 文档同学：把 README 中的可行性说明整理进最终报告。
- 测试同学：按运行步骤在不同电脑上验证 dashboard 能否正常启动。
