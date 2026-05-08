from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import chi2_contingency

from app.charts import chart_layout, empty_chart
from app.config import AMBER, BLUE, GREEN, MUTED, PURPLE, ROSE, TEAL
from app.data import explode_genres


# ─────────────────────────────────────────────
# 数据预处理辅助函数
# ─────────────────────────────────────────────

def _add_derived_cols(df: pd.DataFrame) -> pd.DataFrame:
    """在副本上添加卡方分析所需的派生列，不修改原始 df。"""
    out = df.copy()

    # 盈利标签
    out["profitable"] = np.where(
        (out["revenue"] > 0) & (out["budget"] > 0),
        np.where(out["revenue"] > out["budget"], "Profitable", "Not Profitable"),
        None,
    )

    # 预算分级
    def _tier(b):
        if pd.isna(b) or b <= 0:
            return np.nan
        if b < 10_000_000:
            return "Low (<$10M)"
        if b < 50_000_000:
            return "Mid ($10–50M)"
        if b < 150_000_000:
            return "High ($50–150M)"
        return "Blockbuster (>$150M)"

    tier_order = ["Low (<$10M)", "Mid ($10–50M)", "High ($50–150M)", "Blockbuster (>$150M)"]
    out["budget_tier"] = pd.Categorical(out["budget"].apply(_tier), categories=tier_order, ordered=True)

    # 上映档期
    season_map = {
        1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring",
        5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer",
        9: "Fall", 10: "Fall", 11: "Awards Season", 12: "Awards Season",
    }
    out["season"] = out["release_month"].map(season_map)

    # 评分分级
    def _rating_tier(r):
        if pd.isna(r):
            return np.nan
        if r < 5.0:
            return "Poor (<5)"
        if r < 6.5:
            return "Average (5–6.5)"
        if r < 7.5:
            return "Good (6.5–7.5)"
        return "Great (≥7.5)"

    rating_order = ["Poor (<5)", "Average (5–6.5)", "Good (6.5–7.5)", "Great (≥7.5)"]
    out["rating_tier"] = pd.Categorical(out["avg_rating"].apply(_rating_tier), categories=rating_order, ordered=True)

    return out


# ─────────────────────────────────────────────
# 核心卡方计算
# ─────────────────────────────────────────────

def _run_chi2(df: pd.DataFrame, row_col: str, col_col: str):
    """
    对 df 中的两列做卡方独立性检验。
    返回 (chi2, p_value, dof, contingency_table, residuals_df)
    """
    clean = df[[row_col, col_col]].dropna()
    if len(clean) < 10:
        return None

    contingency = pd.crosstab(clean[row_col], clean[col_col])
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return None

    chi2, p_value, dof, expected = chi2_contingency(contingency)

    # 标准化残差：(observed - expected) / sqrt(expected)
    residuals = (contingency.values - expected) / np.sqrt(expected)
    residuals_df = pd.DataFrame(residuals, index=contingency.index, columns=contingency.columns)

    return chi2, p_value, dof, contingency, residuals_df


# ─────────────────────────────────────────────
# 图表函数
# ─────────────────────────────────────────────

def _heatmap_residuals(residuals_df: pd.DataFrame, title: str) -> go.Figure:
    """标准化残差热力图 — 蓝=正相关，红=负相关。"""
    z = residuals_df.values
    abs_max = max(abs(z.min()), abs(z.max()), 0.1)

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[str(c) for c in residuals_df.columns],
        y=[str(r) for r in residuals_df.index],
        colorscale=[
            [0.0,  "#e11d48"],   # 强负 → 玫红
            [0.45, "#1e3a5f"],   # 轻微负 → 深蓝背景
            [0.5,  "#0f1c2d"],   # 零 → 背景色
            [0.55, "#1e3a5f"],   # 轻微正
            [1.0,  "#3b82f6"],   # 强正 → 蓝
        ],
        zmid=0,
        zmin=-abs_max,
        zmax=abs_max,
        text=[[f"{v:.2f}" for v in row] for row in z],
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#dbe7f8"},
        hovertemplate="%{y} × %{x}<br>Residual: %{z:.3f}<extra></extra>",
        colorbar=dict(
            title=dict(
                text="Std. Residual",
                font=dict(color="#9aa9bd", size=11)
            ),
            tickfont=dict(color="#9aa9bd"),
            thickness=12,
        ),
    ))
    fig.update_layout(**chart_layout(320))
    fig.update_xaxes(title="", tickangle=-35)
    fig.update_yaxes(title="")
    return fig


