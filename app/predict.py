from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import OrdinalEncoder

from app.charts import chart_layout, empty_chart
from app.config import AMBER, BLUE, GREEN, MONTHS, PURPLE, ROSE, TEAL
from app.metrics import money


@st.cache_resource(show_spinner="Training prediction models…")
def _build_models(_df: pd.DataFrame):
    train = _df[
        (_df["budget"] > 0)
        & (_df["revenue"] > 0)
        & _df["roi"].notna()
        & _df["runtime"].notna()
        & (_df["runtime"] > 0)
        & _df["release_month"].notna()
        & _df["primary_genre"].notna()
        & (_df["primary_genre"] != "Unknown")
    ].copy()

    genre_enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    train["genre_enc"] = genre_enc.fit_transform(train[["primary_genre"]])
    train["log_budget"] = np.log1p(train["budget"])

    FEATURES = ["log_budget", "genre_enc", "release_month", "runtime"]
    X = train[FEATURES].values.astype(float)

    roi_cap = train["roi"].quantile(0.97)
    y_rev = np.log1p(train["revenue"].values)
    y_roi = train["roi"].clip(upper=roi_cap).values
    y_profit = (train["revenue"] > train["budget"]).astype(int).values

    params = dict(
        n_estimators=300, learning_rate=0.05, max_depth=4,
        subsample=0.8, min_samples_leaf=10, random_state=42,
    )
    rev_model = GradientBoostingRegressor(**params).fit(X, y_rev)
    roi_model = GradientBoostingRegressor(**params).fit(X, y_roi)
    profit_model = GradientBoostingClassifier(**params).fit(X, y_profit)

    return rev_model, roi_model, profit_model, genre_enc, FEATURES


def predict_movie(df: pd.DataFrame, budget: float, genre: str, release_month: int, runtime: int) -> dict:
    rev_model, roi_model, profit_model, genre_enc, FEATURES = _build_models(df)

    genre_code = genre_enc.transform([[genre]])[0][0]
    X = np.array([[np.log1p(budget), genre_code, release_month, runtime]])

    pred_revenue = float(np.expm1(rev_model.predict(X)[0]))
    pred_roi = float(roi_model.predict(X)[0])
    profit_prob = float(profit_model.predict_proba(X)[0][1])

    return {
        "predicted_revenue": pred_revenue,
        "predicted_roi": pred_roi,
        "profit_probability": profit_prob,
        "lower_revenue": pred_revenue * 0.72,
        "upper_revenue": pred_revenue * 1.42,
    }


def _comparable_scatter(df: pd.DataFrame, budget: float, genre: str, pred_revenue: float) -> go.Figure:
    comps = df[
        (df["budget"] >= budget * 0.5)
        & (df["budget"] <= budget * 1.5)
        & (df["primary_genre"] == genre)
        & (df["revenue"] > 0)
    ]
    if comps.empty:
        comps = df[(df["budget"] >= budget * 0.5) & (df["budget"] <= budget * 1.5) & (df["revenue"] > 0)]

    fig = go.Figure()
    if not comps.empty:
        fig.add_trace(go.Scatter(
            x=comps["budget"], y=comps["revenue"],
            mode="markers", name="Historical",
            text=comps["title"],
            hovertemplate="<b>%{text}</b><br>Budget: $%{x:,.0f}<br>Revenue: $%{y:,.0f}<extra></extra>",
            marker=dict(size=7, color=BLUE, opacity=0.65, line=dict(width=0)),
        ))

    fig.add_trace(go.Scatter(
        x=[budget], y=[pred_revenue],
        mode="markers+text", name="Prediction",
        text=["Your Movie"], textposition="top center",
        textfont=dict(color=AMBER, size=12, family="Inter"),
        hovertemplate="<b>Predicted</b><br>Budget: $%{x:,.0f}<br>Revenue: $%{y:,.0f}<extra></extra>",
        marker=dict(size=14, color=AMBER, symbol="star", line=dict(width=1.5, color="#fff")),
    ))

    fig.update_layout(**chart_layout(320))
    fig.update_xaxes(title="Budget (USD)")
    fig.update_yaxes(title="Revenue (USD)")
    return fig


def _roi_histogram(df: pd.DataFrame, genre: str) -> go.Figure:
    genre_df = df[(df["primary_genre"] == genre) & df["roi"].notna() & (df["roi"] > 0)].copy()
    if genre_df.empty:
        return empty_chart(f"No ROI data for genre: {genre}", 280)

    cap = genre_df["roi"].quantile(0.96)
    plot_df = genre_df[genre_df["roi"] <= cap]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=plot_df["roi"], nbinsx=35,
        marker=dict(color=PURPLE, opacity=0.80, line=dict(color="#07111f", width=0.6)),
        hovertemplate="ROI: %{x:.1f}x<br>Count: %{y}<extra></extra>",
        name="Historical ROI",
    ))
    fig.update_layout(**chart_layout(280))
    fig.update_xaxes(title=f"ROI (x)  ·  {genre}")
    fig.update_yaxes(title="Number of Films")
    return fig


