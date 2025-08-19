from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import dateparser
import time

def parse_radar_lampung(driver, start_date=None, end_date=None, max_articles=30, max_pages=2):
    results = []
    collected = 0

    for page in range(max_pages):
        offset = page * 30
        url = f"https://radarlampung.disway.id/kategori/458/lampung-raya/{offset}"
        print(f"🌐 Memuat halaman: {url}")
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ✅ Ambil semua link dari elemen <p><a href=...>
        article_links = []
        for p in soup.find_all('p'):
            a_tag = p.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if href.startswith("https://radarlampung.disway.id/") and href not in article_links:
                    article_links.append(href)

        if not article_links:
            print("⚠️ Tidak ada artikel ditemukan di halaman ini.")
            break

        for link in article_links:
            if collected >= max_articles:
                break
            try:
                print(f"🔗 Memproses: {link}")
                driver.get(link)
                time.sleep(2)

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "date"))
                    )
                except TimeoutException:
                    print("❌ Gagal menemukan elemen tanggal dengan WebDriverWait")
                    continue

                detail_soup = BeautifulSoup(driver.page_source, "html.parser")

                # ✅ Ambil tanggal
                tanggal_elem = detail_soup.find("span", class_="date")
                tanggal_obj = None
                if tanggal_elem:
                    tanggal_str = tanggal_elem.get_text(strip=True)
                    tanggal_obj = dateparser.parse(tanggal_str, fuzzy=True, dayfirst=True)
                    print(f"📆 Tanggal: {tanggal_obj}")
                else:
                    print("⚠️ Elemen <span class='date'> tidak ditemukan")

                # ✅ Filter tanggal
                if tanggal_obj:
                    if start_date and tanggal_obj.date() < start_date:
                        continue
                    if end_date and tanggal_obj.date() > end_date:
                        continue
                elif start_date or end_date:
                    continue

                # ✅ Ambil judul & isi artikel
                judul_elem = detail_soup.find("h1")
                konten_elem = detail_soup.find("div", class_="article-content")
                judul = judul_elem.get_text(strip=True) if judul_elem else ""
                konten = konten_elem.get_text(strip=True) if konten_elem else ""

                results.append({
                    "judul": judul,
                    "tanggal": tanggal_obj.strftime("%Y-%m-%d") if tanggal_obj else None,
                    "link": link,
                    "isi": konten
                })
                collected += 1
                print(f"✅ Artikel ke-{collected} ditambahkan")

            except Exception as e:
                print(f"❌ Error parsing artikel: {e}")
                continue

        if collected >= max_articles:
            break

    return results
