from parser_rmol import parse_rmol_lampung
from parser_detik import parse_detik_lampung
from parsersAntara import parse_antara
from lampost_parser import parse_lampost
import pandas as pd
import joblib
import os

# Load model dan vectorizer
def load_model_and_vectorizer():
    model = joblib.load("model_berita_svm2.pkl")
    vectorizer = joblib.load("tfidf_vectorizer.pkl")
    return model, vectorizer

model, vectorizer = load_model_and_vectorizer()

def scrape_dan_klasifikasi(start_date, end_date, max_articles=5, max_pages=1):
    df_rmol = parse_rmol_lampung(start_date, end_date, max_articles, max_pages, simpan=False)
    df_detik = parse_detik_lampung(start_date, end_date, max_articles, max_pages, simpan=False)
    df_antara = parse_antara(start_date, end_date, max_articles, max_pages, simpan=False)
    df_lampost = parse_lampost(start_date, end_date, max_articles, max_pages, simpan=False)

    df_all = pd.concat([df_rmol, df_detik, df_antara, df_lampost], ignore_index=True)

    if df_all.empty:
        return None, None

    df_all = df_all[df_all['isi'].notna() & df_all['isi'].str.strip().ne('')]
    if df_all.empty:
        return None, None

    df_all['label'] = model.predict(df_all['isi'])
    df_ekonomi = df_all[df_all['label'] == 1]

    return df_all, df_ekonomi
