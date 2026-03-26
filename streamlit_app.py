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
        pr = p.get("price", {})
        price = pr.get("current", pr.get("sellingPrice", pr.get("originalPrice", 0)))
        
        # --- ROZET AYIKLAMA (Turuncu Şerit) ---
        badge_text = "-"
        badges = p.get("badges", {})
        top_badge = badges.get("topRankingBadge", {})
        if top_badge:
            # "En Çok Satan" + " " + "1."
            badge_text = f"{top_badge.get('type', '')} {top_badge.get('title', '')}".replace('BEST_SELLER', 'En Çok Satan').strip()
        
        if badge_text == "-" or not badge_text:
            tags = p.get("tagDetails", p.get("stamps", []))
            for tag in tags:
                d_name = tag.get("displayName", "")
                if "Satan" in d_name or "Değerlendirilen" in d_name or "Ziyaret" in d_name:
                    badge_text = d_name

        # --- FAVORİ VE SATIŞ ---
        fav = p.get("favoriteCount", 0)
        orders = "-"
        for s in p.get("socialProof", []):
            if s.get("key") == "favoriteCount": fav = s.get("value", fav)
            if s.get("key") == "orderCount": orders = s.get("value", "-")
        
        # --- YORUM SAYISI ---
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

# --- ARAYÜZ ---
st.title("🛡️ Trendyol Akıllı Veri Çözücü v4.1")

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
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_df]).drop_duplicates(subset=['Link'])
                st.success("Eklendi!")
            except: st.error("Hata!")
    if st.button("🗑️ Temizle"):
        st.session_state.main_df = pd.DataFrame()
        st.rerun()

if not st.session_state.main_df.empty:
    df = st.session_state.main_df
    st.divider()
    st.download_button("📥 Excel Raporu Al", to_excel(df), "trendyol_rapor.xlsx")
    st.dataframe(df, use_container_width=True)
