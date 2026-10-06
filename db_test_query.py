import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db')

query = """
SELECT 
    l.title AS "Product Name",
    c.name AS "Category",
    u."fullName" AS "Company Name",
    p."pricePerUnit" AS "Price",
    loc.city AS "Location"
FROM listings l
LEFT JOIN categories c ON l."categoryId" = c.id
LEFT JOIN users u ON l."sellerId" = u.id
LEFT JOIN product_details p ON l.id = p."listingId"
LEFT JOIN locations loc ON l."locationId" = loc.id
LIMIT 5;
"""
df = pd.read_sql(query, engine)
print(df)
