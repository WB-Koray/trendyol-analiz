import streamlit as st
import pandas as pd
import json
from io import BytesIO
from curl_cffi import requests

st.set_page_config(page_title="Trendyol Akıllı Analiz", layout="wide", page_icon="🚀")

# --- FONKSİYONLAR ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol_Rapor')
    return output.getvalue()

def auto_scrape(api_url):
    headers = {
        "authority": "public.trendyol.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://www.trendyol.com/",
    }
    try:
        # Zırhlı çekme yöntemi
        res = requests.get(api_url, headers=headers, impersonate="chrome120", timeout=30)
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None

def process_data(js_data):
    products = js_data.get("products", js_data.get("content", []))
    if not products and "data" in js_data:
        products = js_data["data"].get("products", [])
    
    data_list = []
    for p in products:
        price_obj = p.get("price", {})
        social_proofs = p.get("socialProof", [])
        fav = p.get("favoriteCount", 0)
        order = "-"
        for s in social_proofs:
            if s.get("key") == "favoriteCount": fav = s.get("value", fav)
            if s.get("key") == "orderCount": order = s.get("value", "-")
            
        data_list.append({
            "Ürün Adı": p.get("name"),
            "Marka": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand", "-"),
            "Fiyat (TL)": price_obj.get("current", price_obj.get("sellingPrice", 0)),
            "Favori": fav,
            "Yorum": p.get("ratingCount", 0),
            "Satış": order,
            "Link": "https://www.trendyol.com" + p.get("url", "")
        })
    return pd.DataFrame(data_list)

# --- ARAYÜZ TASARIMI ---
st.title("🚀 Trendyol Akıllı Veri Çözücü v2")

# Sekmeler Tasarımı Değiştiriyor
tab1, tab2 = st.tabs(["✨ Otomatik Analiz (Hızlı)", "📝 Manuel Veri Yapıştır"])

with tab1:
    st.subheader("🔗 API URL ile Otomatik Çek")
    api_input = st.text_input("Trendyol'dan kopyaladığınız API Linkini (filter?...) buraya yapıştırın:")
    if st.button("Otomatik Veri Çek"):
        if api_input:
            with st.spinner("Zırhlı bot devreye giriyor..."):
                raw = auto_scrape(api_input)
                if raw:
                    df = process_data(raw)
                    st.success(f"{len(df)} ürün başarıyla çekildi!")
                    st.download_button("📥 Excel İndir", to_excel(df), "trendyol_auto.xlsx")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("Trendyol engeline takıldık! Lütfen Manuel Yapıştır sekmesini kullanın.")

with tab2:
    st.subheader("📄 JSON Verisini Manuel Çöz")
    raw_json = st.text_area("Network panelinden kopyaladığınız JSON içeriğini buraya yapıştırın:", height=300)
    if st.button("Yapıştırılan Veriyi Analiz Et"):
        if raw_json:
            try:
                df = process_data(json.loads(raw_json))
                st.success(f"{len(df)} ürün ayıklandı!")
                st.download_button("📥 Excel İndir", to_excel(df), "trendyol_manual.xlsx")
                st.dataframe(df, use_container_width=True)
            except:
                st.error("JSON formatı hatalı!")
