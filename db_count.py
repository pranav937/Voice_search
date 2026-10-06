import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db')

query = "SELECT COUNT(*) FROM listings WHERE \"listingType\" = 'PRODUCT';"
count_df = pd.read_sql(query, engine)
print(f"Total Products in listings table: {count_df.iloc[0,0]}")

query_all = "SELECT COUNT(*) FROM listings;"
count_all_df = pd.read_sql(query_all, engine)
print(f"Total entries in listings table: {count_all_df.iloc[0,0]}")
