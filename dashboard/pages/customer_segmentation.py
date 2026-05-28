import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data, load_store_profiles
from utils.visualizations import cluster_scatter, cluster_profile_radar, _base_layout


def show():
    df            = load_data()
    store_profile = load_store_profiles()

    st.markdown("""
    <div style='margin-bottom:24px;'>
        <h1 style='font-size:26px; font-weight:700;
                   color:#e6edf3; margin:0;'>
            Customer Segmentation
        </h1>
        <p style='color:#8b949e; margin:4px 0 0;'>
            Store clusters — behavioral profiles and characteristics
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Cluster size cards ───────────────────────────────────────
    cluster_counts = store_profile.groupby(
        ['cluster', 'cluster_name']
    ).size().reset_index(name='count')

    cols = st.columns(len(cluster_counts))
    cluster_colors = ["#58a6ff", "#3fb950", "#d29922", "#bc8cff"]

    for i, (_, row) in enumerate(cluster_counts.iterrows()):
        with cols[i]:
            color = cluster_colors[i % len(cluster_colors)]
            pct   = row['count'] / len(store_profile) * 100
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d;
                        border-radius:8px; padding:16px; text-align:center;'>
                <div style='font-size:11px; color:#8b949e;
                            text-transform:uppercase;
                            letter-spacing:0.05em; margin-bottom:6px;'>
                    Cluster {int(row['cluster'])}
                </div>
                <div style='font-size:26px; font-weight:700;
                            color:{color};'>
                    {row['count']}
                </div>
                <div style='font-size:12px; color:#8b949e;'>
                    stores ({pct:.1f}%)
                </div>
                <div style='font-size:12px; color:#e6edf3;
                            margin-top:4px; font-weight:500;'>
                    {row['cluster_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Scatter + Radar ──────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            cluster_scatter(store_profile),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            cluster_profile_radar(store_profile),
            use_container_width=True
        )

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Cluster comparison table ─────────────────────────────────
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>Cluster Attribute Comparison</h3>",
        unsafe_allow_html=True
    )

    summary = store_profile.groupby('cluster_name').agg(
        Stores          = ('Store', 'count'),
        Avg_Sales       = ('avg_sales', 'mean'),
        Median_Sales    = ('median_sales', 'mean'),
        Promo_Rate      = ('promo_rate', 'mean'),
        Avg_Competition = ('competition_dist', 'mean'),
        Sales_Volatility = ('sales_cv', 'mean'),
    ).round(2).reset_index()

    summary['Avg_Sales']       = summary['Avg_Sales'].apply(
        lambda x: f"€{x:,.0f}")
    summary['Median_Sales']    = summary['Median_Sales'].apply(
        lambda x: f"€{x:,.0f}")
    summary['Promo_Rate']      = summary['Promo_Rate'].apply(
        lambda x: f"{x:.1%}")
    summary['Avg_Competition'] = summary['Avg_Competition'].apply(
        lambda x: f"{x:,.0f}m")
    summary['Sales_Volatility'] = summary['Sales_Volatility'].apply(
        lambda x: f"{x:.2f}")

    summary.columns = [
        'Cluster', 'Stores', 'Avg Daily Sales',
        'Median Daily Sales', 'Promo Rate',
        'Avg Competition Dist', 'Sales Volatility (CV)'
    ]
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Store type distribution per cluster ──────────────────────
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>Store Type Distribution by Cluster</h3>",
        unsafe_allow_html=True
    )

    type_dist = store_profile.groupby(
        ['cluster_name', 'store_type']
    ).size().reset_index(name='count')

    fig = go.Figure()
    for stype in sorted(type_dist['store_type'].unique()):
        subset = type_dist[type_dist['store_type'] == stype]
        fig.add_trace(go.Bar(
            x=subset['cluster_name'],
            y=subset['count'],
            name=f"Type {stype}",
        ))
    fig.update_layout(barmode='stack')
    fig = _base_layout(fig, "Store Type Composition per Cluster")
    st.plotly_chart(fig, use_container_width=True)