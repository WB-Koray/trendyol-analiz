import streamlit as st
import pandas as pd
import json
import re
from io import BytesIO

st.set_page_config(page_title="Trendyol Veri Ayıklayıcı", layout="wide")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trendyol')
    return output.getvalue()

st.title("🛡️ Trendyol Akıllı Veri Çözücü")
st.markdown("Trendyol sayfasından kopyaladığınız karmaşık metni aşağıya yapıştırın.")

raw_input = st.text_area("Metni buraya yapıştırın:", height=300)

if st.button("🚀 Analizi Başlat"):
    if not raw_input:
        st.warning("Lütfen metin kutusunu doldurun.")
    else:
        content = []
        try:
            # 1. DENEME: Saf JSON (Filter dosyası)
            if raw_input.strip().startswith('{'):
                js = json.loads(raw_input)
                content = js.get("content", js.get("products", []))
            
            # 2. DENEME: HTML içinden PROPS yakalama (Kapsamlı Regex)
            if not content:
                # Metin içindeki JSON bloğunu daha geniş bir aralıkta arıyoruz
                match = re.search(r'__single-search-result__PROPS\"\s*:\s*({.*?})["\s]*[,<]', raw_input)
                if match:
                    js = json.loads(match.group(1))
                    # Trendyol'un props yapısı: data -> products
                    content = js.get("data", {}).get("products", [])
                
            # 3. DENEME: Alternatif SEARCH_APP_INITIAL_STATE
            if not content:
                match = re.search(r'__SEARCH_APP_INITIAL_STATE__\s*=\s*({.*?});', raw_input)
                if match:
                    js = json.loads(match.group(1))
                    content = js.get("products", [])

            if content:
                data_list = []
                for p in content:
                    data_list.append({
                        "Ürün Adı": p.get("name"),
                        "Marka": p.get("brand", {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand", "-"),
                        "Fiyat": p.get("price", {}).get("sellingPrice", 0),
                        "Favori": p.get("favoriteCount", 0),
                        "Yorum": p.get("ratingCount", 0),
                        "Puan": p.get("ratingScore", 0)
                    })
                
                df = pd.DataFrame(data_list)
                st.success(f"✅ Başarıyla {len(df)} ürün bulundu!")
                st.download_button("📥 Excel Olarak İndir", to_excel(df), "trendyol_liste.xlsx")
                st.dataframe(df, use_container_width=True)
            else:
                st.error("❌ Üzgünüm, bu metin bloğunda ürün verisine rastlanmadı. Lütfen Trendyol Network panelindeki dosyayı (sağ tık -> Copy response) kopyaladığınızdan emin olun.")
        
        except Exception as e:
            st.error(f"⚠️ Veri işlenirken bir hata oluştu. Lütfen metnin tamamını kopyaladığınızdan emin olun. (Hata: {str(e)})")
