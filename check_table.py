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

def check_table():
    with engine.connect() as connection:
        try:
            # Check if table exists
            check_sql = """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'sandbox' 
                AND table_name = 'producer_product_category_periods'
            );
            """
            
            result = connection.execute(text(check_sql)).fetchone()
            exists = result[0] if result else False
            
            if exists:
                print("Table sandbox.producer_product_category_periods exists")
                
                # Check columns
                columns_sql = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'sandbox' 
                AND table_name = 'producer_product_category_periods';
                """
                
                print("\nColumns in the table:")
                for column in connection.execute(text(columns_sql)):
                    print(f"- {column[0]}: {column[1]}")
            else:
                print("Table sandbox.producer_product_category_periods does not exist")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    check_table()
