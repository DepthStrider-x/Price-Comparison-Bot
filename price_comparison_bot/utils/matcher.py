import re

def normalize(text):
    if not text:
        return ""
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

def get_match_score(product, query):
    title = product.get("title", "")
    if not title:
        return -1000

    norm_title = normalize(title)
    norm_query = normalize(query)
    
    if not norm_query:
        return 0

    score = 0
    query_tokens = norm_query.split()
    title_tokens = norm_title.split()

    # Base match: Token overlap
    matches = 0
    for token in query_tokens:
        if token in title_tokens: # Exact token match
            score += 10
            matches += 1
        elif token in norm_title: # Substring match
            score += 5

    # Coverage bonus
    if len(query_tokens) > 0:
        coverage = matches / len(query_tokens)
        score += coverage * 20

    # Exact match bonus
    if norm_query == norm_title:
        score += 100
    
    # Number match (Critical for things like '17' vs '16')
    numbers_in_query = re.findall(r"\d+", norm_query)
    numbers_in_title = re.findall(r"\d+", norm_title)
    
    for num in numbers_in_query:
        if num in numbers_in_title:
            score += 30
        else:
            score -= 50  # Heavy penalty for missing model number

    # Negative keywords (unrelated items)
    negative_keywords = ["case", "cover", "guard", "glass", "protector"]
    for kw in negative_keywords:
        if kw in norm_title and kw not in norm_query:
            score -= 100

    return score

def match_product(products, query):
    """
    Selects the single best matching product from a list.
    """
    if not products:
        return None

    scored_products = []
    for p in products:
        score = get_match_score(p, query)
        scored_products.append((score, p))

    # Sort by score descending
    scored_products.sort(key=lambda x: x[0], reverse=True)

    best_score, best_product = scored_products[0]

    # Threshold for "unrelated"
    # If the score is very low (e.g. negative due to penalties), return None
    if best_score < 0:
        return None
        
    return best_product
