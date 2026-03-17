from curl_cffi import requests
import json
import time

def fetch_trendyol_data(url):
    # Trendyol'un gerçek bir kullanıcı ile botu ayırt ettiği kritik başlıklar
    headers = {
        "authority": "public.trendyol.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://www.trendyol.com/",
        "origin": "https://www.trendyol.com",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    try:
        # curl_cffi sayesinde TLS Fingerprint (parmak izi) gerçek tarayıcı gibi görünür
        response = requests.get(
            url, 
            headers=headers, 
            impersonate="chrome120", # En kritik nokta: Chrome taklidi
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Hata Kodu: {response.status_code}")
            return None
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return None

def parse_products(data):
    if not data or 'data' not in data or 'products' not in data['data']:
        return []
    
    products_list = []
    for item in data['data']['products']:
        product = {
            "İsim": item.get('name'),
            "Marka": item.get('brand', {}).get('name'),
            "Fiyat": item.get('price', {}).get('sellingPrice', {}).get('amount'),
            "Favori": item.get('favoriteCount'),
            "Puan": item.get('ratingScore'),
            "URL": f"https://www.trendyol.com{item.get('url')}"
        }
        products_list.append(product)
    return products_list
