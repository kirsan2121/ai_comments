import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Define color scheme
COLORS = {
    'positive': '#34A85A',
    'negative': '#FF3737',
    'neutral': '#808080',
    'grid': '#CCCCCC'
}

def format_number(number):
    """Format large numbers with K/M/B suffixes"""
    if pd.isna(number):
        return "0"
    
    if abs(number) >= 1e9:
        return f'{number/1e9:.1f}B'
    if abs(number) >= 1e6:
        return f'{number/1e6:.1f}M'
    if abs(number) >= 1e3:
        return f'{number/1e3:.1f}K'
    return f'{number:.1f}'

def create_sales_comparison_chart(df):
    """Create sales comparison chart for categories"""
    # Агрегация данных по категориям
    category_agg = df.groupby('category_name').agg({
        'current_sales_rub_total': 'sum',
        'previous_sales_rub_total': 'sum',
        'current_sales_kg_total': 'sum',
        'previous_sales_kg_total': 'sum'
    }).reset_index()
    
    # Расчет изменений
    category_agg['sales_rub_change'] = ((category_agg['current_sales_rub_total'] / category_agg['previous_sales_rub_total'] - 1) * 100).round(1)
    
    # График
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=category_agg['category_name'],
        y=category_agg['sales_rub_change'],
        text=category_agg.apply(lambda x: f"{x['sales_rub_change']:+.1f}%<br>({format_number(x['current_sales_rub_total'])} ₽)", axis=1),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Изменение продаж по категориям (год к году)',
        xaxis_title='Категория',
        yaxis_title='Изменение, %',
        showlegend=False
    )
    
    return fig

def create_price_analysis_charts(df):
    """Create price analysis charts for categories"""
    # Агрегация данных по категориям
    price_agg = df.groupby('category_name').agg({
        'average_price_kg_current': 'mean',
        'average_price_kg_previous': 'mean'
    }).reset_index()
    
    # Расчет изменения цены
    price_agg['price_change'] = ((price_agg['average_price_kg_current'] / price_agg['average_price_kg_previous'] - 1) * 100).round(1)
    
    # График
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=price_agg['category_name'],
        y=price_agg['price_change'],
        text=price_agg.apply(lambda x: f"{x['price_change']:+.1f}%<br>({format_number(x['average_price_kg_current'])} ₽/кг)", axis=1),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Изменение цен по категориям (год к году)',
        xaxis_title='Категория',
        yaxis_title='Изменение, %',
        showlegend=False
    )
    
    return fig

def create_market_share_charts(df):
    """Create market share charts for categories"""
    # Calculate market shares
    total_rub = df['current_sales_rub_total'].sum()
    total_kg = df['current_sales_kg_total'].sum()
    
    share_df = df.groupby('category_name').agg({
        'current_sales_rub_total': 'sum',
        'current_sales_kg_total': 'sum'
    }).reset_index()
    
    share_df['rub_share'] = (share_df['current_sales_rub_total'] / total_rub * 100).round(1)
    share_df['kg_share'] = (share_df['current_sales_kg_total'] / total_kg * 100).round(1)
    
    # Sort by share and get top categories
    share_df = share_df.sort_values('rub_share', ascending=False)
    
    # Create pie chart for RUB share
    fig_rub = go.Figure(data=[go.Pie(
        labels=share_df['category_name'],
        values=share_df['rub_share'],
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>" +
                      "Доля: %{percent}<br>" +
                      "Продажи: %{customdata:,.0f} ₽<extra></extra>",
        customdata=share_df['current_sales_rub_total']
    )])
    fig_rub.update_layout(
        title='Доля категорий (РУБ)',
        showlegend=False
    )
    
    # Create pie chart for KG share
    fig_kg = go.Figure(data=[go.Pie(
        labels=share_df['category_name'],
        values=share_df['kg_share'],
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>" +
                      "Доля: %{percent}<br>" +
                      "Продажи: %{customdata:,.0f} кг<extra></extra>",
        customdata=share_df['current_sales_kg_total']
    )])
    fig_kg.update_layout(
        title='Доля категорий (КГ)',
        showlegend=False
    )
    
    return fig_rub, fig_kg

