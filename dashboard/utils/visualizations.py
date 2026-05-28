import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Shared theme ────────────────────────────────────────────────
DARK_TEMPLATE = "plotly_dark"
BG_COLOR      = "#0e1117"
PAPER_COLOR   = "#161b22"
GRID_COLOR    = "#30363d"
ACCENT_BLUE   = "#58a6ff"
ACCENT_GREEN  = "#3fb950"
ACCENT_RED    = "#f85149"
ACCENT_ORANGE = "#d29922"

CLUSTER_COLORS = {
    0: "#58a6ff",
    1: "#3fb950",
    2: "#d29922",
    3: "#bc8cff",
}

def _base_layout(fig, title="", height=420):
    fig.update_layout(
        template=DARK_TEMPLATE,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        title=dict(
            text=title,
            font=dict(size=15, color="#e6edf3"),
            x=0.02
        ),
        height=height,
        margin=dict(l=16, r=16, t=48, b=16),
        font=dict(color="#c9d1d9", size=12),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        legend=dict(
            bgcolor=PAPER_COLOR,
            bordercolor=GRID_COLOR,
            borderwidth=1
        ),
    )
    return fig


def sales_distribution_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df['Sales'],
        nbinsx=80,
        marker_color=ACCENT_BLUE,
        opacity=0.85,
        name="Sales"
    ))
    return _base_layout(fig, "Daily Sales Distribution", height=380)


def promo_vs_nopromo_box(df):
    fig = go.Figure()
    for promo_val, label, color in [
        (0, "No Promotion", ACCENT_BLUE),
        (1, "Promotion Active", ACCENT_GREEN)
    ]:
        fig.add_trace(go.Box(
            y=df[df['Promo'] == promo_val]['Sales'],
            name=label,
            marker_color=color,
            boxmean=True,
            line=dict(width=1.5)
        ))
    return _base_layout(fig, "Sales: Promotion vs No Promotion", height=420)


def temporal_sales_trend(df):
    weekly = df.groupby(
        [pd.Grouper(key='Date', freq='W'), 'Promo']
    )['Sales'].mean().reset_index()

    fig = go.Figure()
    for promo_val, label, color in [
        (0, "No Promotion", ACCENT_BLUE),
        (1, "Promotion Active", ACCENT_GREEN)
    ]:
        subset = weekly[weekly['Promo'] == promo_val]
        fig.add_trace(go.Scatter(
            x=subset['Date'],
            y=subset['Sales'],
            mode='lines',
            name=label,
            line=dict(color=color, width=1.8),
        ))

    return _base_layout(
        fig, "Weekly Average Sales Over Time", height=400
    )


def sales_by_storetype(df):
    agg = df.groupby('StoreType')['Sales'].mean().reset_index()
    agg.columns = ['StoreType', 'AvgSales']
    agg = agg.sort_values('AvgSales', ascending=True)

    fig = go.Figure(go.Bar(
        x=agg['AvgSales'],
        y=agg['StoreType'],
        orientation='h',
        marker_color=ACCENT_BLUE,
        text=agg['AvgSales'].apply(lambda x: f"€{x:,.0f}"),
        textposition='outside',
        textfont=dict(color="#c9d1d9")
    ))
    return _base_layout(fig, "Average Sales by Store Type", height=340)


def promo_lift_by_cluster(promo_df):
    colors = [
        ACCENT_GREEN if x > 0 else ACCENT_RED
        for x in promo_df['lift_pct']
    ]
    fig = go.Figure(go.Bar(
        x=promo_df['cluster_name'],
        y=promo_df['lift_pct'],
        marker_color=colors,
        text=promo_df['lift_pct'].apply(lambda x: f"{x:+.1f}%"),
        textposition='outside',
        textfont=dict(color="#c9d1d9", size=13)
    ))
    fig.add_hline(
        y=0, line_dash="dash",
        line_color="#8b949e",
        annotation_text="No lift baseline",
        annotation_font_color="#8b949e"
    )
    return _base_layout(
        fig, "Promotion Sales Lift by Store Cluster (%)", height=420
    )


