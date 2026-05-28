import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data
from utils.metrics import compute_promo_metrics, compute_promo2_metrics
from utils.visualizations import promo_lift_by_cluster, dow_sales_chart, _base_layout


def show():
    df         = load_data()
    promo_df   = compute_promo_metrics(df)
    promo2_df  = compute_promo2_metrics(df)

    st.markdown("""
    <div style='margin-bottom:24px;'>
        <h1 style='font-size:26px; font-weight:700;
                   color:#e6edf3; margin:0;'>
            Promotion Analysis
        </h1>
        <p style='color:#8b949e; margin:4px 0 0;'>
            Sales lift by store cluster, promotion type, and timing
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Cluster-level promo lift KPIs ───────────────────────────
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>Promo 1 — Lift by Store Cluster</h3>",
        unsafe_allow_html=True
    )

    cols = st.columns(len(promo_df))
    colors = {"positive": "#3fb950", "negative": "#f85149",
              "neutral": "#d29922"}

    for i, (_, row) in enumerate(promo_df.iterrows()):
        with cols[i]:
            color = colors["positive"] if row['lift_pct'] > 0 \
                    else colors["negative"]
            st.markdown(f"""
            <div style='background:#161b22; border:1px solid #30363d;
                        border-radius:8px; padding:16px; text-align:center;'>
                <div style='font-size:12px; color:#8b949e;
                            text-transform:uppercase;
                            letter-spacing:0.05em; margin-bottom:8px;'>
                    {row['cluster_name']}
                </div>
                <div style='font-size:28px; font-weight:700;
                            color:{color};'>
                    {row['lift_pct']:+.1f}%
                </div>
                <div style='font-size:12px; color:#8b949e; margin-top:4px;'>
                    {row['store_count']} stores
                </div>
                <div style='font-size:11px; color:#8b949e; margin-top:2px;'>
                    Base: €{row['base_sales']:,.0f} →
                    Promo: €{row['promo_sales']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Lift chart ───────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.plotly_chart(
            promo_lift_by_cluster(promo_df),
            use_container_width=True
        )

    with col2:
        st.markdown(
            "<h3 style='font-size:15px; color:#e6edf3; "
            "margin-bottom:12px;'>Cluster Summary Table</h3>",
            unsafe_allow_html=True
        )
        display_df = promo_df[[
            'cluster_name', 'base_sales',
            'promo_sales', 'lift_pct', 'store_count'
        ]].copy()
        display_df.columns = [
            'Cluster', 'Base Sales (€)',
            'Promo Sales (€)', 'Lift %', 'Stores'
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Day of week analysis ─────────────────────────────────────
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>Promotion Timing — Day of Week</h3>",
        unsafe_allow_html=True
    )
    st.plotly_chart(dow_sales_chart(df), use_container_width=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Promo2 section if available ──────────────────────────────
    if not promo2_df.empty:
        st.markdown(
            "<h3 style='font-size:15px; color:#e6edf3; "
            "margin-bottom:16px;'>Promo 2 — Continuous Promotion "
            "Lift by Cluster</h3>",
            unsafe_allow_html=True
        )
        fig = go.Figure(go.Bar(
            x=promo2_df['cluster_name'],
            y=promo2_df['lift_pct'],
            marker_color=[
                "#3fb950" if x > 0 else "#f85149"
                for x in promo2_df['lift_pct']
            ],
            text=promo2_df['lift_pct'].apply(lambda x: f"{x:+.1f}%"),
            textposition='outside',
            textfont=dict(color="#c9d1d9")
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#8b949e")
        fig = _base_layout(fig, "Promo 2 Sales Lift by Cluster (%)")
        st.plotly_chart(fig, use_container_width=True)

    # ── Cluster filter: drill down ───────────────────────────────
    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>Drill Down by Cluster</h3>",
        unsafe_allow_html=True
    )

    cluster_options = sorted(df['cluster_name'].unique())
    selected        = st.selectbox("Select store cluster", cluster_options)
    cdf             = df[df['cluster_name'] == selected]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Stores in Cluster",
                  cdf['Store'].nunique())
    with c2:
        st.metric("Avg Sales — No Promo",
                  f"€{cdf[cdf['Promo']==0]['Sales'].mean():,.0f}")
    with c3:
        st.metric("Avg Sales — Promo",
                  f"€{cdf[cdf['Promo']==1]['Sales'].mean():,.0f}")

    # Weekly trend for selected cluster
    weekly = cdf.groupby(
        [pd.Grouper(key='Date', freq='W'), 'Promo']
    )['Sales'].mean().reset_index()

    fig2 = go.Figure()
    for promo_val, label, color in [
        (0, "No Promotion", "#58a6ff"),
        (1, "Promotion",    "#3fb950")
    ]:
        sub = weekly[weekly['Promo'] == promo_val]
        fig2.add_trace(go.Scatter(
            x=sub['Date'], y=sub['Sales'],
            mode='lines', name=label,
            line=dict(color=color, width=1.8)
        ))
    fig2 = _base_layout(
        fig2,
        f"Weekly Sales Trend — {selected}"
    )
    st.plotly_chart(fig2, use_container_width=True)