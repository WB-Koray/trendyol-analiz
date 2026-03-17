import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="Trendyol Veri Analizi", layout="wide")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol_Rapor')
    return output.getvalue()

st.title("🛡️ Trendyol Akıllı Veri Çözücü")

raw_input = st.text_area("JSON Verisini buraya yapıştırın:", height=250)

if st.button("🚀 Verileri Analiz Et"):
    if raw_input:
        try:
            js_data = json.loads(raw_input.strip())
            products = js_data.get("products", js_data.get("content", []))
            
            if not products and "data" in js_data:
                products = js_data["data"].get("products", [])

            data_list = []
            for p in products:
                # 1. Fiyat Yakalama
                price_obj = p.get("price", {})
                current_price = price_obj.get("current", price_obj.get("sellingPrice", price_obj.get("originalPrice", 0)))
                
                # 2. Marka Yakalama
                brand = p.get("brand", "-")
                brand_name = brand.get("name") if isinstance(brand, dict) else brand

                # 3. Favori ve Diğer Sosyal Kanıtları Yakalama (socialProof listesinden)
                fav_count = p.get("favoriteCount", 0)
                order_count = "-"
                
                social_proofs = p.get("socialProof", [])
                for proof in social_proofs:
                    if proof.get("key") == "favoriteCount":
                        fav_count = proof.get("value", fav_count)
                    if proof.get("key") == "orderCount":
                        order_count = proof.get("value", "-")

                # 4. Yorum ve Puan
                rating_obj = p.get("ratingScore", {})
                rating_avg = rating_obj.get("averageRating", 0) if isinstance(rating_obj, dict) else p.get("ratingScore", 0)
                review_count = rating_obj.get("totalCount", p.get("ratingCount", 0))

                data_list.append({
                    "Ürün Adı": p.get("name"),
                    "Marka": brand_name,
                    "Fiyat (TL)": current_price,
                    "Favori": fav_count,
                    "Yorum": review_count,
                    "Satış Bilgisi": order_count,
                    "Puan": rating_avg,
                    "Link": "https://www.trendyol.com" + p.get("url", "")
                })
            
            df = pd.DataFrame(data_list)
            st.success(f"✅ {len(df)} adet ürün başarıyla analiz edildi!")
            
            # İstatistik Kartları
            c1, c2, c3 = st.columns(3)
            c1.metric("Ürün Sayısı", len(df))
            c2.metric("En Yüksek Fiyat", f"{df['Fiyat (TL)'].max()} TL")
            c3.metric("En Popüler Ürün (Favori)", df['Favori'].max())

            # İndirme Butonu
            st.download_button("📥 Excel Raporunu İndir", to_excel(df), "trendyol_best_seller.xlsx")
            
            # Veri Tablosu
            st.subheader("📋 Ürün Listesi")
            st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Veri işlenirken hata oluştu: {e}")
    else:
        st.warning("Lütfen kutuya veri ekleyin.")
