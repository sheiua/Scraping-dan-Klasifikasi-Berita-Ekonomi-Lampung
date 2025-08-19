from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def parse_viva(driver, start_date=None, end_date=None, max_articles=30):
    driver.get("https://lampung.viva.co.id/")
    time.sleep(3)

    # Klik tombol "Muat Lainnya" beberapa kali
    for _ in range(5):  # kamu bisa sesuaikan jumlah klik
        try:
            muat_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a#load-more-btn.btn-more"))
            )
            driver.execute_script("arguments[0].click();", muat_btn)
            time.sleep(2)
        except:
            break

    # Ambil semua link berita setelah semua dimuat
    links = [
        a.get_attribute("href")
        for a in driver.find_elements(By.CSS_SELECTOR, "div.article-list-container h2 a")
        if a.get_attribute("href")
    ]

    results = []
    for link in links[:max_articles]:
        try:
            driver.get(link)
            time.sleep(2)

            judul = driver.find_element(By.CSS_SELECTOR, "h1.main-content-title").text.strip()
            tanggal_raw = driver.find_element(By.CSS_SELECTOR, "div.main-content-date").text.strip()

            # Contoh format: "Selasa, 22 Juli 2025 - 17:20 WIB"
            tanggal_str = tanggal_raw.split(" - ")[0].split(", ")[-1]
            tanggal = datetime.strptime(tanggal_str, "%d %B %Y").date()

            if start_date and end_date and not (start_date <= tanggal <= end_date):
                continue

            paragraf = driver.find_elements(By.CSS_SELECTOR, "div.main-content-detail p")
            isi = "\n".join([p.text.strip() for p in paragraf if p.text.strip()])

            results.append({
                "judul": judul,
                "link": link,
                "tanggal": tanggal,
                "isi": isi
            })

        except Exception as e:
            continue

    return results

def parse_antara(driver, start_date=None, end_date=None, max_pages=3):
    results = []
    base_url = "https://lampung.antaranews.com/lampung-update"

    for page in range(1, max_pages+1):
        url = f"{base_url}?page={page}"
        driver.get(url)
        time.sleep(2)

        links = [a.get_attribute("href") for a in driver.find_elements(By.CSS_SELECTOR, "article.simple-post a") if a.get_attribute("href")]

        for link in links:
            try:
                driver.get(link)
                time.sleep(2)

                judul = driver.find_element(By.CSS_SELECTOR, "h1.post-title").text.strip()
                waktu = driver.find_element(By.CSS_SELECTOR, "time[itemprop='datePublished']").get_attribute("datetime")
                tanggal = datetime.strptime(waktu.split("T")[0], "%Y-%m-%d").date()

                if start_date and end_date and not (start_date <= tanggal <= end_date):
                    continue

                paragraf = driver.find_elements(By.CSS_SELECTOR, "div#content-detail p")
                isi = "\n".join([p.text.strip() for p in paragraf if p.text.strip()])

                results.append({
                    "judul": judul,
                    "link": link,
                    "tanggal": tanggal,
                    "isi": isi
                })

            except Exception as e:
                continue
    return results

def parse_lampungpro(driver, start_date=None, end_date=None, max_pages=3):
    from urllib.parse import quote
    base_url = "https://lampungpro.co/kategori/news/Lampung Raya"
    encoded_url = quote(base_url, safe="/:")
    
    results = []
    for page in range(1, max_pages + 1):
        url = f"{encoded_url}/{page}"
        print(f"[LP] 🔄 Memuat halaman: {url}")
        driver.get(url)
        time.sleep(2)

        cards = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-col.justify-between.w-full")

        print(f"[LP] 🔗 Total kartu ditemukan: {len(cards)}")

        for card in cards:
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a.font-normal")
                tanggal_elem = card.find_element(By.CSS_SELECTOR, "p.text-xs.font-light.hidden.lg\\:block")
                
                link = link_elem.get_attribute("href")
                tanggal_str = tanggal_elem.text.strip()  # Contoh: 22-Jul-2025
                tanggal = datetime.strptime(tanggal_str, "%d-%b-%Y").date()

                if start_date and end_date and not (start_date <= tanggal <= end_date):
                    print(f"[LP] ⏩ Lewat (di luar rentang): {tanggal}")
                    continue

                driver.get(link)
                time.sleep(2)
                judul = driver.find_element(By.TAG_NAME, "h1").text.strip()
                paragraf = driver.find_elements(By.CSS_SELECTOR, "div.single-post-content p")
                isi = "\n".join([p.text.strip() for p in paragraf if p.text.strip()])

                results.append({
                    "judul": judul,
                    "link": link,
                    "tanggal": tanggal,
                    "isi": isi
                })
                print(f"[LP] ✅ {judul} | {tanggal}")

            except Exception as e:
                print(f"[LP] ❌ Gagal proses kartu ({e})")
                continue
    return results

def scrape_all_portals(start_date=None, end_date=None, max_articles=50):
    from selenium import webdriver
    driver = init_driver()

    viva = parse_viva(driver, start_date=start_date, end_date=end_date, max_articles=max_articles)
    antara = parse_antara(driver, start_date=start_date, end_date=end_date, max_pages=3)
    lampungpro = parse_lampungpro(driver, start_date=start_date, end_date=end_date, max_pages=3)

    driver.quit()
    return viva + antara + lampungpro