def _comparable_table(df: pd.DataFrame, budget: float, genre: str) -> pd.DataFrame:
    valid = df[
        (df["budget"] > 0) & (df["revenue"] > 0)
        & (df["primary_genre"] == genre) & df["roi"].notna()
    ].copy()
    if valid.empty:
        valid = df[(df["budget"] > 0) & (df["revenue"] > 0) & df["roi"].notna()].copy()

    valid["budget_diff"] = (valid["budget"] - budget).abs()
    top5 = valid.nsmallest(5, "budget_diff")[
        ["title", "year", "budget", "revenue", "roi", "avg_rating", "primary_genre"]
    ].copy()
    top5 = top5.rename(columns={
        "title": "Title", "year": "Year", "budget": "Budget",
        "revenue": "Revenue", "roi": "ROI", "avg_rating": "Rating", "primary_genre": "Genre",
    })
    top5["Budget"] = top5["Budget"].apply(money)
    top5["Revenue"] = top5["Revenue"].apply(money)
    top5["ROI"] = top5["ROI"].apply(lambda v: f"{v:.2f}x" if pd.notna(v) else "—")
    top5["Rating"] = top5["Rating"].apply(lambda v: f"{v:.1f}" if pd.notna(v) else "—")
    return top5.reset_index(drop=True)


def _pred_kpi(label: str, value: str, sub: str, accent: str) -> str:
    return (
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-foot"><div class="kpi-change neu" style="font-size:11px">{sub}</div></div>'
        f"</div>"
    )


def render_predict_view(df: pd.DataFrame) -> None:
    from app.components import render_chart_panel

    st.markdown(
        '<div style="font-size:28px;font-weight:900;color:#f7fbff;text-align:center;'
        'margin:0 0 1.2rem;letter-spacing:-.02em;">'
        "🎬 Movie Revenue &amp; ROI Predictor</div>",
        unsafe_allow_html=True,
    )

    valid_genres = sorted(
        df[
            (df["budget"] > 0) & (df["revenue"] > 0) & df["roi"].notna()
            & (df["primary_genre"] != "Unknown") & df["primary_genre"].notna()
        ]["primary_genre"].unique().tolist()
    )

    with st.container(border=True):
        st.markdown('<div class="panel-title">Input Parameters</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1:
            budget_m = st.number_input(
                "Budget (USD millions)", min_value=0.1, max_value=500.0,
                value=50.0, step=1.0, format="%.1f", key="pred_budget",
            )
        with c2:
            default_idx = valid_genres.index("Action") if "Action" in valid_genres else 0
            genre = st.selectbox("Primary Genre", valid_genres, index=default_idx, key="pred_genre")
        with c3:
            release_month = st.selectbox(
                "Release Month", list(range(1, 13)),
                format_func=lambda m: MONTHS[m - 1], index=5, key="pred_month",
            )
        with c4:
            runtime = st.number_input(
                "Runtime (minutes)", min_value=60, max_value=240,
                value=110, step=5, key="pred_runtime",
            )
        run_btn = st.button("Run Prediction", type="primary", width="stretch")

    if not run_btn and "pred_result" not in st.session_state:
        st.markdown(
            '<div class="insight">Fill in parameters above and click '
            "<strong>Run Prediction</strong> to see forecast results.</div>",
            unsafe_allow_html=True,
        )
        return

    if run_btn:
        budget = budget_m * 1_000_000
        st.session_state["pred_result"] = predict_movie(df, budget, genre, release_month, runtime)
        st.session_state["pred_inputs"] = {
            "budget": budget, "genre": genre,
            "release_month": release_month, "runtime": runtime,
        }

    result = st.session_state["pred_result"]
    inputs = st.session_state["pred_inputs"]

    pred_revenue = result["predicted_revenue"]
    pred_roi = result["predicted_roi"]
    profit_prob = result["profit_probability"]

    prob_color = GREEN if profit_prob >= 0.6 else (AMBER if profit_prob >= 0.4 else ROSE)
    roi_color = GREEN if pred_roi >= 2.0 else (AMBER if pred_roi >= 1.0 else ROSE)

    st.html(
        '<div class="kpi-grid" style="grid-template-columns:repeat(3,minmax(180px,1fr));margin:.5rem 0 .8rem">'
        + _pred_kpi("Predicted Revenue", money(pred_revenue),
                    f"Range: {money(result['lower_revenue'])} – {money(result['upper_revenue'])}", TEAL)
        + _pred_kpi("Predicted ROI", f"{pred_roi:.2f}x", f"Input budget: {money(inputs['budget'])}", roi_color)
        + _pred_kpi("Profit Probability", f"{profit_prob * 100:.1f}%", "P(revenue > budget)", prob_color)
        + "</div>"
    )

    left, right = st.columns([0.55, 0.45], gap="medium")
    with left:
        render_chart_panel(
            "Comparable Films — Budget vs Revenue",
            _comparable_scatter(df, inputs["budget"], inputs["genre"], pred_revenue),
            f"Films with similar budget (±50%) in {inputs['genre']}. Gold star marks the prediction.",
        )
    with right:
        render_chart_panel(
            f"Historical ROI Distribution — {inputs['genre']}",
            _roi_histogram(df, inputs["genre"]),
            "Distribution of ROI for same-genre films (96th-percentile capped).",
        )

    with st.container(border=True):
        st.markdown('<div class="panel-title">Top 5 Comparable Films</div>', unsafe_allow_html=True)
        st.dataframe(_comparable_table(df, inputs["budget"], inputs["genre"]),
                     width="stretch", hide_index=True, height=220)
        st.markdown(
            '<div class="insight">Ranked by proximity to your input budget within the same genre.</div>',
            unsafe_allow_html=True,
        )
