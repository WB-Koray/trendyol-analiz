import requests
import pandas as pd

def get_trendyol_data(category_id, pages):
    all_products = []
    # Tarayıcı oturumunu simüle etmek için session başlatıyoruz
    session = requests.Session()
    
    # Trendyol'un bot korumasını geçmek için en kritik bilgiler
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"https://www.trendyol.com/sr?wc={category_id}",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Önce ana sayfaya bir istek atıp çerezleri (cookies) alıyoruz
    try:
        session.get("https://www.trendyol.com", headers=headers, timeout=10)
    except:
        pass

    for page in range(1, pages + 1):
        # Arama servisinin asıl adresi
        url = "https://public.trendyol.com/discovery-web-search-service/v1/filter"
        
        params = {
            "wc": category_id,
            "pi": page,
            "sst": "BEST_SELLER",
            "culture": "tr-TR",
            "storefrontId": "1"
        }
        
        try:
            # Çerezleri de içeren session ile istek atıyoruz
            res = session.get(url, params=params, headers=headers, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                products = data.get("content", [])
                
                # Eğer content yoksa alternatif anahtarlara bak
                if not products:
                    products = data.get("products", [])

                for p in products:
                    all_products.append({
                        "Ürün Adı": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if p.get("brand") else "-",
                        "Fiyat": p.get("price", {}).get("sellingPrice", 0),
                        "Favori": p.get("favoriteCount", 0),
                        "Değerlendirme": p.get("ratingCount", 0),
                        "Puan": p.get("ratingScore", 0),
                        "Link": "https://www.trendyol.com" + p.get("url", "")
                    })
        except Exception as e:
            print(f"Hata oluştu: {e}")
            
    return pd.DataFrame(all_products)
