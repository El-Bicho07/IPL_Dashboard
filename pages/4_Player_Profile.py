import streamlit as st
import plotly.express as px
from data_loader import load_data, ROLE_COLORS, GLOBAL_CSS, section_header

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
df = load_data()

st.markdown("""
<div style='padding:8px 0 4px 0;'>
    <span style='font-size:24px; font-weight:700;'>Player Profile</span><br/>
    <span style='font-size:12px; color:#8b8fa8; letter-spacing:0.08em;'>
        SEARCH ANY PLAYER TO TRACE THEIR COMPLETE IPL AUCTION JOURNEY.
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("### About this page")
    st.info(
        "Search and select a player. Players who appeared in multiple auctions "
        "show a full price timeline and team-by-team history.",
        icon="ℹ️",
    )

selected = st.selectbox(
    "Search player",
    options=[""] + sorted(df["player"].unique()),
    index=0,
    format_func=lambda x: "Type a player name..." if x == "" else x,
)

if not selected:
    st.info("Search and select a player above to see their profile.")
    st.stop()

pdf = df[df["player"] == selected].sort_values("year").copy()
pdf["Amount (Rs Cr)"] = (pdf["amount"] / 1e7).round(2)

timeline_df = (
    pdf.groupby(["year", "team"])
    .agg({"amount": "max", "role": "first"})
    .reset_index()
)
timeline_df["Amount (Rs Cr)"] = (timeline_df["amount"] / 1e7).round(2)

# ── Player name + KPIs ────────────────────────────────────────────────────────
st.markdown(
    f"<div style='font-size:22px; font-weight:700; margin-bottom:4px;'>{selected}</div>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Appearances",   len(pdf))
k2.metric("Teams",          pdf["team"].nunique())
k3.metric("Peak Price",     f"Rs {pdf['amount'].max()/1e7:.2f} Cr")
k4.metric("Origin",         pdf["player_origin"].iloc[0])
k5.metric("Last Sold To",   pdf.sort_values("year").iloc[-1]["team"])

st.divider()

# ── Career journey banner ─────────────────────────────────────────────────────
journey = timeline_df.sort_values("year")[["year", "team"]].values.tolist()
journey_str = "  &rarr;  ".join(
    [f"<span style='color:#f0b429; font-weight:600;'>{t}</span> "
     f"<span style='color:#8b8fa8;'>({int(y)})</span>" for y, t in journey]
)
st.markdown(
    f"<div style='font-size:13px; padding:10px 14px; background:#13161e; "
    f"border-radius:8px; border:1px solid rgba(255,255,255,0.07); margin-bottom:16px;'>"
    f"<span style='font-size:10px; color:#8b8fa8; letter-spacing:0.1em;'>CAREER JOURNEY &nbsp;</span>"
    f"{journey_str}</div>",
    unsafe_allow_html=True,
)

# ── Timeline + History ────────────────────────────────────────────────────────
section_header(
    "Price timeline and auction history",
    "Each point = one auction. Color = buying team. Table shows full raw record."
)

left, right = st.columns([3, 2])

with left:
    teams_in = timeline_df["team"].unique().tolist()
    color_seq = ["#f0b429","#2dd4bf","#f97066","#a78bfa","#60a5fa","#34d399","#fb923c","#e879f9"]
    team_color_map = {t: color_seq[i % len(color_seq)] for i, t in enumerate(teams_in)}

    fig = px.line(
        timeline_df, x="year", y="Amount (Rs Cr)", color="team",
        markers=True, color_discrete_map=team_color_map,
        hover_data=["role"],
        title=f"How {selected}'s auction value changed across seasons",
        labels={"year": "Year", "Amount (Rs Cr)": "Amount (Rs Cr)", "team": "Team"},
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=10))
    fig.update_layout(
        xaxis=dict(tickmode="linear", dtick=1),
        height=380, margin=dict(t=50, b=20), legend_title="Team",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    display = pdf[["year","team","Amount (Rs Cr)","role","player_origin"]].copy()
    display.columns = ["Year","Team","Amount (Rs Cr)","Role","Origin"]
    display = display.sort_values("Year", ascending=False).reset_index(drop=True)

    st.dataframe(
        display, hide_index=True, use_container_width=True, height=360,
        column_config={
            "Amount (Rs Cr)": st.column_config.NumberColumn("Amount (Rs Cr)", format="%.2f Cr"),
            "Year": st.column_config.NumberColumn("Year", format="%d"),
        },
    )

# ── Price delta ───────────────────────────────────────────────────────────────
if len(timeline_df) >= 2:
    st.divider()
    first = timeline_df.sort_values("year").iloc[0]["Amount (Rs Cr)"]
    last  = timeline_df.sort_values("year").iloc[-1]["Amount (Rs Cr)"]
    delta = last - first
    pct   = (delta / first * 100) if first > 0 else 0
    arrow = "up" if delta >= 0 else "down"
    color = "#2dd4bf" if delta >= 0 else "#f97066"
    word  = "increased" if delta >= 0 else "decreased"

    st.markdown(
        f"<div style='padding:12px 16px; background:#13161e; border-radius:8px; "
        f"border-left:3px solid {color}; font-size:13px;'>"
        f"<b>Price movement:</b> {selected}'s auction value <b style='color:{color};'>{word}</b> "
        f"from <b>Rs {first:.2f} Cr</b> to <b>Rs {last:.2f} Cr</b> "
        f"(<b style='color:{color};'>{'+' if delta>=0 else ''}{pct:.1f}%</b>) "
        f"across their recorded auction history.</div>",
        unsafe_allow_html=True,
    )