def _contingency_bar(contingency: pd.DataFrame, normalize: bool = True) -> go.Figure:
    """
    堆叠百分比柱状图，展示各行的列分布。
    normalize=True 时显示比例，False 时显示计数。
    """
    colors = [BLUE, PURPLE, TEAL, AMBER, ROSE, GREEN,
              "#f97316", "#06b6d4", "#84cc16", "#ec4899"]

    if normalize:
        plot_df = contingency.div(contingency.sum(axis=1), axis=0) * 100
        hover_suffix = "%"
        y_title = "Proportion (%)"
    else:
        plot_df = contingency
        hover_suffix = ""
        y_title = "Count"

    fig = go.Figure()
    for i, col in enumerate(plot_df.columns):
        fig.add_trace(go.Bar(
            name=str(col),
            x=[str(r) for r in plot_df.index],
            y=plot_df[col].values,
            marker_color=colors[i % len(colors)],
            marker_line_width=0,
            hovertemplate=f"%{{x}}<br>{col}: %{{y:.1f}}{hover_suffix}<extra></extra>",
        ))

    fig.update_layout(
        **chart_layout(300),
        barmode="stack",
    )
    fig.update_xaxes(title="", tickangle=-35)
    fig.update_yaxes(title=y_title)
    return fig


# ─────────────────────────────────────────────
# p-value 解读工具
# ─────────────────────────────────────────────

def _interpret_p(p: float) -> tuple[str, str, str]:
    """返回 (significance_label, color, interpretation)"""
    if p < 0.001:
        return "p < 0.001 ★★★", GREEN, "Extremely high significance — the association between the two variables is almost impossible to have occurred by chance."
    if p < 0.01:
        return "p < 0.01 ★★", TEAL, "Highly significant — there is a strong association between the two variables."
    if p < 0.05:
        return "p < 0.05 ★", AMBER, "Significant — the hypothesis of independence is rejected at the 95% confidence level."
    if p < 0.10:
        return "p < 0.10", "#f97316", "Marginally significant — there is some association, but the evidence is not sufficient."
    return "p ≥ 0.10", ROSE, "Not significant — unable to reject the hypothesis of independence; the two variables may be unrelated."


def _sig_badge(label: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:.25rem .7rem;border-radius:6px;'
        f'background:rgba(255,255,255,.06);border:1px solid {color};'
        f'color:{color};font-size:12px;font-weight:700">{label}</span>'
    )


# ─────────────────────────────────────────────
# 主渲染函数
# ─────────────────────────────────────────────

