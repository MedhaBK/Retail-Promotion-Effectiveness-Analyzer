import streamlit as st
import pandas as pd
from utils.data_loader import load_data, load_store_profiles
from utils.metrics import compute_promo_metrics


def show():
    df            = load_data()
    store_profile = load_store_profiles()
    promo_df      = compute_promo_metrics(df)

    st.markdown("""
    <div style='margin-bottom:24px;'>
        <h1 style='font-size:26px; font-weight:700;
                   color:#e6edf3; margin:0;'>
            Business Insights
        </h1>
        <p style='color:#8b949e; margin:4px 0 0;'>
            Key findings and strategic recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-generated findings ──────────────────────────────────
    best_cluster  = promo_df.loc[promo_df['lift_pct'].idxmax()]
    worst_cluster = promo_df.loc[promo_df['lift_pct'].idxmin()]
    overall_lift  = (
        df[df['Promo']==1]['Sales'].mean() /
        df[df['Promo']==0]['Sales'].mean() - 1
    ) * 100

    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>📌 Key Findings</h3>",
        unsafe_allow_html=True
    )

    findings = [
        (
            "🏆 Highest Promotion Response",
            f"**{best_cluster['cluster_name']}** stores show the "
            f"strongest promotion lift at "
            f"**+{best_cluster['lift_pct']:.1f}%** average sales "
            f"increase on promotion days across "
            f"{best_cluster['store_count']} stores.",
            "#3fb950"
        ),
        (
            "⚠️ Lowest Promotion Response",
            f"**{worst_cluster['cluster_name']}** stores show the "
            f"weakest promotion response at "
            f"**{worst_cluster['lift_pct']:+.1f}%** lift — "
            f"suggesting promotions in this segment may need "
            f"redesign or reallocation.",
            "#d29922"
        ),
        (
            "📊 Overall Promotion Impact",
            f"Across all {df['Store'].nunique()} stores, promotion "
            f"days yield an average **{overall_lift:+.1f}% sales lift** "
            f"compared to non-promotion days. Promotion coverage "
            f"stands at **{df['Promo'].mean():.1%}** of open store-days.",
            "#58a6ff"
        ),
        (
            "🏪 Store Type Concentration",
            f"Store Type B accounts for the smallest segment but "
            f"exhibits structurally distinct sales patterns — "
            f"sufficient to form an isolated cluster requiring "
            f"separate promotional strategy.",
            "#bc8cff"
        ),
        (
            "📅 Seasonal Concentration Risk",
            f"Sales peak sharply in December and dip in "
            f"July–August across all clusters. "
            f"Promotions running during peak seasons will "
            f"overstate effectiveness — segment-level analysis "
            f"controls for this pattern.",
            "#58a6ff"
        ),
    ]

    for title, body, color in findings:
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #30363d;
                    border-left: 3px solid {color};
                    border-radius:8px; padding:16px 20px;
                    margin-bottom:12px;'>
            <div style='font-size:14px; font-weight:600;
                        color:#e6edf3; margin-bottom:6px;'>
                {title}
            </div>
            <div style='font-size:13px; color:#c9d1d9;
                        line-height:1.6;'>
                {body}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Recommendations ──────────────────────────────────────────
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>💡 Strategic Recommendations</h3>",
        unsafe_allow_html=True
    )

    recs = [
        ("Concentrate promotion spend on high-lift clusters",
         f"Shift budget toward {best_cluster['cluster_name']} stores "
         f"which consistently demonstrate the highest incremental "
         f"response to Promo 1."),
        ("Redesign promotions for low-response segments",
         f"{worst_cluster['cluster_name']} stores show weak or "
         f"marginal lift — test alternative promotion mechanics "
         f"(e.g. loyalty rewards vs. discount depth) before "
         f"committing full budget."),
        ("Separate strategy for Type B stores",
         "Type B stores are structurally distinct — they should "
         "not be benchmarked against Type A/C/D stores. A dedicated "
         "promotion calendar for this segment is recommended."),
        ("Control for seasonality in promotion evaluation",
         "Use same-period year-over-year comparisons or control "
         "groups when reporting promotion effectiveness to "
         "leadership — raw lift figures overstate impact during "
         "December and understate it during summer."),
    ]

    for i, (title, body) in enumerate(recs, 1):
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #30363d;
                    border-radius:8px; padding:16px 20px;
                    margin-bottom:10px; display:flex; gap:16px;'>
            <div style='font-size:22px; font-weight:700;
                        color:#30363d; min-width:28px;'>
                {i:02d}
            </div>
            <div>
                <div style='font-size:14px; font-weight:600;
                            color:#e6edf3; margin-bottom:4px;'>
                    {title}
                </div>
                <div style='font-size:13px; color:#8b949e;
                            line-height:1.6;'>
                    {body}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:24px 0;'>", unsafe_allow_html=True)

    # ── Methodology note ─────────────────────────────────────────
    st.markdown(
        "<h3 style='font-size:15px; color:#e6edf3; "
        "margin-bottom:16px;'>📋 Methodology Notes</h3>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style='background:#161b22; border:1px solid #30363d;
                border-radius:8px; padding:20px;
                font-size:13px; color:#8b949e; line-height:1.8;'>
        <b style='color:#c9d1d9;'>Dataset:</b>
        Rossmann Store Sales — 1,017,209 open store-days across
        1,115 stores, January 2013 to July 2015.<br><br>
        <b style='color:#c9d1d9;'>Clustering:</b>
        K-Means on store-level behavioral features
        (avg sales, promo rate, competition distance, sales volatility,
        store type). Optimal k selected via elbow method and
        silhouette score. Store Type B formed an isolated cluster
        (n=17) and was excluded from comparative analysis.<br><br>
        <b style='color:#c9d1d9;'>Promotion lift:</b>
        Descriptive comparison of average daily sales on promotion
        vs non-promotion days within each cluster. Figures reflect
        correlation, not causation — seasonal confounding
        is acknowledged as a limitation.<br><br>
        <b style='color:#c9d1d9;'>Exclusions:</b>
        Closed store-days (Open=0) removed before all analysis.
        Stores with >30% zero-sale open days flagged as suspicious
        and excluded from cluster-level comparisons.
    </div>
    """, unsafe_allow_html=True)