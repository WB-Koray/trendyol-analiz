import requests
import pandas as pd

def get_trendyol_data(category_id, pages):
    all_products = []
    # Güncel Discovery API adresi
    base_url = "https://public.trendyol.com/discovery-web-search-service/v1/filter"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "culture": "tr-TR",
        "storefrontId": "1"
    }
    
    for page in range(0, pages): # Trendyol API bazen 0'dan başlar
        params = {
            "wc": category_id,
            "pi": page,
            "sst": "BEST_SELLER",
            "culture": "tr-TR",
            "userGenderId": "1",
            "pId": "0",
            "scoringAlgorithmId": "2"
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Trendyol verisi bazen 'content' bazen 'products' altında gelir
                products = data.get("content", [])
                
                for p in products:
                    all_products.append({
                        "Ürün Adı": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if p.get("brand") else "-",
                        "Fiyat": p.get("price", {}).get("sellingPrice"),
                        "Favori": p.get("favoriteCount", 0),
                        "Yorum Sayısı": p.get("ratingCount", 0),
                        "Puan": p.get("ratingScore", 0),
                        "Link": "https://www.trendyol.com" + p.get("url", "")
                    })
        except Exception as e:
            print(f"Bağlantı sorunu: {e}")
            
    return pd.DataFrame(all_products)
