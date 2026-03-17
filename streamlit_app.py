import streamlit as st
from scraper import get_trendyol_data
import plotly.express as px

st.set_page_config(page_title="Trendyol Trend Analizi", layout="wide")
st.title("🚀 Trendyol Ürün Analiz Paneli")

st.sidebar.header("Ayarlar")
cat_id = st.sidebar.text_input("Kategori ID (Örn: 91)", "91")
page_count = st.sidebar.slider("Sayfa Sayısı", 1, 5, 2)

if st.sidebar.button("📊 Analizi Başlat"):
    with st.spinner("Veriler çekiliyor..."):
        df = get_trendyol_data(cat_id, page_count)
        if not df.empty:
            st.success(f"{len(df)} ürün bulundu!")
            
            top_fav = df.nlargest(10, 'Favori')
            fig = px.bar(top_fav, x='Favori', y='Ürün', orientation='h', 
                         title="En Çok Favorilenen İlk 10 Ürün", color='Fiyat')
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Tüm Veriler")
            st.dataframe(df, use_container_width=True)
        else:
            st.error("Veri bulunamadı. Lütfen ID'yi kontrol edin.")
