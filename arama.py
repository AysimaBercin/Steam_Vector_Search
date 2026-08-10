import pyodbc
import json
from sentence_transformers import SentenceTransformer

print("1. Arama motoru için yapay zeka modeli yükleniyor...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("2. SQL Server veritabanına bağlanılıyor...")
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=VectorDB_Project;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

print("\n" + "="*60)
print("🚀 STEAM ANLAMSAL VEKTÖR ARAMA MOTORU AKTİF")
print("="*60)

while True:
    arama_metni = input("\n🔍 Aramak istediğiniz oyun ifadesi (Çıkış için 'q'): ")

    if arama_metni.lower() == 'q':
        print("Sistem kapatılıyor. Başarılar!")
        break

    if not arama_metni.strip():
        continue

    vector_data = model.encode(arama_metni).tolist()
    vector_string = json.dumps(vector_data)

    # Sonuç limitini en az 10 olacak şekilde güncelledik
    sql_sorgusu = """
        DECLARE @AramaVektoru VECTOR(384) = CAST(? AS NVARCHAR(MAX));

        SELECT TOP 10 
            OyunAdi, 
            Turler,
            VECTOR_DISTANCE('cosine', @AramaVektoru, Vektor) AS BenzerlikSkoru
        FROM dbo.SteamOyunlari
        ORDER BY BenzerlikSkoru ASC;
    """

    try:
        cursor.execute(sql_sorgusu, (vector_string,))
        sonuclar = cursor.fetchall()

        print(f"\n--- '{arama_metni}' İçin En İyi 10 Eşleşme ---")
        for satir in sonuclar:
            print(f"🎮 Oyun: {satir.OyunAdi}")
            print(f"🏷️ Türler: {satir.Turler}")
            print(f"📊 Benzerlik Skoru (Cosine Mesafesi): {satir.BenzerlikSkoru:.4f}")
            print("-" * 50)

    except Exception as e:
        print(f"Arama sırasında hata oluştu: {e}\n")

cursor.close()
conn.close()