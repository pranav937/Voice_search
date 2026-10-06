import pandas as pd
from rapidfuzz import fuzz
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:Jadequest%403009@3.111.57.216:5432/jaxmart_db')

query = """
SELECT 
    l.title AS "Product Name",
    c.name AS "Category",
    u."fullName" AS "Company Name",
    pd."pricePerUnit" AS "Price",
    'India' AS "Location"
FROM listings l
LEFT JOIN categories c ON l."categoryId" = c.id
LEFT JOIN users u ON l."sellerId" = u.id
LEFT JOIN product_details pd ON l.id = pd."listingId"
WHERE l.title ILIKE '%%t-shirt%%' OR l.title ILIKE '%%tshirt%%' OR l.title ILIKE '%%t shirt%%'
LIMIT 5;
"""
df = pd.read_sql(query, engine)
print("DF Length:", len(df))
for _, row in df.iterrows():
    text = (str(row['Product Name']) + " " + str(row['Category']) + " " + str(row['Location'])).lower()
    score = fuzz.WRatio("t-shirt", text)
    print(f"Text: {text} | WRatio: {score}")
