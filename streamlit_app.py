import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="Trendyol Veri Analiz", layout="wide")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol_Analiz')
    return output.getvalue()

st.title("🛡️ Trendyol Akıllı Veri Çözücü")
st.markdown("Verileri aşağıya yapıştırın.")

raw_input = st.text_area("JSON Metni:", height=250)

if st.button("🚀 Analiz Et"):
    if raw_input:
        try:
            js_data = json.loads(raw_input.strip())
            products = js_data.get("products", js_data.get("content", []))
            
            if not products and "data" in js_data:
                products = js_data["data"].get("products", [])

            data_list = []
            for p in products:
                # Fiyat çekme mantığını esnetiyoruz
                p_obj = p.get("price", {})
                s_price = p_obj.get("sellingPrice", p_obj.get("originalPrice", 0))
                o_price = p_obj.get("originalPrice", 0)
                
                # Markayı çekme
                brand = p.get("brand")
                brand_name = brand.get("name") if isinstance(brand, dict) else brand
                
                # Değerlendirme puanı
                rating = p.get("ratingScore", 0)
                if isinstance(rating, dict): rating = rating.get("averageRating", 0)

                data_list.append({
                    "Ürün Adı": p.get("name"),
                    "Marka": brand_name if brand_name else "-",
                    "Fiyat (TL)": s_price,
                    "Eski Fiyat": o_price,
                    "Favori": p.get("favoriteCount", 0),
                    "Yorum": p.get("ratingCount", 0),
                    "Puan": rating,
                    "Link": "https://www.trendyol.com" + p.get("url", "")
                })
            
            df = pd.DataFrame(data_list)
            st.success(f"✅ {len(df)} ürün ayıklandı!")
            
            # İndirme ve Tablo
            st.download_button("📥 Excel Olarak İndir", to_excel(df), "trendyol_rapor.xlsx")
            st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Hata: {e}")
