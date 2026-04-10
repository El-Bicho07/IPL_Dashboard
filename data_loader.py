import pandas as pd
import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

# ── Global Plotly theme ───────────────────────────────────────────────────────
pio.templates["ipl"] = pio.templates["plotly_dark"]
pio.templates["ipl"].layout.paper_bgcolor  = "rgba(0,0,0,0)"
pio.templates["ipl"].layout.plot_bgcolor   = "rgba(0,0,0,0)"
pio.templates["ipl"].layout.font           = dict(family="monospace", color="#edeef2")
pio.templates["ipl"].layout.title.font     = dict(family="monospace", color="#edeef2", size=14)
pio.templates["ipl"].layout.xaxis          = dict(
    gridcolor="rgba(255,255,255,0.05)",
    linecolor="rgba(255,255,255,0.1)",
    tickcolor="rgba(255,255,255,0.1)",
)
pio.templates["ipl"].layout.yaxis          = dict(
    gridcolor="rgba(255,255,255,0.05)",
    linecolor="rgba(255,255,255,0.1)",
    tickcolor="rgba(255,255,255,0.1)",
)
pio.templates["ipl"].layout.legend         = dict(
    bgcolor="rgba(0,0,0,0)",
    bordercolor="rgba(255,255,255,0.08)",
    borderwidth=1,
)
pio.templates.default = "ipl"

# ── Team metadata ─────────────────────────────────────────────────────────────
TEAM_SHORT = {
    "Mumbai Indians":                "MI",
    "Chennai Super Kings":           "CSK",
    "Royal Challengers Bangalore":   "RCB",
    "Kolkata Knight Riders":         "KKR",
    "Sunrisers Hyderabad":           "SRH",
    "Rajasthan Royals":              "RR",
    "Delhi Capitals":                "DC",
    "Kings XI Punjab":               "KXIP",
    "Gujarat Lions":                 "GL",
    "Rising Pune Supergiant":        "RPS",
    "Pune Warriors":                 "PWI",
    "Kochi Tuskers Kerala":          "KTK",
    "Deccan Chargers":               "DC2",
    "Delhi Daredevils":              "DD",
}

TEAMS_2022_ACTIVE = [
    "Mumbai Indians",
    "Chennai Super Kings",
    "Royal Challengers Bangalore",
    "Kolkata Knight Riders",
    "Sunrisers Hyderabad",
    "Rajasthan Royals",
    "Delhi Capitals",
    "Kings XI Punjab",
    "Gujarat Titans",
    "Lucknow Super Giants",
]

TEAM_TIMELINE = {
    "Deccan Chargers":               "2008-2012 (dissolved)",
    "Kochi Tuskers Kerala":          "2011 only (dissolved)",
    "Pune Warriors India":           "2011-2013 (dissolved)",
    "Gujarat Lions":                 "2016-2017 (temporary replacement franchise)",
    "Rising Pune Supergiant":        "2016-2017 (temporary replacement franchise)",
    "Delhi Daredevils":              "2008-2019 (rebranded to Delhi Capitals in 2020)",
    "Delhi Capitals":                "2020-present",
    "Kings XI Punjab":               "2008-present (rebranded to Punjab Kings in 2021)",
    "Chennai Super Kings":           "2008-present (suspended 2016-2017)",
    "Rajasthan Royals":              "2008-present (suspended 2016-2017)",
    "Mumbai Indians":                "2008-present",
    "Kolkata Knight Riders":         "2008-present",
    "Royal Challengers Bangalore":   "2008-present",
    "Sunrisers Hyderabad":           "2013-present",
    "Gujarat Titans":                "2022-present (not in dataset)",
    "Lucknow Super Giants":          "2022-present (not in dataset)",
}

ROLE_COLORS = {
    "Batsman":       "#f0b429",
    "Bowler":        "#2dd4bf",
    "All-Rounder":   "#f97066",
    "Wicket Keeper": "#a78bfa",
}

ORIGIN_COLORS = {
    "Indian":   "#2dd4bf",
    "Overseas": "#f97066",
}

# ── Shared CSS ────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
    [data-testid="stSidebar"] { min-width: 240px; max-width: 260px; }
    [data-testid="stMetric"] {
        background: #13161e;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 18px 20px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #8b8fa8 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 600;
        color: #edeef2 !important;
    }
    hr { border-color: rgba(255,255,255,0.07) !important; }
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        overflow: hidden;
    }
    [data-testid="stAlert"] { border-radius: 10px; font-size: 13px; }
    [data-testid="stSidebar"] label {
        font-size: 11px !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #8b8fa8 !important;
    }
</style>
"""

def section_header(title: str, subtitle: str = ""):
    """Gold left-border section header used consistently across all pages."""
    sub_html = (
        f"<div style='font-size:12px; color:#8b8fa8; margin-top:3px;'>{subtitle}</div>"
        if subtitle else ""
    )
    st.markdown(
        f"""
        <div style='padding-left:14px; border-left:3px solid #f0b429; margin:8px 0 16px 0;'>
            <span style='font-size:12px; letter-spacing:0.12em; text-transform:uppercase;
                         color:#8b8fa8; font-family:monospace;'>{title}</span>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

@st.cache_data
def load_data():
    df = pd.read_csv("data/ipl_feature_engineered_dataset.csv")
    return df

@st.cache_data
def get_filtered(year_min, year_max, origins, roles):
    df = load_data()
    mask = (
        (df["year"] >= year_min) &
        (df["year"] <= year_max) &
        (df["player_origin"].isin(list(origins))) &
        (df["role"].isin(list(roles)))
    )
    return df[mask].copy()
