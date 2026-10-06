from rapidfuzz import fuzz

text1 = "Mens Plain Cotton T Shirt Mens T-Shirts India".lower()
print(f"token_set_ratio t-shirt: {fuzz.token_set_ratio('t-shirt', text1)}")
print(f"partial_ratio t-shirt: {fuzz.partial_ratio('t-shirt', text1)}")
print(f"WRatio t-shirt: {fuzz.WRatio('t-shirt', text1)}")
print(f"WRatio tshirt: {fuzz.WRatio('tshirt', text1)}")
print(f"WRatio t shirt: {fuzz.WRatio('t shirt', text1)}")

text2 = "Industrial Heavy Duty Drill Press".lower()
print(f"WRatio drill: {fuzz.WRatio('drill', text2)}")
