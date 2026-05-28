import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import load_data
from utils.metrics import compute_executive_kpis
from utils.visualizations import (
    temporal_sales_trend,
    promo_vs_nopromo_box,
    sales_by_storetype
)


def show():
    df   = load_data()
    kpis = compute_executive_kpis(df)

    # ── Page header ─────────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:24px;'>
        <h1 style='font-size:26px; font-weight:700;
                   color:#e6edf3; margin:0;'>
            Executive Overview
        </h1>
        <p style='color:#8b949e; margin:4px 0 0;'>
            Rossmann Store Sales · 1,115 Stores · 2013–2015
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI cards ────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Total Revenue",
            f"€{kpis['total_sales']/1e9:.2f}B"
        )
    with c2:
        st.metric(
            "Stores Analyzed",
            f"{kpis['total_stores']:,}"
        )
    with c3:
        st.metric(
            "Avg Daily Revenue",
            f"€{kpis['avg_daily_sales']:,.0f}"
        )
    with c4:
        st.metric(
            "Promotion Coverage",
            f"{kpis['promo_coverage']:.1f}%",
            help="% of open store-days with a promotion active"
        )
    with c5:
        st.metric(
            "Raw Promo Lift",
            f"+{kpis['raw_promo_lift']:.1f}%",
            delta="vs non-promo days",
            help="Unadjusted average sales lift on promotion days"
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Charts row 1 ─────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.plotly_chart(
            temporal_sales_trend(df),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            promo_vs_nopromo_box(df),
            use_container_width=True
        )

    # ── Charts row 2 ─────────────────────────────────────────────
    col3, col4 = st.columns([2, 3])

    with col3:
        st.plotly_chart(
            sales_by_storetype(df),
            use_container_width=True
        )

    with col4:
        # Promo vs No-Promo summary table
        st.markdown(
            "<h3 style='font-size:15px; color:#e6edf3; "
            "margin-bottom:12px;'>Promotion Impact Summary</h3>",
            unsafe_allow_html=True
        )
        summary_data = {
            "Metric": [
                "Avg Sales — No Promotion",
                "Avg Sales — With Promotion",
                "Absolute Lift per Store-Day",
                "Relative Lift",
                "Days with Promotion",
                "Days without Promotion",
            ],
            "Value": [
                f"€{kpis['no_promo_avg_sales']:,.0f}",
                f"€{kpis['promo_avg_sales']:,.0f}",
                f"€{kpis['promo_avg_sales'] - kpis['no_promo_avg_sales']:,.0f}",
                f"+{kpis['raw_promo_lift']:.1f}%",
                f"{(df['Promo']==1).sum():,}",
                f"{(df['Promo']==0).sum():,}",
            ]
        }
        import pandas as pd
        st.dataframe(
            pd.DataFrame(summary_data),
            use_container_width=True,
            hide_index=True
        )

    # ── Methodology note ────────────────────────────────────────
    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)
    st.info(
        "**Note on lift figures:** The raw promotion lift shown here "
        "is a descriptive comparison of average sales on promotion vs "
        "non-promotion days. It does not control for seasonality or "
        "pre-existing trends. Cluster-level analysis on the Promotion "
        "Analysis page provides a more granular breakdown by store segment."
    )