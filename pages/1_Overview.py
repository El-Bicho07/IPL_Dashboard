import streamlit as st
import plotly.express as px
from data_loader import load_data, ROLE_COLORS, ORIGIN_COLORS, GLOBAL_CSS, section_header

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
df = load_data()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:8px 0 4px 0;'>
    <span style='font-size:24px; font-weight:700;'>Auction Overview</span><br/>
    <span style='font-size:12px; color:#8b8fa8; letter-spacing:0.08em;'>
        WHERE DID THE MONEY GO? A DECADE OF IPL SPENDING AT A GLANCE.
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
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
    st.warning("No data matches the current filters. Adjust the sidebar selections.")
    st.stop()

fdf["Amount (Rs Cr)"] = (fdf["amount"] / 1e7).round(2)

# ── KPI row ───────────────────────────────────────────────────────────────────
section_header("At a Glance", "Filtered totals based on sidebar selections")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Spend",    f"Rs {fdf['amount'].sum()/1e7:.1f} Cr")
k2.metric("Players",         fdf["player"].nunique())
k3.metric("Teams Active",    fdf["team"].nunique())
k4.metric("Avg. Price",      f"Rs {fdf['amount'].mean()/1e7:.2f} Cr")

st.divider()

# ── Row 1: Spend by year + Origin split ───────────────────────────────────────
section_header(
    "Auction inflation: how IPL spending shifted over a decade",
    "Total spend per year alongside Indian vs Overseas composition"
)

col1, col2 = st.columns([2, 1])

with col1:
    yearly = (
        fdf.groupby("year")["amount"].sum()
        .reset_index()
        .assign(**{"Total (Rs Cr)": lambda d: (d["amount"] / 1e7).round(2)})
    )
    fig = px.bar(
        yearly, x="year", y="Total (Rs Cr)",
        title="Auction spend grew nearly 3x from 2013 to 2022",
        text="Total (Rs Cr)",
        color_discrete_sequence=["#f0b429"],
    )
    fig.update_traces(texttemplate="%{text:.1f} Cr", textposition="outside")
    fig.update_layout(
        xaxis=dict(tickmode="linear", dtick=1, title="Year"),
        yaxis_title="Amount (Rs Cr)",
        showlegend=False,
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    origin_counts = fdf["player_origin"].value_counts().reset_index()
    origin_counts.columns = ["Origin", "Count"]
    fig2 = px.pie(
        origin_counts, names="Origin", values="Count",
        title="Overseas players command higher prices — but are fewer in number",
        color="Origin", color_discrete_map=ORIGIN_COLORS, hole=0.45,
    )
    fig2.update_traces(textinfo="percent+label")
    fig2.update_layout(showlegend=False, margin=dict(t=60, b=20))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Row 2: Players per year + Top 5 ───────────────────────────────────────────
section_header(
    "Player volume and top earners",
    "How many players entered each auction — and who commanded the highest bids"
)

col3, col4 = st.columns(2)

with col3:
    players_yr = (
        fdf.groupby("year")["player"].nunique()
        .reset_index()
        .rename(columns={"player": "Unique Players"})
    )
    fig3 = px.line(
        players_yr, x="year", y="Unique Players",
        title="Player pool size fluctuated — dips reflect team suspensions and format changes",
        markers=True,
        color_discrete_sequence=["#a78bfa"],
    )
    fig3.update_traces(line=dict(width=2.5), marker=dict(size=8))
    fig3.update_layout(xaxis=dict(tickmode="linear", dtick=1, title="Year"), margin=dict(t=50, b=20))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    top5 = (
        fdf.groupby("player")["amount"].max().reset_index()
        .sort_values("amount", ascending=False).head(5)
    )
    top5["Amount (Rs Cr)"] = (top5["amount"] / 1e7).round(2)
    top5 = top5.merge(fdf[["player", "role"]].drop_duplicates("player"), on="player", how="left")

    fig4 = px.bar(
        top5.sort_values("Amount (Rs Cr)"),
        x="Amount (Rs Cr)", y="player", orientation="h",
        title="Top 5 most expensive players — all-rounders and batsmen dominate",
        color="role", color_discrete_map=ROLE_COLORS, text="Amount (Rs Cr)",
    )
    fig4.update_traces(texttemplate="%{text:.2f} Cr", textposition="outside")
    fig4.update_layout(
        yaxis_title="", xaxis_title="Amount (Rs Cr)",
        legend_title="Role", margin=dict(t=50, b=20, r=60),
    )
    st.plotly_chart(fig4, use_container_width=True)
