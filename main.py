from parser_rmol import parse_rmol_lampung
from parser_detik import parse_detik_lampung
from parsersAntara import parse_antara
from lampost_parser import parse_lampost

import pandas as pd
import joblib
import os

# Load model dan TF-IDF vectorizer
def load_model_and_vectorizer():
    model_path = "model_berita_svm2.pkl"
    vectorizer_path = "tfidf_vectorizer.pkl"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ File model tidak ditemukan: {model_path}")
    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"❌ File vectorizer tidak ditemukan: {vectorizer_path}")

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model, vectorizer

model, vectorizer = load_model_and_vectorizer()

def main():
    # Input tanggal dari user
    start_date = input("🗓️ Masukkan tanggal mulai (YYYY-MM-DD): ")
    end_date = input("🗓️ Masukkan tanggal akhir (YYYY-MM-DD): ")

    max_articles = 5
    max_pages = 1

    print("\n🚀 Mulai proses scraping...\n")

    # Scrape dari semua portal
    df_rmol = parse_rmol_lampung(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)
    df_detik = parse_detik_lampung(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)
    df_antara = parse_antara(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)
    df_lampost = parse_lampost(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)

    # Gabungkan semua DataFrame
    df_all = pd.concat([df_rmol, df_detik, df_antara, df_lampost], ignore_index=True)

    if not df_all.empty:
        print(f"📝 Total artikel sebelum klasifikasi: {len(df_all)}")

        # Filter isi yang kosong
        df_all = df_all[df_all['isi'].notna() & df_all['isi'].str.strip().ne('')]

        if df_all.empty:
            print("❌ Tidak ada artikel dengan isi valid untuk klasifikasi.")
            return

        # Transform dengan TF-IDF dan prediksi
        X_tfidf = vectorizer.transform(df_all['isi'])
        df_all['label'] = model.predict(X_tfidf)

        # Filter label ekonomi
        df_ekonomi = df_all[df_all['label'] == 1]

        # Simpan hasil
        df_all.to_excel("hasil_semua_portal.xlsx", index=False)
        df_ekonomi.to_excel("Berita_Ekonomi.xlsx", index=False)

        print(f"\n✅ Total artikel setelah filter isi: {len(df_all)}")
        print(f"📊 Jumlah artikel ekonomi: {len(df_ekonomi)}")
        print("📁 File disimpan: hasil_semua_portal.xlsx dan Berita_Ekonomi.xlsx")

    else:
        print("\n❌ Tidak ada artikel yang ditemukan dari semua portal.")

if __name__ == "__main__":
    main()
