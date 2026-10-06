from rapidfuzz import fuzz

texts = [
    "zara men slim fit shirt  textiles & apparel india",
    "cotton plain men t-shirts, size: medium, round neck mens t-shirts india",
    "mens plain cotton t shirt mens t-shirts india",
    "plain half sleeves men t shirt, polo neck mens t-shirts india",
]
query = "t-shirt"
for t in texts:
    print("---")
    print("Text:", t)
    print("WRatio:", fuzz.WRatio(query, t))
    print("partial_ratio:", fuzz.partial_ratio(query, t))
    print("token_set_ratio:", fuzz.token_set_ratio(query, t))
