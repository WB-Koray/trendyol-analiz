import streamlit as st
import pandas as pd
import json
import re
from io import BytesIO

st.set_page_config(page_title="Trendyol Veri Analiz", layout="wide")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol_Analiz')
    return output.getvalue()

st.title("🛡️ Trendyol Akıllı Veri Çözücü (Saf Veri Modu)")
st.markdown("Trendyol Network -> **filter** veya **sr** dosyasından kopyaladığınız JSON metni buraya yapıştırın.")

raw_input = st.text_area("JSON Verisini buraya yapıştırın:", height=300)

if st.button("🚀 Verileri Analiz Et ve Excel Hazırla"):
    if not raw_input:
        st.warning("Lütfen metin kutusuna veri yapıştırın.")
    else:
        try:
            # Metin temizleme (Başta veya sonda gereksiz karakter varsa)
            clean_text = raw_input.strip()
            
            # JSON Çözümleme
            js_data = json.loads(clean_text)
            
            # Trendyol JSON yapısında ürünler genelde 'products' veya 'content' altındadır
            products = js_data.get("products", js_data.get("content", []))
            
            if not products and "data" in js_data:
                products = js_data["data"].get("products", [])

            if products:
                data_list = []
                for p in products:
                    # Derin verileri çekme (Hata almamak için .get() kullanıyoruz)
                    price_info = p.get("price", {})
                    brand_info = p.get("brand", {})
                    rating_info = p.get("ratingScore", {}) # Bazı paketlerde bu sözlüktür
                    
                    data_list.append({
                        "Ürün Adı": p.get("name", "Bilinmiyor"),
                        "Marka": brand_info.get("name", brand_info) if isinstance(brand_info, dict) else brand_info,
                        "Satış Fiyatı": price_info.get("sellingPrice", 0),
                        "Orijinal Fiyat": price_info.get("originalPrice", 0),
                        "Favori Sayısı": p.get("favoriteCount", 0),
                        "Yorum Sayısı": p.get("ratingCount", 0),
                        "Puan": p.get("ratingScore", 0) if not isinstance(rating_info, dict) else rating_info.get("averageRating", 0),
                        "Ürün ID": p.get("id", ""),
                        "Link": "https://www.trendyol.com" + p.get("url", "")
                    })
                
                df = pd.DataFrame(data_list)
                
                # Görselleştirmeler ve Özet
                st.success(f"✅ Analiz Başarılı! {len(df)} adet ürün tüm detaylarıyla ayıklandı.")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Ortalama Fiyat", f"{round(df['Satış Fiyatı'].mean(), 2)} TL")
                c2.metric("En Çok Favori", int(df['Favori Sayısı'].max()))
                c3.metric("Toplam Yorum", int(df['Yorum Sayısı'].sum()))

                # İndirme Butonu
                excel_data = to_excel(df)
                st.download_button(
                    label="📥 Tüm Verileri Excel Olarak İndir",
                    data=excel_data,
                    file_name="trendyol_detayli_analiz.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Tablo
                st.subheader("📋 Ayıklanan Ürün Listesi")
                st.dataframe(df, use_container_width=True)
                
            else:
                st.error("❌ Yapıştırılan metin içerisinde ürün listesi bulunamadı. Lütfen 'filter' yanıtının tamamını kopyaladığınızdan emin olun.")
        
        except Exception as e:
            st.error(f"⚠️ Veri işleme hatası! JSON formatı bozuk olabilir. Hata: {str(e)}")
