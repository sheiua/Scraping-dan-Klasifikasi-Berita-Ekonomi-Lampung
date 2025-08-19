from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date
import time
from dateutil import parser as dateparser

def parse_antara(start_date=None, end_date=None, max_pages=2, max_articles=50, simpan=False, output_file='antara_lampung.xlsx'):
    # 1) Pastikan start_date/end_date jadi date objects
    if isinstance(start_date, str):
        start_date = dateparser.parse(start_date).date()
    if isinstance(end_date, str):
        end_date = dateparser.parse(end_date).date()

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    base_url = "https://lampung.antaranews.com/lampung-update?page="
    results = []
    artikel_count = 0

    try:
        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            print(f"🔄 Memproses halaman {page} → {url}")
            driver.get(url)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            headers = soup.find_all('h3')
            links = []
            for h3 in headers:
                a = h3.find('a', href=True)
                if a and 'berita' in a['href']:
                    link = a['href']
                    if not link.startswith("http"):
                        link = "https://lampung.antaranews.com" + link
                    links.append(link)

            print(f"   🔗 Ditemukan {len(links)} link")
            for link in links:
                if artikel_count >= max_articles:
                    raise StopIteration

                # init tanggal sebagai None setiap loop
                tanggal = None

                try:
                    # buka tab baru
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(link)
                    time.sleep(1)

                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # 2) Parsing tanggal lewat dateparser, selalu menghasilkan date atau None
                    time_tag = detail_soup.find("time", itemprop="datePublished")
                    if time_tag and time_tag.has_attr("datetime"):
                        raw = time_tag["datetime"].strip()
                        try:
                            tanggal = dateparser.parse(raw).date()
                        except Exception as e:
                            print(f"     ⚠️ Gagal parsing tanggal: {e}")
                            tanggal = None

                    # 3) Filter tanggal hanya jika start_date & end_date ada
                    if start_date and end_date:
                        if not tanggal or not (start_date <= tanggal <= end_date):
                            print(f"     ⏩ Lewat (tanggal tidak sesuai): {tanggal}")
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            continue

                    # Judul
                    h1 = detail_soup.find("h1")
                    judul = h1.get_text(strip=True) if h1 else "Tanpa Judul"

                    # Konten
                    konten = detail_soup.find("article") or detail_soup.find("div", class_="content-detail")
                    paras = konten.find_all('p') if konten else []
                    isi = " ".join(p.get_text(strip=True) for p in paras if not p.get("class"))
                    isi = isi.split("Baca juga:")[0]

                    print(f"     📅 {tanggal} | 📛 {judul[:60]}...")
                    results.append({
                        "judul": judul,
                        "link": link,
                        "tanggal": tanggal,
                        "isi": isi
                    })
                    artikel_count += 1

                    # tutup tab detail
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"     ⚠️ Gagal parsing artikel: {e}")
                    # pastikan kembali ke tab utama
                    try:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except:
                        pass
                    continue

    except StopIteration:
        print("🚫 Batas maksimum artikel tercapai.")
    finally:
        driver.quit()

    # hasil
    df = pd.DataFrame(results)
    if simpan:
        if not df.empty:
            df.to_excel(output_file, index=False)
            print(f"📁 Disimpan ke {output_file} ({len(df)} artikel)")
        else:
            print("❌ Tidak ada artikel yang disimpan.")
    return df
