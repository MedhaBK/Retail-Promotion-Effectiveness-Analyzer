import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    base_dir  = os.path.dirname(base_dir)
    base_dir  = os.path.dirname(base_dir)
    data_path = os.path.join(base_dir, 'data', 'cleaned_data.csv')

    df = pd.read_csv(data_path, parse_dates=['Date'])

    # Guard — only map cluster names if column exists
    if 'cluster' not in df.columns:
        st.error("cleaned_data.csv is missing the 'cluster' column. "
                 "Please run the segmentation notebook and save.")
        st.stop()

    df['cluster'] = df['cluster'].astype(int)

    cluster_names = {
        0: "High-Volume Urban",
        1: "Mid-Size Stable",
        2: "Small Price-Sensitive",
        3: "Specialty/Niche"
    }
    df['cluster_name'] = df['cluster'].map(cluster_names).fillna(
        df['cluster'].astype(str)
    )

    return df


@st.cache_data
def load_store_profiles():
    """
    Build store-level aggregate profile from cleaned data.
    Used in segmentation and insights pages.
    """
    df = load_data()

    store_profile = df.groupby('Store').agg(
        avg_sales        = ('Sales', 'mean'),
        median_sales     = ('Sales', 'median'),
        std_sales        = ('Sales', 'std'),
        total_sales      = ('Sales', 'sum'),
        promo_rate       = ('Promo', 'mean'),
        competition_dist = ('CompetitionDistance', 'first'),
        store_type       = ('StoreType', 'first'),
        assortment       = ('Assortment', 'first'),
        cluster          = ('cluster', 'first'),
        cluster_name     = ('cluster_name', 'first'),
    ).reset_index()

    store_profile['sales_cv'] = (
        store_profile['std_sales'] / store_profile['avg_sales']
    )

    return store_profile