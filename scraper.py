import streamlit as st
import pandas as pd
import plotly.express as px
import re
import json

st.set_page_config(page_title="Trendyol Analiz", layout="wide")

st.title("🚀 Trendyol Veri Analiz Paneli")

tab1, tab2 = st.tabs(["Otomatik Çek (API)", "Veri Yapıştır (Manuel)"])

with tab1:
    st.info("Trendyol bazen bulut sunucuları engelleyebilir. Eğer çalışmazsa Manuel sekmesini kullanın.")
    # Mevcut çekme kodun burada kalsın...

with tab2:
    st.subheader("📝 Trendyol Sayfa Verisini Yapıştır")
    st.markdown("""
    **Nasıl Yapılır?**
    1. Trendyol kategorisine gir. 2. `F12` tuşuna bas (İncele). 3. `Network` sekmesine tıkla.
    4. Sayfayı yenile. 5. `filter` yazan isteğe sağ tıkla -> `Copy Response`. 6. Buraya yapıştır.
    """)
    raw_data = st.text_area("JSON Verisini Buraya Yapıştırın", height=200)
    
    if st.button("Veriyi Çözümle"):
        try:
            data = json.loads(raw_data)
            products = data.get("content", [])
            all_products = []
            for p in products:
                all_products.append({
                    "Ürün": p.get("name"),
                    "Marka": p.get("brand", {}).get("name"),
                    "Fiyat": p.get("price", {}).get("sellingPrice"),
                    "Favori": p.get("favoriteCount"),
                    "Yorum": p.get("ratingCount")
                })
            df = pd.DataFrame(all_products)
            st.success(f"{len(df)} ürün başarıyla ayıklandı!")
            st.plotly_chart(px.bar(df.nlargest(10, 'Favori'), x='Favori', y='Ürün', orientation='h'))
            st.dataframe(df)
        except:
            st.error("Veri formatı hatalı. Lütfen Trendyol Network yanıtını (JSON) yapıştırdığınızdan emin olun.")
