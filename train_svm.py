import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# ✅ Import preprocessor dari file eksternal
from text_preprocessor import TextPreprocessor

# ========================
# 1. Load Data
# ========================
df = pd.read_excel("label_baru.xlsx")
kolom_teks = "5. APA yang terjadi pada fenomena ekonomi yang ditemukan ?"
kolom_label = "Label_Ekonomi"

# Buang data kosong
df_clean = df.dropna(subset=[kolom_teks, kolom_label])
X = df_clean[kolom_teks].fillna("")
y = df_clean[kolom_label].astype(int)

# ========================
# 2. Split Data
# ========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ========================
# 3. Buat Pipeline (Preprocessing + TF-IDF + SVM)
# ========================
pipeline = make_pipeline(
    TextPreprocessor(),  # Preprocessing custom
    TfidfVectorizer(max_features=5000, ngram_range=(1, 2)),
    LinearSVC()
)

# Latih model
pipeline.fit(X_train, y_train)
print("✅ Model SVM dengan preprocessing selesai dilatih.")

# ========================
# 4. Evaluasi
# ========================
y_pred = pipeline.predict(X_test)
print("📊 Hasil Evaluasi:\n")
print(classification_report(y_test, y_pred))

# ========================
# 5. Simpan Pipeline Model
# ========================
joblib.dump(pipeline, "model_berita_svm2.pkl")
print("💾 Model pipeline disimpan sebagai 'model_berita_svm2.pkl'")

# ========================
# 6. Simpan Vectorizer Saja (Opsional)
# ========================
vectorizer = pipeline.named_steps['tfidfvectorizer']
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
print("💾 Vectorizer disimpan sebagai 'tfidf_vectorizer.pkl'")