def create_chain_analysis_charts(df):
    """Create analysis charts for chains"""
    # Aggregate data by chain
    chain_agg = df.groupby('chain_name').agg({
        'current_sales_rub_total': 'sum',
        'current_sales_kg_total': 'sum',
        'previous_sales_rub_total': 'sum',
        'previous_sales_kg_total': 'sum',
        'current_sales_rub_share': 'mean',
        'current_sales_kg_share': 'mean'
    }).reset_index()
    
    # Calculate changes
    chain_agg['sales_change_rub'] = ((chain_agg['current_sales_rub_total'] / chain_agg['previous_sales_rub_total'] - 1) * 100).round(1)
    chain_agg['sales_change_kg'] = ((chain_agg['current_sales_kg_total'] / chain_agg['previous_sales_kg_total'] - 1) * 100).round(1)
    
    # Sort by current sales
    chain_agg = chain_agg.sort_values('current_sales_rub_total', ascending=False)
    
    # Create sales comparison chart
    fig_sales = go.Figure()
    
    # Add current sales bars
    fig_sales.add_trace(go.Bar(
        name='Текущий период (РУБ)',
        x=chain_agg['chain_name'],
        y=chain_agg['current_sales_rub_total'],
        text=chain_agg['current_sales_rub_total'].apply(lambda x: format_number(x) + ' ₽'),
        textposition='auto',
    ))
    
    # Add previous sales bars
    fig_sales.add_trace(go.Bar(
        name='Предыдущий период (РУБ)',
        x=chain_agg['chain_name'],
        y=chain_agg['previous_sales_rub_total'],
        text=chain_agg['previous_sales_rub_total'].apply(lambda x: format_number(x) + ' ₽'),
        textposition='auto',
    ))
    
    fig_sales.update_layout(
        title='Продажи по торговым сетям',
        barmode='group',
        showlegend=True
    )
    
    # Create market share chart
    sales_text = chain_agg['current_sales_rub_total'].apply(lambda x: format_number(x) + ' ₽')
    
    fig_share = go.Figure(data=[go.Pie(
        labels=chain_agg['chain_name'],
        values=chain_agg['current_sales_rub_share'],
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>" +
                      "Доля: %{percent}<br>" +
                      "Продажи: %{text}<br>" +
                      "<extra></extra>",
        text=sales_text
    )])
    
    fig_share.update_layout(
        title='Доли торговых сетей',
        showlegend=False
    )
    
    # Create changes chart
    fig_changes = go.Figure()
    
    # Add RUB change bars
    fig_changes.add_trace(go.Bar(
        name='Изменение продаж (РУБ)',
        x=chain_agg['chain_name'],
        y=chain_agg['sales_change_rub'],
        text=chain_agg['sales_change_rub'].apply(lambda x: f"{x:+.1f}%"),
        textposition='auto',
    ))
    
    # Add KG change bars
    fig_changes.add_trace(go.Bar(
        name='Изменение продаж (КГ)',
        x=chain_agg['chain_name'],
        y=chain_agg['sales_change_kg'],
        text=chain_agg['sales_change_kg'].apply(lambda x: f"{x:+.1f}%"),
        textposition='auto',
    ))
    
    fig_changes.update_layout(
        title='Изменение продаж по сетям',
        barmode='group',
        showlegend=True
    )
    
    return fig_sales, fig_share, fig_changes