def cluster_scatter(store_profile):
    fig = px.scatter(
        store_profile,
        x='competition_dist',
        y='avg_sales',
        color='cluster_name',
        size='promo_rate',
        hover_data=['Store', 'store_type', 'promo_rate'],
        color_discrete_map={
            name: CLUSTER_COLORS.get(cid, "#8b949e")
            for cid, name in store_profile.set_index(
                'cluster')['cluster_name'].to_dict().items()
        },
        labels={
            'competition_dist': 'Competition Distance (m)',
            'avg_sales':        'Average Daily Sales (€)',
            'cluster_name':     'Cluster',
            'promo_rate':       'Promo Rate'
        }
    )
    return _base_layout(
        fig, "Store Clusters: Sales vs Competition Distance", height=460
    )


def cluster_profile_radar(store_profile):
    from sklearn.preprocessing import MinMaxScaler

    agg = store_profile.groupby('cluster_name').agg(
        avg_sales        = ('avg_sales', 'mean'),
        promo_rate       = ('promo_rate', 'mean'),
        competition_dist = ('competition_dist', 'mean'),
        sales_cv         = ('sales_cv', 'mean'),
    ).reset_index()

    scaler = MinMaxScaler()
    dims   = ['avg_sales', 'promo_rate', 'competition_dist', 'sales_cv']
    agg[dims] = scaler.fit_transform(agg[dims])
    # Invert competition_dist — closer competitor = higher score
    agg['competition_dist'] = 1 - agg['competition_dist']

    categories = [
        'Avg Sales', 'Promo Rate',
        'Competition\nProximity', 'Sales Volatility'
    ]

    fig = go.Figure()
    colors = list(CLUSTER_COLORS.values())

    for i, (_, row) in enumerate(agg.iterrows()):
        vals = [
            row['avg_sales'], row['promo_rate'],
            row['competition_dist'], row['sales_cv']
        ]
        vals += [vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories + [categories[0]],
            fill='toself',
            name=row['cluster_name'],
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)].replace(')', ', 0.15)')
                       .replace('rgb', 'rgba')
                       if colors[i].startswith('rgb')
                       else colors[i % len(colors)],
            opacity=0.85
        ))

    fig.update_layout(
        template=DARK_TEMPLATE,
        paper_bgcolor=PAPER_COLOR,
        polar=dict(
            bgcolor=BG_COLOR,
            radialaxis=dict(
                visible=True, range=[0, 1],
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color="#8b949e", size=10)
            ),
            angularaxis=dict(
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color="#c9d1d9", size=11)
            )
        ),
        title=dict(
            text="Cluster Profile Comparison",
            font=dict(size=15, color="#e6edf3"), x=0.02
        ),
        height=460,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor=PAPER_COLOR,
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color="#c9d1d9")
        )
    )
    return fig


def dow_sales_chart(df):
    dow_map = {
        0:'Mon', 1:'Tue', 2:'Wed',
        3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'
    }
    df['DayName'] = df['DayOfWeek'].map(dow_map)
    agg = df.groupby(['DayName', 'Promo'])['Sales'].mean().reset_index()

    fig = go.Figure()
    order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    for promo_val, label, color in [
        (0, "No Promotion", ACCENT_BLUE),
        (1, "Promotion", ACCENT_GREEN)
    ]:
        subset = agg[agg['Promo'] == promo_val]
        subset = subset.set_index('DayName').reindex(order).reset_index()
        fig.add_trace(go.Bar(
            x=subset['DayName'],
            y=subset['Sales'],
            name=label,
            marker_color=color,
        ))

    fig.update_layout(barmode='group')
    return _base_layout(fig, "Sales by Day of Week", height=380)


def monthly_trend_chart(df):
    monthly = df.groupby(['Year', 'Month'])['Sales'].mean().reset_index()
    monthly['period'] = pd.to_datetime(
        monthly[['Year', 'Month']].assign(day=1)
    )
    monthly = monthly.sort_values('period')

    fig = go.Figure(go.Scatter(
        x=monthly['period'],
        y=monthly['Sales'],
        mode='lines+markers',
        line=dict(color=ACCENT_BLUE, width=2),
        marker=dict(size=5, color=ACCENT_BLUE),
        fill='tozeroy',
        fillcolor='rgba(88, 166, 255, 0.08)'
    ))
    return _base_layout(fig, "Monthly Average Sales Trend", height=380)