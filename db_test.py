import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db')
tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", engine)
print(tables)
if not tables.empty:
    for table in tables['table_name']:
        print(f"Table: {table}")
        print(pd.read_sql(f"SELECT * FROM {table} LIMIT 1", engine).columns)
