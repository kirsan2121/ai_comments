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

def check_permissions():
    with engine.connect() as connection:
        try:
            # Check current user
            current_user_sql = "SELECT current_user, session_user;"
            
            # Check schema permissions
            schema_permissions_sql = """
            SELECT 
                n.nspname as schema_name,
                has_schema_privilege(current_user, n.nspname, 'CREATE') as has_create,
                has_schema_privilege(current_user, n.nspname, 'USAGE') as has_usage
            FROM pg_namespace n
            WHERE n.nspname NOT LIKE 'pg_%' 
            AND n.nspname != 'information_schema';
            """
            
            # Check table permissions
            table_permissions_sql = """
            SELECT 
                schemaname,
                tablename,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'SELECT') as has_select,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'INSERT') as has_insert,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'UPDATE') as has_update,
                has_table_privilege(current_user, schemaname || '.' || tablename, 'DELETE') as has_delete
            FROM pg_tables
            WHERE schemaname IN ('data_mart', 'sandbox');
            """
            
            print("\nCurrent user info:")
            result = connection.execute(text(current_user_sql))
            for row in result:
                print(f"Current user: {row[0]}, Session user: {row[1]}")
            
            print("\nSchema permissions:")
            result = connection.execute(text(schema_permissions_sql))
            for row in result:
                print(f"Schema: {row[0]}, Create: {row[1]}, Usage: {row[2]}")
            
            print("\nTable permissions:")
            result = connection.execute(text(table_permissions_sql))
            for row in result:
                print(f"Schema: {row[0]}, Table: {row[1]}")
                print(f"  Select: {row[2]}, Insert: {row[3]}, Update: {row[4]}, Delete: {row[5]}")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    check_permissions()