def calculate_metrics(df):
    """Calculate key metrics from the data"""
    metrics = {}
    
    # Total current sales
    metrics['total_current_sales_rub'] = df['current_sales_rub_total'].sum()
    metrics['total_current_sales_kg'] = df['current_sales_kg_total'].sum()
    
    # Total previous sales
    metrics['total_previous_sales_rub'] = df['previous_sales_rub_total'].sum()
    metrics['total_previous_sales_kg'] = df['previous_sales_kg_total'].sum()
    
    # Average prices
    metrics['avg_current_price'] = df['average_price_kg_current'].mean()
    metrics['avg_previous_price'] = df['average_price_kg_previous'].mean()
    
    # Calculate changes
    metrics['sales_rub_yoy'] = ((metrics['total_current_sales_rub'] / metrics['total_previous_sales_rub'] - 1) * 100).round(1)
    metrics['sales_kg_yoy'] = ((metrics['total_current_sales_kg'] / metrics['total_previous_sales_kg'] - 1) * 100).round(1)
    metrics['price_change'] = ((metrics['avg_current_price'] / metrics['avg_previous_price'] - 1) * 100).round(1)
    
    # Format values for display
    metrics['current_sales_rub_fmt'] = format_number(metrics['total_current_sales_rub']) + ' ₽'
    metrics['current_sales_kg_fmt'] = format_number(metrics['total_current_sales_kg']) + ' кг'
    metrics['sales_rub_yoy_fmt'] = f"{metrics['sales_rub_yoy']:+.1f}%"
    metrics['sales_kg_yoy_fmt'] = f"{metrics['sales_kg_yoy']:+.1f}%"
    metrics['price_change_fmt'] = f"{metrics['price_change']:+.1f}%"
    
    # Count unique values
    metrics['category_count'] = df['category_name'].nunique() if 'category_name' in df.columns else None
    metrics['chain_count'] = df['chain_name'].nunique() if 'chain_name' in df.columns else None
    metrics['producer_count'] = df['producer_name'].nunique()
    
    return metrics

def calculate_chain_metrics(df):
    """Calculate metrics for chains"""
    metrics = {}
    
    # Общие продажи
    metrics['total_current_sales_rub'] = df['current_sales_rub_total'].sum()
    metrics['total_previous_sales_rub'] = df['previous_sales_rub_total'].sum()
    metrics['total_current_sales_kg'] = df['current_sales_kg_total'].sum()
    metrics['total_previous_sales_kg'] = df['previous_sales_kg_total'].sum()
    
    # Изменения год к году
    metrics['sales_rub_yoy'] = ((metrics['total_current_sales_rub'] / metrics['total_previous_sales_rub'] - 1) * 100).round(1)
    metrics['sales_kg_yoy'] = ((metrics['total_current_sales_kg'] / metrics['total_previous_sales_kg'] - 1) * 100).round(1)
    
    # Форматирование значений
    metrics['total_current_sales_rub_fmt'] = format_number(metrics['total_current_sales_rub']) + ' ₽'
    metrics['total_current_sales_kg_fmt'] = format_number(metrics['total_current_sales_kg']) + ' кг'
    metrics['sales_rub_yoy_fmt'] = f"{metrics['sales_rub_yoy']:+.1f}%"
    metrics['sales_kg_yoy_fmt'] = f"{metrics['sales_kg_yoy']:+.1f}%"
    
    # Количество сетей и категорий
    metrics['chain_count'] = df['chain_name'].nunique()
    metrics['category_count'] = df['category_name'].nunique()
    
    return metrics

