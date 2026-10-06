import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db')

query = "SELECT title FROM listings WHERE \"listingType\" = 'PRODUCT' LIMIT 20;"
df = pd.read_sql(query, engine)
print(df)
