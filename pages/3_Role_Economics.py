import streamlit as st
import plotly.express as px
from data_loader import load_data, ROLE_COLORS, ORIGIN_COLORS, GLOBAL_CSS, section_header

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
df = load_data()

st.markdown("""
<div style='padding:8px 0 4px 0;'>
    <span style='font-size:24px; font-weight:700;'>Role Economics</span><br/>
    <span style='font-size:12px; color:#8b8fa8; letter-spacing:0.08em;'>
        WHAT A PLAYER DOES ON THE FIELD DETERMINES WHAT TEAMS WILL PAY AT AUCTION.
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("### Filters")
    year_range = st.slider("Year range", int(df["year"].min()), int(df["year"].max()), (2013, 2022))
    origins    = st.multiselect("Player origin", sorted(df["player_origin"].unique()), default=sorted(df["player_origin"].unique()))
    roles      = st.multiselect("Role", sorted(df["role"].unique()), default=sorted(df["role"].unique()))

fdf = df[
    (df["year"].between(year_range[0], year_range[1])) &
    (df["player_origin"].isin(origins)) &
    (df["role"].isin(roles))
].copy()

if fdf.empty:
    st.warning("No data matches the current filters.")
    st.stop()

fdf["Amount (Rs Cr)"] = (fdf["amount"] / 1e7).round(2)

# ── Strip plot ────────────────────────────────────────────────────────────────
section_header(
    "Every player as a data point — where does your role put you?",
    "Each dot is one auction entry. Dots clustered near the bottom = most players sell cheap. Outliers tell the real story."
)

fig_strip = px.strip(
    fdf, x="role", y="Amount (Rs Cr)",
    color="role", color_discrete_map=ROLE_COLORS,
    hover_data=["player", "team", "year"],
    stripmode="overlay",
    title="All-Rounders have the widest price spread — highest ceiling, lowest floor",
)
fig_strip.update_traces(jitter=0.4, marker=dict(size=5, opacity=0.65))
fig_strip.update_layout(
    xaxis_title="Role", yaxis_title="Amount (Rs Cr)",
    showlegend=False, height=430, margin=dict(t=50, b=20),
)
st.plotly_chart(fig_strip, use_container_width=True)
st.divider()

# ── Trend line ────────────────────────────────────────────────────────────────
section_header(
    "Which roles became more expensive over time?",
    "Average auction price per role from 2013 to 2022 — upward slope means the market valued that role more over time"
)

trend = (
    fdf.groupby(["year", "role"])["Amount (Rs Cr)"].mean()
    .reset_index()
    .rename(columns={"Amount (Rs Cr)": "Avg Price (Rs Cr)"})
)
trend["Avg Price (Rs Cr)"] = trend["Avg Price (Rs Cr)"].round(2)

fig_trend = px.line(
    trend, x="year", y="Avg Price (Rs Cr)", color="role",
    markers=True, color_discrete_map=ROLE_COLORS,
    title="Batsman and All-Rounder prices climbed fastest — Bowlers remained undervalued",
    labels={"year": "Year", "Avg Price (Rs Cr)": "Avg Price (Rs Cr)", "role": "Role"},
)
fig_trend.update_traces(line=dict(width=2.5), marker=dict(size=7))
fig_trend.update_layout(
    xaxis=dict(tickmode="linear", dtick=1),
    height=410, margin=dict(t=50, b=20), legend_title="Role",
)
st.plotly_chart(fig_trend, use_container_width=True)
st.divider()

# ── Grouped bar ───────────────────────────────────────────────────────────────
section_header(
    "The overseas premium — do foreign players earn more in each role?",
    "Average price by role split between Indian and Overseas players"
)

origin_role = (
    fdf.groupby(["role", "player_origin"])["Amount (Rs Cr)"].mean()
    .reset_index()
    .rename(columns={"Amount (Rs Cr)": "Avg Price (Rs Cr)"})
)
origin_role["Avg Price (Rs Cr)"] = origin_role["Avg Price (Rs Cr)"].round(2)

fig_grp = px.bar(
    origin_role, x="role", y="Avg Price (Rs Cr)", color="player_origin",
    barmode="group", text="Avg Price (Rs Cr)",
    color_discrete_map=ORIGIN_COLORS,
    title="Overseas Wicket Keepers command a significant premium over Indian counterparts",
    labels={"role": "Role", "Avg Price (Rs Cr)": "Avg Price (Rs Cr)", "player_origin": "Origin"},
)
fig_grp.update_traces(texttemplate="%{text:.2f} Cr", textposition="outside")
fig_grp.update_layout(
    xaxis_title="Role", yaxis_title="Avg Price (Rs Cr)",
    legend_title="Origin", height=420, margin=dict(t=50, b=20, r=40),
)
st.plotly_chart(fig_grp, use_container_width=True)
