import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="Trendyol Veri Analizi", layout="wide", page_icon="🚀")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol_Veri')
    return output.getvalue()

def smart_parse(js_data):
    # Ürün listesini farklı anahtarlardan bulmaya çalış
    products = js_data.get("products", js_data.get("content", []))
    if not products and "data" in js_data:
        products = js_data["data"].get("products", [])
    
    parsed_list = []
    for p in products:
        # Fiyat yakalama (Current, Selling veya Original)
        pr = p.get("price", {})
        price = pr.get("current", pr.get("sellingPrice", pr.get("originalPrice", 0)))
        
        # Sosyal kanıtlar (Favori ve Satış)
        fav = p.get("favoriteCount", 0)
        orders = "-"
        for s in p.get("socialProof", []):
            if s.get("key") == "favoriteCount": fav = s.get("value", fav)
            if s.get("key") == "orderCount": orders = s.get("value", "-")
        
        parsed_list.append({
            "Ürün Adı": p.get("name", "Bilinmiyor"),
            "Marka": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand", "-"),
            "Fiyat (TL)": price,
            "Favori": fav,
            "Yorum": p.get("ratingCount", 0),
            "Satış Bilgisi": orders,
            "Puan": p.get("ratingScore", {}).get("averageRating", 0) if isinstance(p.get("ratingScore"), dict) else p.get("ratingScore", 0),
            "Link": "https://www.trendyol.com" + p.get("url", "")
        })
    return pd.DataFrame(parsed_list)

st.title("🛡️ Trendyol Akıllı Veri Çözücü v2")
st.info("Trendyol engeli nedeniyle 'Manuel Veri Yapıştır' sekmesi en güvenli yoldur.")

tab1, tab2 = st.tabs(["📝 Manuel Veri Yapıştır", "ℹ️ Nasıl Yapılır?"])

with tab1:
    raw_text = st.text_area("JSON verisini buraya yapıştırın:", height=300, placeholder="<!DOCTYPE... veya { ... }")
    if st.button("Analizi Başlat"):
        if raw_text:
            try:
                # Önce JSON deniyoruz
                try:
                    data = json.loads(raw_text.strip())
                except:
                    # HTML içinden veri ayıklama (regex)
                    import re
                    match = re.search(r'__SEARCH_APP_INITIAL_STATE__\s*=\s*({.*?});', raw_text)
                    if not match:
                        match = re.search(r'__single-search-result__PROPS\"\s*:\s*({.*?})<', raw_text)
                    data = json.loads(match.group(1)) if match else None
                
                if data:
                    df = smart_parse(data)
                    st.success(f"✅ {len(df)} ürün başarıyla ayıklandı!")
                    st.download_button("📥 Excel Olarak İndir", to_excel(df), "trendyol_rapor.xlsx")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("Metin içinde ürün verisi bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")

with tab2:
    st.markdown("""
    ### En Hızlı Yöntem:
    1. Trendyol'da sayfayı aşağı kaydırın.
    2. F12 -> **Network** sekmesine girin.
    3. Filtreye `filter` yazın.
    4. Çıkan dosyaya sağ tıklayıp **Copy Response** yapın.
    5. Buraya yapıştırın.
    """)
