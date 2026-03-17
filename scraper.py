import requests
import pandas as pd

def get_trendyol_data(category_id, pages):
    all_products = []
    session = requests.Session()
    
    # Gerçek bir tarayıcı gibi görünmek için gerekli kimlik bilgileri
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.trendyol.com/",
        "X-Domain": "https://www.trendyol.com"
    }

    for page in range(1, pages + 1):
        url = "https://public.trendyol.com/discovery-web-search-service/v1/filter"
        params = {
            "wc": category_id,
            "pi": page,
            "sst": "BEST_SELLER",
            "culture": "tr-TR",
            "storefrontId": "1"
        }
        
        try:
            res = session.get(url, params=params, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                products = data.get("content", [])
                
                for p in products:
                    all_products.append({
                        "Ürün": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if p.get("brand") else "-",
                        "Fiyat": p.get("price", {}).get("sellingPrice", 0),
                        "Favori": p.get("favoriteCount", 0),
                        "Yorum": p.get("ratingCount", 0),
                        "Link": "https://www.trendyol.com" + p.get("url", "")
                    })
        except:
            continue
            
    return pd.DataFrame(all_products)
