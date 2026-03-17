import streamlit as st
import pandas as pd
import plotly.express as px
import json
from io import BytesIO
from scraper import get_trendyol_data  # scraper.py'dan fonksiyonu çağırıyoruz

st.set_page_config(page_title="Trendyol Analiz", layout="wide")

# Excel indirme yardımcısı
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Veriler')
    return output.getvalue()

st.title("🚀 Trendyol Ürün Analiz Paneli")

# Sekme Yapısı
tab1, tab2 = st.tabs(["🌐 Otomatik Analiz", "📝 Manuel Veri Yapıştır"])

with tab1:
    st.sidebar.header("Ayarlar")
    cat_id = st.sidebar.text_input("Kategori ID (Örn: 104024)", "104024")
    page_count = st.sidebar.slider("Sayfa Sayısı", 1, 5, 2)
    
    if st.sidebar.button("Analizi Başlat"):
        with st.spinner("Veriler çekiliyor..."):
            df = get_trendyol_data(cat_id, page_count)
            if not df.empty:
                st.success(f"{len(df)} ürün bulundu!")
                st.download_button("📥 Excel Olarak İndir", to_excel(df), "trendyol_veri.xlsx")
                
                fig = px.bar(df.nlargest(10, 'Favori'), x='Favori', y='Ürün', orientation='h', color='Fiyat', title="En Çok Favorilenenler")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Otomatik veri çekilemedi. Trendyol engellemiş olabilir. Lütfen 'Manuel Veri Yapıştır' sekmesini deneyin.")

with tab2:
    st.subheader("Trendyol JSON Verisini Yapıştır")
    st.info("Trendyol'da F12 -> Network -> 'filter' dosyasına sağ tık -> Copy Response yapıp buraya yapıştırın.")
    
    raw_json = st.text_area("JSON içeriğini buraya ekleyin:", height=200)
    
    if st.button("Veriyi Çözümle"):
        try:
            js_data = json.loads(raw_json)
            content = js_data.get("content", [])
            manual_list = []
            for item in content:
                manual_list.append({
                    "Ürün": item.get("name"),
                    "Marka": item.get("brand", {}).get("name"),
                    "Fiyat": item.get("price", {}).get("sellingPrice"),
                    "Favori": item.get("favoriteCount")
                })
            df_m = pd.DataFrame(manual_list)
            st.success(f"{len(df_m)} ürün ayıklandı!")
            st.plotly_chart(px.bar(df_m.nlargest(10, 'Favori'), x='Favori', y='Ürün', orientation='h'))
            st.dataframe(df_m)
        except Exception as e:
            st.error(f"Hata: Veri formatı uyumsuz. {e}")
