import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import load_data, GLOBAL_CSS, section_header

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
df = load_data()

st.markdown("""
<div style='padding:8px 0 4px 0;'>
    <span style='font-size:24px; font-weight:700;'>Feature Engineering Insights</span><br/>
    <span style='font-size:12px; color:#8b8fa8; letter-spacing:0.08em;'>
        RAW DATA RARELY WORKS STRAIGHT OUT OF THE BOX. HERE IS HOW THIS DATASET WAS PREPARED.
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("### View Mode")
    advanced = st.toggle(
        "Advanced Insights",
        value=False,
        help=(
            "OFF: Fan-friendly overview — histogram comparison only.\n\n"
            "ON: Full technical analysis — correlation matrix, normalisation, "
            "and scaled scatter for mentor or technical evaluation."
        ),
    )
    st.divider()
    year_range = st.slider("Year range", int(df["year"].min()), int(df["year"].max()), (2013, 2022))

fdf = df[df["year"].between(year_range[0], year_range[1])].copy()

if fdf.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── Always visible: Raw vs Log histogram ─────────────────────────────────────
section_header(
    "Why the raw price data needed a log transform",
    "Left: heavily right-skewed raw values. Right: log transform makes the distribution usable for modelling."
)

col1, col2 = st.columns(2)

with col1:
    fig_raw = px.histogram(
        fdf, x="amount", nbins=45,
        title="Raw amount — a handful of stars compress everyone else to zero",
        color_discrete_sequence=["#f97066"],
        labels={"amount": "Amount (Rs)", "count": "Players"},
    )
    fig_raw.update_layout(margin=dict(t=50, b=20), height=340)
    st.plotly_chart(fig_raw, use_container_width=True)

with col2:
    fig_log = px.histogram(
        fdf, x="amount_log", nbins=45,
        title="Log-transformed — now models can actually learn from this",
        color_discrete_sequence=["#2dd4bf"],
        labels={"amount_log": "log(Amount)", "count": "Players"},
    )
    fig_log.update_layout(margin=dict(t=50, b=20), height=340)
    st.plotly_chart(fig_log, use_container_width=True)

# ── Advanced section ──────────────────────────────────────────────────────────
if advanced:
    st.info(
        "Advanced Insights mode is ON. "
        "The charts below show encoded feature relationships and scaling effects "
        "used during data preparation for modelling.",
        icon="🔬",
    )
    st.divider()

    # Correlation heatmap
    section_header(
        "Feature correlation matrix",
        "Strong correlation between amount, amount_log, and amount_normalized is expected — they are all derived from the same column."
    )

    encoded_cols = [
        "amount","amount_log","amount_scaled",
        "amount_normalized","role_encoded","team_encoded",
        "origin_encoded","year_scaled",
    ]
    corr = fdf[encoded_cols].corr()

    fig_c, ax = plt.subplots(figsize=(9, 6))
    fig_c.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="YlOrRd",
    ax=ax,
    linewidths=0.4,
    linecolor=(0, 0, 0, 0.1),  # FIXED
    annot_kws={"size": 9},
    cbar_kws={"shrink": 0.8},
)
    ax.set_title("Encoded feature correlations", color="#edeef2", pad=12)
    ax.tick_params(colors="#edeef2", labelsize=9)
    plt.xticks(rotation=35, ha="right", color="#edeef2")
    plt.yticks(rotation=0, color="#edeef2")
    plt.tight_layout()
    st.pyplot(fig_c)
    plt.close(fig_c)

    st.divider()

    # Normalised distribution + spread comparison
    section_header(
        "Normalised amount distribution and scaling comparison",
        "amount_normalized rescales to [0,1] via min-max. amount_scaled applies z-score standardisation."
    )

    col3, col4 = st.columns(2)

    with col3:
        fig_norm = px.histogram(
            fdf, x="amount_normalized", nbins=40,
            title="Normalised amount [0-1] — shape mirrors raw, only scale changes",
            color_discrete_sequence=["#a78bfa"],
            labels={"amount_normalized": "Normalised Value"},
        )
        fig_norm.update_layout(margin=dict(t=50, b=20), height=320)
        st.plotly_chart(fig_norm, use_container_width=True)

    with col4:
        fig_box = go.Figure()
        for col_name, color, label in [
            ("amount_log",        "#f0b429", "Log"),
            ("amount_scaled",     "#f97066", "Scaled"),
            ("amount_normalized", "#a78bfa", "Normalized"),
        ]:
            fig_box.add_trace(go.Box(
                y=fdf[col_name], name=label,
                marker_color=color, boxmean=True,
            ))
        fig_box.update_layout(
            title="Log vs Scaled vs Normalized — spread comparison",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=320, margin=dict(t=50, b=20),
            font=dict(family="monospace", color="#edeef2"),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # Scaled vs original scatter
    section_header(
        "Standard scaling confirms a clean linear relationship",
        "Every point should fall on a diagonal — any deviation would indicate a data issue."
    )

    scat = fdf[["amount","amount_scaled","role","player","year"]].copy()
    scat["Raw (Rs Cr)"] = (scat["amount"] / 1e7).round(2)

    fig_scat = px.scatter(
        scat, x="Raw (Rs Cr)", y="amount_scaled",
        color="role",
        color_discrete_map={
            "Batsman":       "#f0b429",
            "Bowler":        "#2dd4bf",
            "All-Rounder":   "#f97066",
            "Wicket Keeper": "#a78bfa",
        },
        hover_data=["player", "year"], opacity=0.65,
        title="Raw vs standard-scaled — the diagonal confirms scaling worked correctly",
        labels={"Raw (Rs Cr)": "Raw Amount (Rs Cr)", "amount_scaled": "Scaled Amount (sigma)"},
    )
    fig_scat.update_traces(marker=dict(size=6))
    fig_scat.update_layout(height=420, margin=dict(t=50, b=20), legend_title="Role")
    st.plotly_chart(fig_scat, use_container_width=True)

else:
    st.divider()
    st.markdown(
        "<div style='padding:14px 16px; background:#13161e; border-radius:8px; "
        "border-left:3px solid #f0b429; font-size:13px; color:#8b8fa8;'>"
        "Toggle <b style='color:#f0b429;'>Advanced Insights</b> in the sidebar to reveal "
        "the correlation matrix, normalisation analysis, and scaling scatter — "
        "intended for technical or mentor evaluation.</div>",
        unsafe_allow_html=True,
    )
