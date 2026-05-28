import streamlit as st

st.set_page_config(
    page_title="Retail Promotion Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Global dark corporate styling ──────────────────────────────
st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
}
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
}
[data-testid="metric-container"] label {
    color: #8b949e !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e6edf3 !important;
    font-size: 28px !important;
    font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 13px !important;
}

/* Section headers */
h1, h2, h3 {
    color: #e6edf3 !important;
}
p, li {
    color: #c9d1d9 !important;
}

/* Divider */
hr {
    border-color: #30363d;
}

/* Selectbox / dropdown */
[data-testid="stSelectbox"] > div > div {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #c9d1d9;
}

/* Tab styling */
[data-testid="stTabs"] button {
    color: #8b949e !important;
    font-weight: 500;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
    border-radius: 6px;
}

/* Info / warning boxes */
[data-testid="stAlert"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 8px 0 24px 0;'>
        <div style='font-size:20px; font-weight:700;
                    color:#e6edf3; letter-spacing:0.02em;'>
            Retail Promo
        </div>
        <div style='font-size:12px; color:#8b949e;
                    margin-top:4px;'>
            Promotion Effectiveness Analyzer
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:11px; font-weight:600; "
        "color:#8b949e; letter-spacing:0.08em; "
        "text-transform:uppercase; margin-bottom:8px;'>"
        "Navigation</div>",
        unsafe_allow_html=True
    )

    pages = {
        "Executive Overview":    "",
        "Promotion Analysis":    "",
        "Customer Segmentation": "",
        "Sales Trends":          "",
        "Business Insights":     "",
    }

    if "page" not in st.session_state:
        st.session_state.page = "Executive Overview"

    for page_name, icon in pages.items():
        is_active = st.session_state.page == page_name
        btn_style = (
            "background-color:#21262d; border:1px solid #58a6ff; "
            "color:#58a6ff;"
            if is_active else
            "background-color:transparent; border:1px solid transparent; "
            "color:#8b949e;"
        )
        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("<hr style='margin:24px 0 16px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:11px; color:#8b949e;'>"
        "Dataset: Rossmann Store Sales<br>"
        "Stores: 1,115 | Period: 2013–2015"
        "</div>",
        unsafe_allow_html=True
    )

# ── Route to page ───────────────────────────────────────────────
page = st.session_state.page

if page == "Executive Overview":
    from pages.executive_overview import show
    show()
elif page == "Promotion Analysis":
    from pages.promotion_analysis import show
    show()
elif page == "Customer Segmentation":
    from pages.customer_segmentation import show
    show()
elif page == "Sales Trends":
    from pages.sales_trends import show
    show()
elif page == "Business Insights":
    from pages.business_insights import show
    show()