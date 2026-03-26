import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="Trendyol Popülerlik Analizi", layout="wide", page_icon="🚀")

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
        
        # Rozet (Badge) Ayıklama: "En Çok Değerlendirilen", "En Çok Satan" vb.
        badge_text = "-"
        # 1. Yöntem: badges -> topRankingBadge
        badges = p.get("badges", {})
        top_badge = badges.get("topRankingBadge", {})
        if top_badge:
            # Örn: "En Çok Satan" + " 1. " + "Ürün"
            badge_text = top_badge.get("title", "")
            
        # 2. Yöntem: Eğer üstteki boşsa 'stamps' kısmına bak
        if badge_text == "-" or not badge_text:
            stamps = p.get("tagDetails", []) # Bazı paketlerde tagDetails altında olur
            for tag in stamps:
                if "encoksatanlar" in tag.get("tag", "").lower() or "ziyaret" in tag.get("tag", "").lower():
                    badge_text = tag.get("displayName", "-")

        # Favori ve Satış
        fav = p.get("favoriteCount", 0)
        orders = "-"
        for s in p.get("socialProof", []):
            if s.get("key") == "favoriteCount": fav = s.get("value", fav)
            if s.get("key") == "orderCount": orders = s.get("value", "-")
        
        parsed_list.append({
            "Ürün Adı": p.get("name", "Bilinmiyor"),
            "Marka": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand", "-"),
            "Rozet/Sıralama": badge_text, # Aradığın o turuncu şerit bilgisi
            "Fiyat (TL)": price,
            "Favori": fav,
            "Yorum": p.get("ratingCount", 0),
            "Satış Bilgisi": orders,
            "Link": "https://www.trendyol.com" + p.get("url", "")
        })
    return pd.DataFrame(parsed_list)

# --- ANA UYGULAMA ---
st.title("🛡️ Trendyol Akıllı Veri Çözücü v4")
st.markdown("Bookmarklet'ten kopyaladığınız veriyi yapıştırıp **'Listeye Ekle'** butonuna basın.")

if 'main_df' not in st.session_state:
    st.session_state.main_df = pd.DataFrame()

col1, col2 = st.columns([4, 1])
with col1:
    raw_text = st.text_area("Veri Girişi:", height=150)
with col2:
    if st.button("➕ Listeye Ekle"):
        if raw_text:
            try:
                data = json.loads(raw_text.strip())
                new_df = smart_parse(data)
                st.session_state.main_df = pd.concat([st.session_state.main_df, new_df]).drop_duplicates(subset=['Link'])
                st.success("Eklendi!")
            except:
                st.error("Hata!")
    if st.button("🗑️ Temizle"):
        st.session_state.main_df = pd.DataFrame()
        st.rerun()

if not st.session_state.main_df.empty:
    df = st.session_state.main_df
    st.divider()
    st.download_button("📥 Excel Raporu Al", to_excel(df), "trendyol_rozetli_analiz.xlsx")
    st.dataframe(df, use_container_width=True)
