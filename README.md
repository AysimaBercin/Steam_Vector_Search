# Steam Vector Search 🚀

Bu proje, **SQL Server 2025**'in native vektör veritabanı özelliklerini ve **Doğal Dil İşleme (NLP)** tekniklerini kullanarak, 137.000'den fazla Steam oyunu üzerinde çalışan çok dilli bir semantik (anlamsal) arama motorudur. 

Geleneksel kelime eşleştirme (LIKE) yöntemleri yerine, kullanıcı sorgularını anlamsal vektörlere dönüştürerek oyunların türleri, kategorileri ve içerikleriyle "anlam" üzerinden eşleştirir.

## 🎯 Projenin Öne Çıkan Özellikleri

*   **Büyük Veri İşleme:** 137.000+ satırlık devasa veri seti, bellek yönetimi (batch processing) kullanılarak veritabanına aktarılmıştır.
*   **Çok Dilli NLP:** `paraphrase-multilingual-MiniLM-L12-v2` modeli kullanılarak 50'den fazla dilde yapılan aramalar, İngilizce veri setiyle anlamsal olarak eşleştirilir.
*   **Vektör Veritabanı:** SQL Server 2025'in vektör yetenekleri (`VECTOR_DISTANCE`) kullanılarak Cosine Similarity (Kosinüs Benzerliği) üzerinden yüksek performanslı arama gerçekleştirilir.
*   **Profesyonel Arayüz:** Streamlit kullanılarak sade, hızlı ve veri odaklı bir kullanıcı deneyimi tasarlanmıştır.

## 🛠️ Kullanılan Teknolojiler

*   **Veritabanı:** SQL Server 2025 (Native Vector Support)
*   **Programlama Dili:** Python 3
*   **Yapay Zeka Modeli:** sentence-transformers (Hugging Face)
*   **Arayüz:** Streamlit
*   **Veri Manipülasyonu:** Pandas
*   **Veritabanı Bağlantısı:** PyODBC

## 📂 Proje Dosyaları

*   `app.py`: Streamlit tabanlı kullanıcı arayüzü ve arama motoru motoru ana kodları.
*   `veri_hazirla.py`: Ham veri setlerini (CSV) birleştirip vektörleştiren ve veritabanına aktaran ETL (Extract, Transform, Load) betiği.
*   `arama.py`: Terminal üzerinden hızlı testler yapmak için kullanılan CLI arama scripti.

## ⚙️ Kurulum ve Çalıştırma

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install pandas pyodbc sentence-transformers streamlit
