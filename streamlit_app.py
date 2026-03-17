import streamlit as st
import pandas as pd
import json
import re
from io import BytesIO

st.set_page_config(page_title="Trendyol Analiz", layout="wide")

# Excel indirme fonksiyonu
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Veri')
    return output.getvalue()

st.title("🚀 Trendyol Manuel Veri Çözücü")

st.info("Trendyol Network panelinden kopyaladığınız 'HTML' veya 'JSON' metni aşağıya yapıştırın.")

raw_input = st.text_area("Veriyi buraya yapıştırın (<!DOCTYPE html> ile başlayan metin dahil olabilir):", height=300)

if st.button("🔍 Veriyi Çözümle ve Analiz Et"):
    if not raw_input:
        st.warning("Lütfen önce bir veri yapıştırın.")
    else:
        try:
            content = []
            # 1. Senaryo: Saf JSON verisi gelmişse
            if raw_input.strip().startswith('{'):
                js_data = json.loads(raw_input)
                content = js_data.get("content", js_data.get("products", []))
            
            # 2. Senaryo: HTML (Az önce gönderdiğin metin) gelmişse
            else:
                # Metnin içindeki gizli veri kutusunu buluyoruz
                found = re.search(r'__single-search-result__PROPS\"\s*:\s*({.*?})<', raw_input)
                if not found:
                    found = re.search(r'__SEARCH_APP_INITIAL_STATE__\s*=\s*({.*?});', raw_input)
                
                if found:
                    cleaned_json = found.group(1)
                    js_data = json.loads(cleaned_json)
                    # HTML içindeki yapı farklıdır, 'products' veya 'data.products' altında olur
                    content = js_data.get("products", js_data.get("data", {}).get("products", []))

            if content:
                all_products = []
                for p in content:
                    all_products.append({
                        "Ürün Adı": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand", "-"),
                        "Fiyat": p.get("price", {}).get("sellingPrice", 0),
                        "Favori": p.get("favoriteCount", 0),
                        "Yorum Sayısı": p.get("ratingCount", 0)
                    })
                
                df = pd.DataFrame(all_products)
                st.success(f"✅ Başarılı! {len(df)} adet ürün ayıklandı.")
                
                # Excel İndir
                st.download_button("📥 Excel Olarak İndir", to_excel(df), "trendyol_liste.xlsx")
                
                # Tabloyu Göster
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Metin içinde ürün verisi bulunamadı. Lütfen doğru dosyayı (sr? veya filter?) kopyaladığınızdan emin olun.")
        
        except Exception as e:
            st.error(f"⚠️ Bir hata oluştu: Metin formatı beklenen yapıda değil. (Detay: {str(e)})")
