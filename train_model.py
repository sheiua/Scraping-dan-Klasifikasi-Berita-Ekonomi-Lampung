import pandas as pd
import re
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# === Tambahan untuk preprocessing ===
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi stopwords dan stemmer
stop_factory = StopWordRemoverFactory()
stem_factory = StemmerFactory()
stopwords = set(stop_factory.get_stop_words())
stemmer = stem_factory.create_stemmer()

# Fungsi preprocessing
def preprocess(text):
    text = text.lower()  # lowercase
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # hapus angka & simbol
    words = text.split()
    words = [word for word in words if word not in stopwords]  # hapus stopwords
    text = ' '.join(words)
    text = stemmer.stem(text)  # stemming
    return text

# === 1. Load Data ===
data = pd.read_excel("hasil_label.xlsx")
data = data.dropna(subset=[data.columns[5], 'Label'])

X = data.iloc[:, 5].astype(str)
y = data['Label'].astype(int)

# === 2. Preprocessing Text ===
print("🔧 Preprocessing data...")
X = X.apply(preprocess)

# === 3. TF-IDF Vectorization ===
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2)
)
X_vec = vectorizer.fit_transform(X)

# === 4. Split data untuk evaluasi ===
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

# === 5. Latih model SVM dengan class_weight untuk menangani imbalance ===
model = LinearSVC(class_weight='balanced')
model.fit(X_train, y_train)

# === 6. Evaluasi performa ===
y_pred = model.predict(X_test)
print("\n📊 Hasil Evaluasi:\n")
print(classification_report(y_test, y_pred))

# === 7. Simpan model dan vectorizer ===
joblib.dump(model, "model_berita_svm2.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("\n✅ Model dan vectorizer berhasil disimpan ke file.")
