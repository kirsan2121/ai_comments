"""
This file contains the schemas of database tables used in the project.
It serves as a reference for column names and data types.
"""

PRODUCER_CATEGORY_SCHEMA = {
    # Dimensions
    "current_month": "date",
    "previous_month": "date",
    "producer_name": "varchar",
    "category_name": "varchar",
    
    # Metrics - Current Period
    "current_sales_rub_total": "numeric",
    "current_sales_kg_total": "numeric",
    "average_price_kg_current": "numeric",
    
    # Metrics - Previous Period
    "previous_sales_rub_total": "numeric",
    "previous_sales_kg_total": "numeric",
    "average_price_kg_previous": "numeric",
}

PRODUCER_CHAIN_SCHEMA = {
    # Dimensions
    "current_month": "date",
    "previous_month": "date",
    "producer_name": "varchar",
    "chain_name": "varchar",
    "category_name": "varchar",
    "product_name": "varchar",
    
    # Metrics - Current Period
    "current_sales_rub_total": "numeric",
    "current_sales_kg_total": "numeric",
    "current_sales_rub_share": "numeric",
    "current_sales_kg_share": "numeric",
    
    # Metrics - Previous Period
    "previous_sales_rub_total": "numeric",
    "previous_sales_kg_total": "numeric",
    "previous_sales_rub_share": "numeric",
    "previous_sales_kg_share": "numeric",
}

# Table names and schemas in database
TABLES = {
    "producer_product_category_periods": {
        "schema": "sandbox",
        "columns": PRODUCER_CATEGORY_SCHEMA
    },
    "producer_chain_product_periods": {
        "schema": "data_mart",
        "columns": PRODUCER_CHAIN_SCHEMA
    }
}
