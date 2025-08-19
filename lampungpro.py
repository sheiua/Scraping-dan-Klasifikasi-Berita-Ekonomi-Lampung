from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# URL target
url = "https://www.rmollampung.id/category/daerah"
print(f"🔄 Membuka {url}")
driver.get(url)
time.sleep(3)  # Tunggu konten termuat

# Simpan halaman ke file
html_source = driver.page_source
with open("rmollampung_page1.html", "w", encoding="utf-8") as f:
    f.write(html_source)

print("✅ Halaman disimpan sebagai 'rmollampung_page1.html'")
driver.quit()
