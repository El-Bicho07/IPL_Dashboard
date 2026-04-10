import streamlit as st
from data_loader import load_data, TEAM_TIMELINE, TEAMS_2022_ACTIVE, GLOBAL_CSS, section_header

st.set_page_config(
    page_title="IPL Auction Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

df = load_data()

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 8px 0 4px 0;'>
    <span style='font-size:28px; font-weight:700; letter-spacing:0.04em;'>
        IPL Player Auction Analytics
    </span><br/>
    <span style='font-size:12px; color:#8b8fa8; letter-spacing:0.1em;'>
        2013 &ndash; 2022 &nbsp;·&nbsp; 970 RECORDS &nbsp;·&nbsp; KAGGLE DATASET
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── KPI cards ─────────────────────────────────────────────────────────────────
section_header("At a Glance", "Full dataset — no filters applied")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Auction Spend",   f"Rs {df['amount'].sum()/1e7:.1f} Cr")
c2.metric("Unique Players",         f"{df['player'].nunique()}")
c3.metric("Teams in Dataset",       f"{df['team'].nunique()}")
c4.metric("Avg. Player Price",      f"Rs {df['amount'].mean()/1e7:.2f} Cr")

st.divider()

# ── Team timeline ─────────────────────────────────────────────────────────────
section_header(
    "Team Active Timeline",
    "GT and LSG entered in 2022 and are not in this dataset. "
    "GL and RPS were temporary 2016-2017 franchises retained as-is."
)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(
        "<div style='font-size:12px; color:#8b8fa8; margin-bottom:10px;'>"
        "ALL FRANCHISES AND THEIR ACTIVE PERIODS</div>",
        unsafe_allow_html=True,
    )
    for team, period in TEAM_TIMELINE.items():
        if "present" in period and "not in dataset" not in period:
            icon = "🟢"
        elif "not in dataset" in period:
            icon = "🔵"
        else:
            icon = "🔴"
        st.markdown(f"{icon} **{team}** — {period}")

with col_b:
    st.markdown(
        "<div style='font-size:12px; color:#8b8fa8; margin-bottom:10px;'>"
        "TEAMS ACTIVE AS OF IPL 2022</div>",
        unsafe_allow_html=True,
    )
    for team in TEAMS_2022_ACTIVE:
        not_in = team in ["Gujarat Titans", "Lucknow Super Giants"]
        badge_color = "#f0b429" if not_in else "#2dd4bf"
        badge_text  = "Not in dataset" if not_in else "In dataset"
        badge_icon  = "⚠" if not_in else "✓"
        st.markdown(
            f"- **{team}** &nbsp;"
            f"<code style='background:{badge_color}22; color:{badge_color}; "
            f"border:1px solid {badge_color}44; border-radius:4px; "
            f"padding:1px 7px; font-size:10px;'>"
            f"{badge_icon} {badge_text}</code>",
            unsafe_allow_html=True,
        )
    st.info(
        "When filtering by team in any page, GT and LSG will not appear "
        "because they have no auction records in the 2013-2022 window."
    )

st.divider()
st.markdown(
    "<p style='color:#50546a; font-size:11px; font-family:monospace;'>"
    "IPL AUCTION DATASET · KAGGLE · 2013-2022 · 970 RECORDS</p>",
    unsafe_allow_html=True,
)