def create_manufacturer_market_comparison(df, selected_producer):
    """
    Создает график сравнения динамики цен и объемов продаж производителя с рынком
    
    Args:
        df: DataFrame с данными
        selected_producer: выбранный производитель для анализа
    """
    # Подготовка данных для всего рынка
    market_metrics = df.groupby('category_name').agg({
        'current_sales_kg_total': 'sum',
        'previous_sales_kg_total': 'sum',
        'current_sales_rub_total': 'sum',
        'previous_sales_rub_total': 'sum'
    }).reset_index()
    
    # Расчет средних цен по рынку
    market_metrics['market_price_current'] = market_metrics['current_sales_rub_total'] / market_metrics['current_sales_kg_total']
    market_metrics['market_price_previous'] = market_metrics['previous_sales_rub_total'] / market_metrics['previous_sales_kg_total']
    
    # Расчет изменений для рынка
    market_metrics['market_price_change'] = ((market_metrics['market_price_current'] / market_metrics['market_price_previous']) - 1) * 100
    market_metrics['market_volume_change'] = ((market_metrics['current_sales_kg_total'] / market_metrics['previous_sales_kg_total']) - 1) * 100
    
    # Подготовка данных для производителя
    manufacturer_data = df[df['producer_name'] == selected_producer].groupby('category_name').agg({
        'current_sales_kg_total': 'sum',
        'previous_sales_kg_total': 'sum',
        'current_sales_rub_total': 'sum',
        'previous_sales_rub_total': 'sum'
    }).reset_index()
    
    # Расчет средних цен производителя
    manufacturer_data['manuf_price_current'] = manufacturer_data['current_sales_rub_total'] / manufacturer_data['current_sales_kg_total']
    manufacturer_data['manuf_price_previous'] = manufacturer_data['previous_sales_rub_total'] / manufacturer_data['previous_sales_kg_total']
    
    # Расчет изменений для производителя
    manufacturer_data['manuf_price_change'] = ((manufacturer_data['manuf_price_current'] / manufacturer_data['manuf_price_previous']) - 1) * 100
    manufacturer_data['manuf_volume_change'] = ((manufacturer_data['current_sales_kg_total'] / manufacturer_data['previous_sales_kg_total']) - 1) * 100
    
    # Объединение данных
    merged_data = pd.merge(market_metrics, manufacturer_data, on='category_name', suffixes=('_market', '_manuf'))
    
    # Создание графика
    fig = go.Figure()
    
    # Добавляем линии изменения цен
    fig.add_trace(go.Scatter(
        x=merged_data['category_name'],
        y=merged_data['manuf_price_change'],
        name=f'Изменение цен {selected_producer}',
        line=dict(color=COLORS['positive'], width=2),
        yaxis='y1'
    ))
    
    fig.add_trace(go.Scatter(
        x=merged_data['category_name'],
        y=merged_data['market_price_change'],
        name='Изменение цен (рынок)',
        line=dict(color=COLORS['positive'], dash='dash', width=2),
        yaxis='y1'
    ))
    
    # Добавляем линии изменения объемов
    fig.add_trace(go.Scatter(
        x=merged_data['category_name'],
        y=merged_data['manuf_volume_change'],
        name=f'Изменение объемов {selected_producer}',
        line=dict(color=COLORS['neutral'], width=2),
        yaxis='y2'
    ))
    
    fig.add_trace(go.Scatter(
        x=merged_data['category_name'],
        y=merged_data['market_volume_change'],
        name='Изменение объемов (рынок)',
        line=dict(color=COLORS['neutral'], dash='dash', width=2),
        yaxis='y2'
    ))
    
    # Настройка layout
    fig.update_layout(
        title=f'Сравнение динамики цен и объемов: {selected_producer} vs Рынок',
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            title='Категория',
            tickangle=45
        ),
        yaxis=dict(
            title='Изменение цены (%)',
            side='left',
            showgrid=True,
            gridcolor=COLORS['grid'],
            zeroline=True,
            zerolinecolor=COLORS['grid']
        ),
        yaxis2=dict(
            title='Изменение объема (%)',
            side='right',
            overlaying='y',
            showgrid=False,
            zeroline=True,
            zerolinecolor=COLORS['grid']
        ),
        legend=dict(
            x=1.1,
            y=1,
            bgcolor='rgba(255, 255, 255, 0.1)'
        ),
        showlegend=True
    )
    
    # Добавляем аннотации для корреляции
    correlations = []
    for idx, row in merged_data.iterrows():
        if abs(row['manuf_price_change']) > 5 or abs(row['manuf_volume_change']) > 5:
            if row['manuf_price_change'] * row['manuf_volume_change'] < 0:
                correlations.append(f"• {row['category_name']}: Отрицательная корреляция")
            elif row['manuf_price_change'] * row['manuf_volume_change'] > 0:
                correlations.append(f"• {row['category_name']}: Положительная корреляция")
    
    if correlations:
        correlation_text = "Значимые корреляции:<br>" + "<br>".join(correlations)
        fig.add_annotation(
            x=1.3,
            y=0.5,
            xref="paper",
            yref="paper",
            text=correlation_text,
            showarrow=False,
            font=dict(size=10),
            align="left",
            bgcolor='rgba(255, 255, 255, 0.1)',
            bordercolor=COLORS['grid'],
            borderwidth=1
        )
    
    return apply_dark_theme(fig)

def apply_dark_theme(fig):
    fig.update_layout(
        template='plotly_dark',
        font=dict(color='white')
    )
    return fig
