import requests
import pandas as pd

def get_trendyol_data(category_id, pages):
    all_products = []
    base_url = "https://public.trendyol.com/discovery-web-search-service/v1/filter"
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in range(1, pages + 1):
        params = {"wc": category_id, "pi": page, "sst": "BEST_SELLER", "culture": "tr-TR"}
        try:
            res = requests.get(base_url, params=params, headers=headers)
            if res.status_code == 200:
                products = res.json().get("content", [])
                for p in products:
                    all_products.append({
                        "Ürün": p.get("name"),
                        "Marka": p.get("brand", {}).get("name"),
                        "Fiyat": p.get("price", {}).get("sellingPrice"),
                        "Favori": p.get("favoriteCount"),
                        "Yorum": p.get("ratingCount")
                    })
        except: continue
    return pd.DataFrame(all_products)