def render_chi2_view(df: pd.DataFrame) -> None:
    from app.components import render_chart_panel

    st.markdown(
        '<div class="panel-title" style="font-size:18px;margin-bottom:.6rem">'
        "Chi-Square Independence Tests</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="insight" style="margin-bottom:1rem">'
        "Chi-square independence test: determines whether two categorical variables have a statistically significant association."
        'The <strong>standardized residuals</strong> in the heatmap reveal which combinations occur more or less frequently than expected under &ldquo;complete independence&rdquo;.'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── 构建派生列 ──────────────────────────────
    enriched = _add_derived_cols(df)

    # ── 分析配置 ────────────────────────────────
    TESTS = {
        "Genre × Profitability": {
            "desc": "Is there a statistically significant difference in profit margins across different movie genres?",
            "row": "primary_genre",
            "col": "profitable",
            "df_fn": lambda d: d,
        },
        "Budget Tier × Profitability": {
            "desc": "Is there a statistically significant difference in profitability across different types of movies?",
            "row": "budget_tier",
            "col": "profitable",
            "df_fn": lambda d: d,
        },
        "Release Season × Profitability": {
            "desc": "Is release season (summer, awards season, etc.) correlated with profitability?",
            "row": "season",
            "col": "profitable",
            "df_fn": lambda d: d,
        },
        "Genre × Rating Tier": {
            "desc": "Is there a systematic difference in rating distributions across different movie types/genres?",
            "row": "primary_genre",
            "col": "rating_tier",
            "df_fn": lambda d: d,
        },
        "Budget Tier × Rating Tier": {
            "desc": "Is there a correlation between production budget and audience ratings?",
            "row": "budget_tier",
            "col": "rating_tier",
            "df_fn": lambda d: d,
        },
    }

    # ── UI 选择 ──────────────────────────────────
    with st.container(border=True):
        st.markdown('<div class="panel-title">Select Test</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            chosen = st.selectbox(
                "Analysis",
                list(TESTS.keys()),
                key="chi2_test",
                label_visibility="collapsed",
            )
        with c2:
            normalize = st.toggle("Show proportions (vs counts)", value=True, key="chi2_norm")

        cfg = TESTS[chosen]
        st.markdown(
            f'<div class="insight">{cfg["desc"]}</div>',
            unsafe_allow_html=True,
        )

    # ── 运行检验 ─────────────────────────────────
    result = _run_chi2(cfg["df_fn"](enriched), cfg["row"], cfg["col"])

    if result is None:
        st.warning("Insufficient data under the current filter conditions to perform a chi-square test (a minimum 2×2 contingency table with a sample size ≥ 10)")
        return

    chi2_val, p_val, dof, contingency, residuals_df = result
    sig_label, sig_color, interpretation = _interpret_p(p_val)

    # ── KPI 条 ───────────────────────────────────
    cramer_v = float(np.sqrt(chi2_val / (contingency.values.sum() * (min(contingency.shape) - 1))))

    st.html(
        '<div class="kpi-grid" style="grid-template-columns:repeat(4,minmax(160px,1fr));margin:.5rem 0 .8rem">'
        + _pred_kpi("χ² Statistic",    f"{chi2_val:.2f}",  "Chi-square value",          BLUE)
        + _pred_kpi("Degrees of Freedom", str(dof),         "(rows−1)×(cols−1)",          PURPLE)
        + _pred_kpi("p-value",          f"{p_val:.4f}" if p_val >= 0.0001 else "<0.0001",
                    interpretation[:28] + "…",              sig_color)
        + _pred_kpi("Cramér's V",       f"{cramer_v:.3f}",  "Effect size (0=none, 1=perfect)", TEAL)
        + "</div>"
    )

    # 显著性徽章 + 解读
    st.markdown(
        f'<div style="margin-bottom:.9rem">'
        f'{_sig_badge(sig_label, sig_color)}'
        f'<span style="color:#c8d4e6;font-size:13px;margin-left:.6rem">{interpretation}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── 图表区域 ─────────────────────────────────
    left, right = st.columns([0.52, 0.48], gap="medium")
    with left:
        render_chart_panel(
            f"Standardized Residuals — {chosen}",
            _heatmap_residuals(residuals_df, chosen),
            "Blue: the combination occurs more frequently than expected under independence (positive association); Red: occurs less frequently (negative association). |Residual| > 2 indicates a statistically significant deviation.",
        )
    with right:
        render_chart_panel(
            f"{'Proportion' if normalize else 'Count'} Distribution — {chosen}",
            _contingency_bar(contingency, normalize),
            "Column distribution by category. If the color proportions across rows are similar, the two variables are close to independent; the greater the difference, the stronger the association.",
        )

    # ── 列联表原始数据 ────────────────────────────
    with st.container(border=True):
        st.markdown('<div class="panel-title">Contingency Table (Observed Counts)</div>', unsafe_allow_html=True)
        st.dataframe(contingency, use_container_width=True, height=min(40 * (len(contingency) + 2), 320))
        st.markdown(
            f'<div class="insight">Total sample size：{int(contingency.values.sum()):,} movie. '
            f'矩阵大小：{contingency.shape[0]}×{contingency.shape[1]}</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# 内部 KPI 卡片（复用 predict.py 的样式）
# ─────────────────────────────────────────────

def _pred_kpi(label: str, value: str, sub: str, accent: str) -> str:
    return (
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-foot"><div class="kpi-change neu" style="font-size:11px">{sub}</div></div>'
        f"</div>"
    )
