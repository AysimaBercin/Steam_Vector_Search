import streamlit as st
import pyodbc
import json
from sentence_transformers import SentenceTransformer

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Steam Vector Search",
    layout="wide"
)

# Modelin Önbelleğe Alınması
@st.cache_resource
def load_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

model = load_model()

# Yan Menü - Sistem ve Veritabanı Bilgileri
with st.sidebar:
    st.header("Sistem Mimarisi")
    st.markdown("---")
    st.write("**Veritabanı:** SQL Server 2025")
    st.write("**Aktif Kayıt:** 137,000+ Oyun")
    st.write("**Vektör Modeli:** Multilingual MiniLM")
    st.write("**Metrik:** Cosine Distance")

# Ana Ekran Başlığı ve Açıklama
st.title("Steam Vector Search")
st.markdown("137.000+ Steam oyunu üzerinde doğal dil işleme tabanlı anlamsal arama sistemi.")
st.markdown("---")

# Arama Giriş Alanı
query = st.text_input(
    "Arama Sorgusu",
    placeholder="Örn: küçük bir şehir kurup insanları yönettiğim simülasyon oyunu"
)

# Arama Butonu (Sade düzen)
col_btn, _ = st.columns([1, 6])
with col_btn:
    search_triggered = st.button("Sorgula", type="primary", use_container_width=True)

if search_triggered:
    if query.strip():
        with st.spinner("Vektör uzayında anlamsal tarama gerçekleştiriliyor..."):
            # Metni vektöre dönüştürme
            vector_data = model.encode(query).tolist()
            vector_string = json.dumps(vector_data)

            # Güvenli ve taze veritabanı bağlantısı
            conn = pyodbc.connect(
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=localhost;"
                "Database=VectorDB_Project;"
                "Trusted_Connection=yes;"
            )
            cursor = conn.cursor()

            sql_sorgusu = """
                DECLARE @AramaVektoru VECTOR(384) = CAST(? AS NVARCHAR(MAX));

                SELECT TOP 10 
                    OyunAdi, 
                    Turler,
                    Kategoriler,
                    VECTOR_DISTANCE('cosine', @AramaVektoru, Vektor) AS BenzerlikSkoru
                FROM dbo.SteamOyunlari
                ORDER BY BenzerlikSkoru ASC;
            """

            cursor.execute(sql_sorgusu, (vector_string,))
            sonuclar = cursor.fetchall()
            cursor.close()
            conn.close()

            # Sonuçların Listelenmesi
            if sonuclar:
                st.markdown(f"**'{query}'** için en yakın eşleşmeler:")
                st.markdown("---")
                
                for i, satir in enumerate(sonuclar):
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.subheader(f"{i+1}. {satir.OyunAdi}")
                        st.write(f"**Türler:** {satir.Turler}")
                        st.write(f"**Kategoriler:** {satir.Kategoriler}")
                    with col2:
                        st.metric(label="Mesafe Skoru", value=f"{satir.BenzerlikSkoru:.4f}")
                    with col3:
                        benzerlik_yuzdesi = (1 - satir.BenzerlikSkoru) * 100
                        st.metric(label="Benzerlik Oranı", value=f"%{benzerlik_yuzdesi:.2f}")
                    st.markdown("---")
            else:
                st.info("Eşleşen kayıt bulunamadı.")
    else:
        st.error("Lütfen geçerli bir arama ifadesi girin.")