import requests
import pandas as pd

def get_trendyol_data(category_id, pages):
    all_products = []
    # Bu sefer doğrudan web filtreleme API'sini kullanıyoruz
    base_url = "https://public.trendyol.com/discovery-web-search-service/v1/filter"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.trendyol.com/",
        "X-Domain": "https://www.trendyol.com"
    }
    
    for page in range(1, pages + 1):
        # Parametreleri Trendyol'un mobil sitesi gibi simüle ediyoruz
        params = {
            "wc": str(category_id),
            "pi": str(page),
            "sst": "BEST_SELLER",
            "culture": "tr-TR",
            "userGenderId": "1",
            "pId": "0",
            "scoringAlgorithmId": "2",
            "categoryRelevancyEnabled": "false",
            "isLegalRequirementConfirmed": "false",
            "searchByFeaturedBrand": "false"
        }
        
        try:
            # Streamlit Cloud IP'leri engellenebileceği için verify=False ekliyoruz (Gerekirse)
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Trendyol'un iki farklı json yapısı vardır, ikisini de kontrol ediyoruz
                products = data.get("content", [])
                if not products:
                    products = data.get("products", [])

                for p in products:
                    all_products.append({
                        "Ürün Adı": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if p.get("brand") else "-",
                        "Fiyat": p.get("price", {}).get("sellingPrice", 0),
                        "Favori": p.get("favoriteCount", 0),
                        "Yorum": p.get("ratingCount", 0),
                        "Puan": p.get("ratingScore", 0),
                        "Link": "https://www.trendyol.com" + p.get("url", "")
                    })
            else:
                # Debug bilgisi: Hangi kodla reddedildiğimizi görelim
                print(f"Hata: {response.status_code}")
                
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            
    return pd.DataFrame(all_products)
