import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db')

for table in ['listings', 'users', 'categories', 'addresses', 'companies']:
    try:
        print(f"--- {table} ---")
        df = pd.read_sql(f"SELECT * FROM {table} LIMIT 1", engine)
        print(df.columns.tolist())
    except Exception as e:
        print(f"Error: {e}")
