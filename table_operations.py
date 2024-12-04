from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def copy_and_modify_table():
    with engine.connect() as connection:
        try:
            # Step 1: Create table structure and copy data
            copy_table_sql = """
            CREATE TABLE sandbox.producer_product_category_periods 
            (LIKE data_mart.producer_product_category_periods INCLUDING ALL);
            
            INSERT INTO sandbox.producer_product_category_periods 
            SELECT * FROM data_mart.producer_product_category_periods;
            """
            
            print("Step 1: Creating table and copying data from data_mart to sandbox...")
            connection.execute(text(copy_table_sql))
            connection.commit()
            print("Table created and data copied successfully!")

            # Step 2: Add new columns and calculate values
            modify_table_sql = """
            ALTER TABLE sandbox.producer_product_category_periods 
            ADD COLUMN IF NOT EXISTS average_price_kg_current DECIMAL,
            ADD COLUMN IF NOT EXISTS average_price_kg_previous DECIMAL;
            
            UPDATE sandbox.producer_product_category_periods 
            SET 
                average_price_kg_current = CASE 
                    WHEN current_sales_kg_total != 0 THEN current_sales_rub_total / current_sales_kg_total 
                    ELSE NULL 
                END,
                average_price_kg_previous = CASE 
                    WHEN previous_sales_kg_total != 0 THEN previous_sales_rub_total / previous_sales_kg_total 
                    ELSE NULL 
                END;
            """
            
            print("Step 2: Adding new columns and calculating values...")
            connection.execute(text(modify_table_sql))
            connection.commit()
            print("Columns added and values calculated successfully!")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            connection.rollback()

if __name__ == "__main__":
    copy_and_modify_table()
