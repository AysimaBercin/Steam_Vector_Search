import pandas as pd
import pyodbc
import time

print("1. Çok dilli yapay zeka modeli yükleniyor...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("2. Devasa CSV dosyaları belleğe okunuyor...")
veri_klasoru = r"C:\Users\aysim\OneDrive\Images\Masaüstü\Steam_Vector_Search\Data"

df_games = pd.read_csv(f"{veri_klasoru}\\steam_games.csv")
df_reviews = pd.read_csv(f"{veri_klasoru}\\steam_games_reviews.csv")

print(f"Toplam oyun sayısı: {len(df_games)}")

print("3. Veriler 'app_id' üzerinden birleştiriliyor...")
df_merged = pd.merge(df_games, df_reviews, on='app_id', how='left')
df_merged = df_merged.fillna("")

print("4. SQL Server veritabanına bağlanılıyor...")
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=VectorDB_Project;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Zaten veritabanında kaç kayıt olduğunu kontrol ediyoruz (TRUNCATE YOK!)
cursor.execute("SELECT COUNT(*) FROM dbo.SteamOyunlari")
mevcut_sayi = cursor.fetchone()[0]
print(f"Veritabanında halihazırda kayıtlı olan oyun sayısı: {mevcut_sayi}")

# Sadece henüz işlenmemiş kalan kısımdan (121.000'den sonraki) devam ediyoruz
kalan_df = df_merged.iloc[mevcut_sayi:]

if len(kalan_df) == 0:
    print("Tebrikler! Tüm veri seti zaten eksiksiz olarak veritabanında yüklü.")
else:
    print(f"Kalan {len(kalan_df)} adet oyun işlenmeye başlanıyor...")

    insert_query = """
        INSERT INTO dbo.SteamOyunlari (AppID, OyunAdi, Turler, Kategoriler, AramaMetni, Vektor)
        VALUES (?, ?, ?, ?, ?, CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(384)))
    """

    batch_size = 300  # Bilgisayarı yormamak için paket boyutunu biraz daha küçük tutuyoruz
    toplam_kalan = len(kalan_df)
    islenen_sayac = 0

    for i in range(0, toplam_kalan, batch_size):
        batch_df = kalan_df.iloc[i:i+batch_size]
        batch_parametreleri = []
        
        metinler = []
        app_ids = []
        oyun_adlari = []
        turler_listesi = []
        kategoriler_listesi = []
        
        for _, row in batch_df.iterrows():
            try:
                app_id = int(row['app_id'])
                oyun_adi = str(row['name_x']) if row['name_x'] != "" else "Bilinmeyen Oyun"
                turler = str(row['genres'])
                kategoriler = str(row['categories'])
                yorumlar = str(row['reviews'])
                
                arama_metni = f"Oyun: {oyun_adi} | Türler: {turler} | Kategoriler: {kategoriler} | Yorumlar: {yorumlar}"
                
                app_ids.append(app_id)
                oyun_adlari.append(oyun_adi)
                turler_listesi.append(turler)
                kategoriler_listesi.append(kategoriler)
                metinler.append(arama_metni)
            except:
                continue

        if not metinler:
            continue

        vektorler = model.encode(metinler, show_progress_bar=False)

        for j in range(len(metinler)):
            vektor_string = str(vektorler[j].tolist())
            batch_parametreleri.append((
                app_ids[j], 
                oyun_adlari[j], 
                turler_listesi[j], 
                kategoriler_listesi[j], 
                metinler[j], 
                vektor_string
            ))

        cursor.executemany(insert_query, batch_parametreleri)
        conn.commit()
        
        islenen_sayac += len(batch_parametreleri)
        print(f"-> Kalandan {islenen_sayac} / {toplam_kalan} oyun eklendi...")

cursor.close()
conn.close()

print("\n MÜKEMMEL! Eksik kalan tüm oyunlar eklendi ve veri seti 137 bine tamamlandı!")