import pandas as pd
import numpy as np


def compute_executive_kpis(df: pd.DataFrame) -> dict:
    total_sales     = df['Sales'].sum()
    avg_daily_sales = df.groupby('Date')['Sales'].sum().mean()
    total_stores    = df['Store'].nunique()
    promo_coverage  = df['Promo'].mean() * 100

    promo_avg    = df[df['Promo'] == 1]['Sales'].mean()
    no_promo_avg = df[df['Promo'] == 0]['Sales'].mean()
    raw_lift_pct = (promo_avg - no_promo_avg) / no_promo_avg * 100

    total_days = df['Date'].nunique()

    return {
        "total_sales":      total_sales,
        "avg_daily_sales":  avg_daily_sales,
        "total_stores":     total_stores,
        "promo_coverage":   promo_coverage,
        "raw_promo_lift":   raw_lift_pct,
        "total_days":       total_days,
        "promo_avg_sales":  promo_avg,
        "no_promo_avg_sales": no_promo_avg,
    }


def compute_promo_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Per-cluster promo vs non-promo comparison."""
    rows = []
    for cluster_id in sorted(df['cluster'].unique()):
        cdf         = df[df['cluster'] == cluster_id]
        name        = cdf['cluster_name'].iloc[0]
        promo_sales = cdf[cdf['Promo'] == 1]['Sales'].mean()
        base_sales  = cdf[cdf['Promo'] == 0]['Sales'].mean()
        lift_pct    = (promo_sales - base_sales) / base_sales * 100
        store_count = cdf['Store'].nunique()

        rows.append({
            'cluster':      cluster_id,
            'cluster_name': name,
            'base_sales':   round(base_sales, 0),
            'promo_sales':  round(promo_sales, 0),
            'lift_pct':     round(lift_pct, 1),
            'store_count':  store_count,
        })

    return pd.DataFrame(rows)


def compute_promo2_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Promo2 effectiveness if column exists."""
    if 'promo2_active' not in df.columns:
        return pd.DataFrame()

    rows = []
    for cluster_id in sorted(df['cluster'].unique()):
        cdf         = df[df['cluster'] == cluster_id]
        name        = cdf['cluster_name'].iloc[0]
        p2_sales    = cdf[cdf['promo2_active'] == 1]['Sales'].mean()
        base_sales  = cdf[cdf['promo2_active'] == 0]['Sales'].mean()

        if pd.isna(p2_sales) or pd.isna(base_sales):
            continue

        lift_pct = (p2_sales - base_sales) / base_sales * 100
        rows.append({
            'cluster':      cluster_id,
            'cluster_name': name,
            'base_sales':   round(base_sales, 0),
            'promo2_sales': round(p2_sales, 0),
            'lift_pct':     round(lift_pct, 1),
        })

    return pd.DataFrame(rows)