import pandas as pd
from sqlalchemy import text
from config.database import engine
from config.table_schemas import TABLES
import streamlit as st

def get_table_columns(table_name):
    """Get column names from specified table"""
    query = f"""
    SELECT column_name, data_type 
    FROM information_schema.columns
    WHERE table_schema = 'data_mart'
    AND table_name = '{table_name}'
    ORDER BY ordinal_position;
    """
    return pd.read_sql(query, engine)

def get_column_names(table_name):
    """
    Get column names for a specific table from the schema definition.
    
    Args:
        table_name (str): Name of the table without schema prefix
        
    Returns:
        dict: Dictionary with column names and their types
    """
    if table_name not in TABLES:
        raise ValueError(f"Table {table_name} not found in schema definitions")
    
    return TABLES[table_name]["columns"]

def validate_columns(df, table_name):
    """
    Validate that DataFrame has all required columns from the schema.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        table_name (str): Name of the table to check against
        
    Returns:
        bool: True if all required columns are present
    """
    required_columns = set(get_column_names(table_name).keys())
    df_columns = set(df.columns)
    missing_columns = required_columns - df_columns
    
    if missing_columns:
        raise ValueError(f"Missing required columns for {table_name}: {missing_columns}")
    
    return True

@st.cache_data(ttl=3600)
def load_data(current_month=None, previous_month=None, producers=None, categories=None):
    """Load data from producer_product_category_periods table"""
    columns = get_column_names('producer_product_category_periods')
    column_list = ', '.join(columns.keys())
    
    query = f"""
    SELECT {column_list}
    FROM sandbox.producer_product_category_periods
    WHERE 1=1
    """
    
    params = {}
    if current_month:
        query += " AND current_month = :current_month"
        params['current_month'] = current_month

    if previous_month:
        query += " AND previous_month = :previous_month"
        params['previous_month'] = previous_month

    if producers and 'Все' not in producers:
        query += " AND producer_name = ANY(:producers)"
        params['producers'] = producers

    if categories and 'Все' not in categories:
        query += " AND category_name = ANY(:categories)"
        params['categories'] = categories

    df = pd.read_sql(text(query), engine, params=params)
    validate_columns(df, 'producer_product_category_periods')
    return df

@st.cache_data(ttl=3600)
def load_chain_data(current_month=None, previous_month=None, producers=None, chains=None):
    """Load data from producer_chain_product_periods table"""
    columns = get_column_names('producer_chain_product_periods')
    column_list = ', '.join(columns.keys())
    
    query = f"""
    SELECT {column_list}
    FROM data_mart.producer_chain_product_periods
    WHERE 1=1
    """
    
    params = {}
    if current_month:
        query += " AND current_month = :current_month"
        params['current_month'] = current_month

    if previous_month:
        query += " AND previous_month = :previous_month"
        params['previous_month'] = previous_month

    if producers and 'Все' not in producers:
        query += " AND producer_name = ANY(:producers)"
        params['producers'] = producers

    if chains and 'Все' not in chains:
        query += " AND chain_name = ANY(:chains)"
        params['chains'] = chains

    df = pd.read_sql(text(query), engine, params=params)
    validate_columns(df, 'producer_chain_product_periods')
    return df

@st.cache_data(ttl=3600)
def get_unique_values():
    query = """
    SELECT DISTINCT
        producer_name,
        category_name
    FROM sandbox.producer_product_category_periods
    """
    df = pd.read_sql(query, engine)
    return (
        ['Все'] + sorted(df['producer_name'].unique().tolist()),
        ['Все'] + sorted(df['category_name'].unique().tolist())
    )

@st.cache_data(ttl=3600)
def get_available_months():
    query = """
    SELECT DISTINCT current_month, previous_month
    FROM sandbox.producer_product_category_periods
    ORDER BY current_month DESC
    """
    df = pd.read_sql(query, engine)
    return (
        sorted(df['current_month'].unique(), reverse=True),
        sorted(df['previous_month'].unique(), reverse=True)
    )

@st.cache_data(ttl=3600)
def get_table_columns():
    """Get column names from the table"""
    query = """
    SELECT column_name, data_type 
    FROM information_schema.columns
    WHERE table_schema = 'data_mart'
    AND table_name = 'producer_chain_product_periods'
    ORDER BY ordinal_position;
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=3600)
def get_unique_chain_values():
    """Get unique values for chains from the new table"""
    query = """
    SELECT DISTINCT
        producer_name,
        chain_name
    FROM data_mart.producer_chain_product_periods
    """
    df = pd.read_sql(query, engine)
    return (
        ['Все'] + sorted(df['producer_name'].unique().tolist()),
        ['Все'] + sorted(df['chain_name'].unique().tolist())
    )
