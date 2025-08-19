from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time

# Fungsi untuk membuat driver headless
def get_headless_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

# ----------------------------
# PARSER ANTARA NEWS LAMPUNG
# ----------------------------
def parse_antara(driver, start_date=None, end_date=None, max_articles=50):
    results = []
    visited = set()
    base_url = "https://lampung.antaranews.com"

    for page in range(1, 20):  # Ubah sesuai kebutuhan
        if len(results) >= max_articles:
            break
        url = f"{base_url}/indeks-news/lampung/{page}"
        driver.get(url)
        time.sleep(1.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div.article__list a")

        for item in items:
            link = item.get("href")
            if not link or link in visited or not link.startswith("/berita/"):
                continue

            full_link = urljoin(base_url, link)
            visited.add(link)
            driver.get(full_link)
            time.sleep(1)
            detail = BeautifulSoup(driver.page_source, "html.parser")

            # Judul
            title_tag = detail.find("h1")
            title = title_tag.text.strip() if title_tag else ""

            # Konten
            content_tag = detail.find("div", class_="article__content")
            content = content_tag.get_text(separator=" ", strip=True) if content_tag else ""

            # Tanggal
            date_tag = detail.find("div", class_="article__date")
            tanggal = None
            if date_tag:
                try:
                    raw = date_tag.text.strip()  # misal: "Kamis, 11 Juli 2024 16:22 WIB"
                    tanggal_str = raw.split(", ")[-1].split(" WIB")[0]  # "11 Juli 2024 16:22"
                    tanggal = datetime.strptime(tanggal_str, "%d %B %Y %H:%M")
                except:
                    pass

            if tanggal:
                tanggal_only = tanggal.date()
                if start_date and tanggal_only < start_date:
                    continue
                if end_date and tanggal_only > end_date:
                    continue

            results.append({
                "portal": "Antara News",
                "judul": title,
                "tanggal": tanggal.date() if tanggal else None,
                "konten": content,
                "link": full_link
            })

    return results

# ----------------------------
# PARSER RADAR LAMPUNG
# ----------------------------
def parse_radarlampung(driver, start_date=None, end_date=None, max_articles=50, max_pages=10):
    base_url = "https://radarlampung.disway.id/kategori/458/lampung-raya"
    results = []
    visited_links = set()

    for page in range(1, max_pages + 1):
        if len(results) >= max_articles:
            break

        offset = page * 30
        url = f"{base_url}/{offset}"
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.select("a.post-title")

        if not articles:
            continue

        for a in articles:
            if len(results) >= max_articles:
                break

            try:
                link = urljoin(base_url, a['href'])
                if link in visited_links:
                    continue
                visited_links.add(link)

                driver.get(link)
                time.sleep(1.5)
                detail = BeautifulSoup(driver.page_source, "html.parser")

                judul_tag = detail.find("h1", class_="post-title")
                judul = judul_tag.text.strip() if judul_tag else ""

                konten_tag = detail.find("div", class_="post-content")
                konten = konten_tag.get_text(separator=" ", strip=True) if konten_tag else ""

                tanggal_tag = detail.find("div", class_="post-date")
                tanggal = None
                if tanggal_tag:
                    try:
                        raw = tanggal_tag.text.strip()  # e.g., "Rabu, 10 Juli 2024 - 18:42 WIB"
                        tanggal_str = raw.split(" - ")[0].split(", ")[-1]
                        tanggal = datetime.strptime(tanggal_str, "%d %B %Y")
                    except:
                        pass

                if tanggal:
                    tanggal_only = tanggal.date()
                    if start_date and tanggal_only < start_date:
                        continue
                    if end_date and tanggal_only > end_date:
                        continue

                results.append({
                    "portal": "Radar Lampung",
                    "judul": judul,
                    "tanggal": tanggal.date() if tanggal else None,
                    "konten": konten,
                    "link": link
                })

            except:
                continue

    return results
