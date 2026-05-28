import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data
from utils.visualizations import (
    monthly_trend_chart,
    sales_distribution_chart,
    _base_layout
)


def show():
    df = load_data()

    st.markdown("""
    <div style='margin-bottom:24px;'>
        <h1 style='font-size:26px; font-weight:700;
                   color:#e6edf3; margin:0;'>
            Sales Trends
        </h1>
        <p style='color:#8b949e; margin:4px 0 0;'>
            Temporal patterns, seasonality, and distribution analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        years = sorted(df['Year'].unique())
        selected_year = st.selectbox(
            "Filter by Year",
            ["All Years"] + [str(y) for y in years]
        )
    with col_f2:
        cluster_opts = ["All Clusters"] + sorted(
            df['cluster_name'].unique().tolist()
        )
        selected_cluster = st.selectbox("Filter by Cluster", cluster_opts)
    with col_f3:
        store_type_opts = ["All Types"] + sorted(
            df['StoreType'].unique().tolist()
        )
        selected_type = st.selectbox("Filter by Store Type", store_type_opts)

    # Apply filters
    filtered = df.copy()
    if selected_year != "All Years":
        filtered = filtered[filtered['Year'] == int(selected_year)]
    if selected_cluster != "All Clusters":
        filtered = filtered[filtered['cluster_name'] == selected_cluster]
    if selected_type != "All Types":
        filtered = filtered[filtered['StoreType'] == selected_type]

    # ── KPIs for filtered view ───────────────────────────────────
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Sales (filtered)",
                  f"€{filtered['Sales'].sum()/1e6:.1f}M")
    with c2:
        st.metric("Avg Daily Sales",
                  f"€{filtered['Sales'].mean():,.0f}")
    with c3:
        st.metric("Peak Sales Day",
                  f"€{filtered.groupby('Date')['Sales'].sum().max():,.0f}")
    with c4:
        st.metric("Stores in View",
                  filtered['Store'].nunique())

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Charts ───────────────────────────────────────────────────
    st.plotly_chart(monthly_trend_chart(filtered), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            sales_distribution_chart(filtered),
            use_container_width=True
        )

    with col2:
        # Holiday impact
        holiday_agg = filtered.groupby('is_holiday')['Sales'].mean()
        fig = go.Figure(go.Bar(
            x=["Normal Day", "Holiday Period"],
            y=[
                holiday_agg.get(0, 0),
                holiday_agg.get(1, 0)
            ],
            marker_color=["#58a6ff", "#d29922"],
            text=[
                f"€{holiday_agg.get(0,0):,.0f}",
                f"€{holiday_agg.get(1,0):,.0f}"
            ],
            textposition='outside',
            textfont=dict(color="#c9d1d9")
        ))
        fig = _base_layout(fig, "Average Sales: Holiday vs Normal Days")
        st.plotly_chart(fig, use_container_width=True)

    # ── Year-over-year comparison ────────────────────────────────
    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>Year-over-Year Monthly Comparison</h3>",
        unsafe_allow_html=True
    )

    yoy = df.groupby(['Year', 'Month'])['Sales'].mean().reset_index()
    fig_yoy = go.Figure()
    yoy_colors = ["#58a6ff", "#3fb950", "#d29922"]

    for i, year in enumerate(sorted(yoy['Year'].unique())):
        subset = yoy[yoy['Year'] == year].sort_values('Month')
        fig_yoy.add_trace(go.Scatter(
            x=subset['Month'],
            y=subset['Sales'],
            mode='lines+markers',
            name=str(year),
            line=dict(color=yoy_colors[i % len(yoy_colors)], width=2),
            marker=dict(size=6)
        ))

    fig_yoy.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=['Jan','Feb','Mar','Apr','May','Jun',
                  'Jul','Aug','Sep','Oct','Nov','Dec']
    )
    fig_yoy = _base_layout(fig_yoy, "Monthly Sales by Year", height=400)
    st.plotly_chart(fig_yoy, use_container_width=True)