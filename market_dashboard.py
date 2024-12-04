import streamlit as st
import pandas as pd
import logging
from data.queries import (
    load_data, 
    get_unique_values, 
    get_available_months,
    load_chain_data,
    get_unique_chain_values
)
from utils.visualization import (
    create_sales_comparison_chart, 
    create_price_analysis_charts,
    create_market_share_charts,
    calculate_metrics,
    create_chain_analysis_charts,
    calculate_chain_metrics
)

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Загрузка уникальных значений для фильтров
    logging.debug('Loading unique values for filters...')
    producers, categories = get_unique_values()
    chain_producers, chains = get_unique_chain_values()
    available_current_months, available_previous_months = get_available_months()

    logging.debug(f'Producers: {producers}, Categories: {categories}')
    logging.debug(f'Chain Producers: {chain_producers}, Chains: {chains}')

    # Sidebar filters
    st.sidebar.header("Фильтры")

    selected_current_month = st.sidebar.selectbox(
        "Выберите текущий месяц",
        options=available_current_months,
        format_func=lambda x: pd.to_datetime(x).strftime('%B %Y') if x else 'Все'
    )

    selected_previous_month = st.sidebar.selectbox(
        "Выберите предыдущий месяц для сравнения",
        options=available_previous_months,
        format_func=lambda x: pd.to_datetime(x).strftime('%B %Y') if x else 'Все'
    )

    # Фильтры для категорий
    st.sidebar.subheader("Фильтры по категориям")
    selected_producers = st.sidebar.multiselect(
        "Производители (категории)",
        options=producers,
        default=['Все']
    )

    selected_categories = st.sidebar.multiselect(
        "Категории",
        options=categories,
        default=['Все']
    )

    # Фильтры для торговых сетей
    st.sidebar.subheader("Фильтры по торговым сетям")
    selected_chain_producers = st.sidebar.multiselect(
        "Производители (сети)",
        options=chain_producers,
        default=['Все']
    )

    selected_chains = st.sidebar.multiselect(
        "Торговые сети",
        options=chains,
        default=['Все']
    )

    # Загрузка данных
    df_categories = load_data(
        current_month=selected_current_month,
        previous_month=selected_previous_month,
        producers=selected_producers,
        categories=selected_categories
    )

    df_chains = load_chain_data(
        current_month=selected_current_month,
        previous_month=selected_previous_month,
        producers=selected_chain_producers,
        chains=selected_chains
    )

    # Основной контент
    st.title("Анализ рынка")

    # Секция анализа по категориям
    st.header("Анализ по категориям")
    
    # Метрики по категориям
    metrics = calculate_metrics(df_categories)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Продажи (руб)", metrics['current_sales_rub_fmt'], metrics['sales_rub_yoy_fmt'])
    with col2:
        st.metric("Продажи (кг)", metrics['current_sales_kg_fmt'], metrics['sales_kg_yoy_fmt'])
    with col3:
        st.metric("Категорий", str(metrics['category_count']))
    with col4:
        st.metric("Производителей", str(metrics['producer_count']))

    # Графики по категориям
    st.subheader("Продажи по категориям")
    sales_chart = create_sales_comparison_chart(df_categories)
    st.plotly_chart(sales_chart, use_container_width=True)

    st.subheader("Анализ цен")
    price_charts = create_price_analysis_charts(df_categories)
    st.plotly_chart(price_charts, use_container_width=True)

    st.subheader("Доли рынка")
    market_share_charts = create_market_share_charts(df_categories)
    for chart in market_share_charts:
        st.plotly_chart(chart, use_container_width=True)

    # Секция анализа по торговым сетям
    st.header("Анализ по торговым сетям")
    
    # Метрики по сетям
    chain_metrics = calculate_chain_metrics(df_chains)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Продажи в сетях (руб)", chain_metrics['total_current_sales_rub_fmt'], chain_metrics['sales_rub_yoy_fmt'])
    with col2:
        st.metric("Продажи в сетях (кг)", chain_metrics['total_current_sales_kg_fmt'], chain_metrics['sales_kg_yoy_fmt'])
    with col3:
        st.metric("Торговых сетей", str(chain_metrics['chain_count']))
    with col4:
        st.metric("Категорий", str(chain_metrics['category_count']))

    # Графики по сетям
    sales_fig, volume_fig, top_products_fig = create_chain_analysis_charts(df_chains)
    
    st.subheader("Изменение продаж в рублях")
    st.plotly_chart(sales_fig, use_container_width=True)
    
    st.subheader("Изменение продаж в килограммах")
    st.plotly_chart(volume_fig, use_container_width=True)
    
    st.subheader("Топ продуктов")
    st.plotly_chart(top_products_fig, use_container_width=True)

except Exception as e:
    logging.error(f"An error occurred: {str(e)}")
    st.error(f"Произошла ошибка: {str(e)}")
