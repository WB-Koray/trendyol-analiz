import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="Trendyol Detaylı Analiz", layout="wide", page_icon="🚀")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol_Analiz')
    return output.getvalue()

def smart_parse(js_data):
    products = js_data.get("products", js_data.get("content", []))
    if not products and "data" in js_data:
        products = js_data["data"].get("products", [])
    
    parsed_list = []
    for p in products:
        # Fiyat
        pr = p.get("price", {})
        price = pr.get("current", pr.get("sellingPrice", pr.get("originalPrice", 0)))
        
        # --- ROZET AYIKLAMA (Fenomen Seçimi, En Çok Satan vs.) ---
        badge_text = "-"
        strip_badge = p.get("stripBadge", {})
        
        if strip_badge:
            b_type = strip_badge.get("type", "")
            b_title = strip_badge.get("title", "")
            
            # Trendyol'un İngilizce kodlarını Türkçeye çeviriyoruz
            if b_type == "BEST_SELLER":
                badge_text = f"En Çok Satan {b_title}. Ürün"
            elif b_type == "MOST_RATED":
                badge_text = f"En Çok Değerlendirilen {b_title}. Ürün"
            elif b_type == "MOST_FAVOURITE":
                badge_text = f"En Çok Favorilenen {b_title}. Ürün"
            elif b_type == "TOP_VIEWED":
                badge_text = f"En Çok Ziyaret Edilen {b_title}. Ürün"
            else:
                badge_text = b_title # Fenomen Seçimi, Birlikte Al Kazan vb. direkt alınır.

        # --- FAVORİ VE SATIŞ BİLGİSİ ---
        # Ana dizindeki net rakamı almaya öncelik veriyoruz (23K yerine 23000 almak için)
        fav = p.get("favoriteCount", 0)
        orders = "-"
        
        for s in p.get("socialProof", []):
            if s.get("key") == "orderCount": 
                orders = s.get("value", "-")
            # Eğer ana dizinde favori yoksa socialProof içindekini ("23K" olanı) yedek olarak al
            if s.get("key") == "favoriteCount" and fav == 0:
                fav = s.get("value", "-")
        
        # --- YORUM SAYISI VE PUAN ---
        rating_obj = p.get("ratingScore", {})
        if isinstance(rating_obj, dict):
            review_count = rating_obj.get("totalCount", 0)
            rating_avg = rating_obj.get("averageRating", 0)
        else:
            review_count = p.get("ratingCount", 0)
            rating_avg = rating_obj

        parsed_list.append({
            "Ürün Adı": p.get("name", "Bilinmiyor"),
            "Marka": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand", "-"),
            "Sıralama/Rozet": badge_text,
            "Fiyat (TL)": price,
            "Favori": fav,
            "Yorum Sayısı": review_count,
            "Satış Bilgisi": orders,
            "Puan": rating_avg,
            "Link": "https://www.trendyol.com" + p.get("url", "")
        })
    return pd.DataFrame(parsed_list)

# --- ARAYÜZ TASARIMI ---
st.title("🛡️ Trendyol Akıllı Veri Çözücü v5")

if 'main_df' not in st.session_state:
    st.session_state.main_df = pd.DataFrame()

col1, col2 = st.columns([4, 1])
with col1:
    raw_text = st.text_area("Bookmarklet verisini buraya yapıştırın:", height=150)
with col2:
    if st.button("➕ Listeye Ekle"):
        if raw_text:
            try:
                data = json.loads(raw_text.strip())
                new_df = smart_parse(data)
                # Yeni ürünleri ekle ve mükerrerleri sil
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_df]).drop_duplicates(subset=['Link'])
                st.success("Başarıyla Eklendi!")
            except: 
                st.error("Veri okunamadı. Hatalı format.")
    if st.button("🗑️ Temizle"):
        st.session_state.main_df = pd.DataFrame()
        st.rerun()

if not st.session_state.main_df.empty:
    df = st.session_state.main_df
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Ürün", len(df))
    
    st.download_button("📥 Excel Raporu Al", to_excel(df), "trendyol_rapor.xlsx")
    
    # Tablo yüksekliğini (height) 800 piksel yaparak tek seferde 25-30 ürün görünmesini sağladık
    st.dataframe(df, use_container_width=True, height=800)
