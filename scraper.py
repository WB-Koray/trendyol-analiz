import requests
import pandas as pd

def get_trendyol_data(category_id, pages):
    all_products = []
    # Alternatif ve daha güncel bir Trendyol Discovery URL'i
    base_url = "https://public.trendyol.com/discovery-web-search-service/v1/filter"
    
    # Trendyol bot korumasını geçmek için daha detaylı Header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.trendyol.com/",
        "Origin": "https://www.trendyol.com"
    }
    
    for page in range(1, pages + 1):
        params = {
            "wc": category_id,
            "pi": page,
            "sst": "BEST_SELLER", # En çok satanlar
            "culture": "tr-TR",
            "storefrontId": "1",
            "categoryRelevancyEnabled": "true"
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("content", [])
                
                if not products:
                    # Eğer 'content' boşsa 'products' anahtarına bak
                    products = data.get("products", [])

                for p in products:
                    all_products.append({
                        "Ürün Adı": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if p.get("brand") else "Belirtilmemiş",
                        "Fiyat": p.get("price", {}).get("sellingPrice"),
                        "Favori Sayısı": p.get("favoriteCount", 0),
                        "Değerlendirme Sayısı": p.get("ratingCount", 0),
                        "Puan": p.get("ratingScore", 0),
                        "Link": "https://www.trendyol.com" + p.get("url", "")
                    })
            else:
                print(f"Hata Kodu: {response.status_code}")
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")
            
    return pd.DataFrame(all_products)
