import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, ROLE_COLORS, GLOBAL_CSS, section_header

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
df = load_data()

st.markdown("""
<div style='padding:8px 0 4px 0;'>
    <span style='font-size:24px; font-weight:700;'>Team Spending Analysis</span><br/>
    <span style='font-size:12px; color:#8b8fa8; letter-spacing:0.08em;'>
        HIGH SPEND DIDN'T ALWAYS BUY TROPHIES. HERE'S WHERE EACH FRANCHISE PUT THEIR MONEY.
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("### Filters")
    year_range     = st.slider("Year range", int(df["year"].min()), int(df["year"].max()), (2013, 2022))
    all_teams      = sorted(df["team"].unique())
    selected_teams = st.multiselect("Teams", all_teams, default=all_teams)
    roles          = st.multiselect("Role", sorted(df["role"].unique()), default=sorted(df["role"].unique()))

fdf = df[
    (df["year"].between(year_range[0], year_range[1])) &
    (df["team"].isin(selected_teams)) &
    (df["role"].isin(roles))
].copy()

if fdf.empty:
    st.warning("No data matches the current filters.")
    st.stop()

fdf["Amount (Rs Cr)"] = (fdf["amount"] / 1e7).round(2)

# ── Heatmap ───────────────────────────────────────────────────────────────────
section_header(
    "Spending intensity by team and season",
    "Darker cells = higher spend. Blank cells = team not active that year."
)

heat = fdf.groupby(["team", "year"])["amount"].sum().reset_index()
heat["Spend (Rs Cr)"] = (heat["amount"] / 1e7).round(2)
pivot = heat.pivot(index="team", columns="year", values="Spend (Rs Cr)").fillna(0)

fig_heat = go.Figure(go.Heatmap(
    z=pivot.values,
    x=[str(y) for y in pivot.columns],
    y=pivot.index.tolist(),
    colorscale="YlOrRd",
    text=pivot.values.round(1),
    texttemplate="%{text}",
    textfont={"size": 10},
    hovertemplate="Team: %{y}<br>Year: %{x}<br>Spend: Rs%{z} Cr<extra></extra>",
    colorbar=dict(title="Rs Cr"),
))
fig_heat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Year", yaxis_title="",
    margin=dict(t=20, b=20), height=430,
    font=dict(family="monospace", color="#edeef2"),
)
st.plotly_chart(fig_heat, use_container_width=True)
st.divider()

# ── Treemap + Ranking ─────────────────────────────────────────────────────────
section_header(
    "Cumulative budget distribution",
    "Treemap area = total spend across selected seasons. Bar = ranked order."
)

col1, col2 = st.columns(2)

with col1:
    tree = (
        fdf.groupby("team")["amount"].sum().reset_index()
        .assign(**{"Total (Rs Cr)": lambda d: (d["amount"] / 1e7).round(2)})
    )
    fig_tree = px.treemap(
        tree, path=["team"], values="Total (Rs Cr)",
        color="Total (Rs Cr)", color_continuous_scale="YlOrRd",
        custom_data=["Total (Rs Cr)"],
        title="Mumbai Indians and CSK consistently outspend the field",
    )
    fig_tree.update_traces(
        texttemplate="<b>%{label}</b><br>Rs%{customdata[0]} Cr",
        hovertemplate="<b>%{label}</b><br>Total: Rs%{customdata[0]} Cr<extra></extra>",
    )
    fig_tree.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=10),
        height=380,
        coloraxis_showscale=False,
        font=dict(family="monospace"),
    )
    st.plotly_chart(fig_tree, use_container_width=True)

with col2:
    rank = (
        fdf.groupby("team")["amount"].sum().reset_index()
        .sort_values("amount")
        .assign(**{"Spend (Rs Cr)": lambda d: (d["amount"] / 1e7).round(2)})
    )
    fig_rank = px.bar(
        rank, x="Spend (Rs Cr)", y="team", orientation="h",
        text="Spend (Rs Cr)", color="Spend (Rs Cr)", color_continuous_scale="YlOrRd",
        title="Total spend ranking across all selected seasons",
    )
    fig_rank.update_traces(texttemplate="%{text:.1f} Cr", textposition="outside")
    fig_rank.update_layout(
        yaxis_title="", xaxis_title="Total Spend (Rs Cr)",
        margin=dict(t=50, b=10, r=60), height=380,
        showlegend=False, coloraxis_showscale=False,
    )
    st.plotly_chart(fig_rank, use_container_width=True)

st.divider()

# ── Role mix stacked bar ──────────────────────────────────────────────────────
section_header(
    "Role philosophy per franchise",
    "How each team split their budget across Batsmen, Bowlers, All-Rounders, and Wicket Keepers"
)

role_mix = (
    fdf.groupby(["team", "role"])["amount"].sum().reset_index()
    .assign(**{"Spend (Rs Cr)": lambda d: (d["amount"] / 1e7).round(2)})
)
fig_stack = px.bar(
    role_mix, x="team", y="Spend (Rs Cr)", color="role",
    barmode="stack",
    color_discrete_map=ROLE_COLORS,
    title="Some teams bet heavily on batsmen — others balanced their spend across roles",
    labels={"team": "", "Spend (Rs Cr)": "Spend (Rs Cr)", "role": "Role"},
)
fig_stack.update_layout(
    xaxis_tickangle=-35, yaxis_title="Spend (Rs Cr)",
    legend_title="Role", margin=dict(t=50, b=80), height=430,
)
st.plotly_chart(fig_stack, use_container_width=True)
