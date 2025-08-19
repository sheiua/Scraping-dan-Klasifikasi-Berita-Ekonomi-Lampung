from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd

def parse_lampost(start_date=None, end_date=None, max_articles=10, max_pages=2, simpan=False, output_file="hasil_lampost.xlsx"):
    base_url = "https://lampost.co/kategori/lampung/page/{}"
    results = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    # Konversi string ke tanggal
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    seen_links = set()
    article_count = 0
    page = 1

    while article_count < max_articles and page <= max_pages:
        url = base_url.format(page)
        print(f"🔄 Memuat halaman {page} → {url}")
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.select("h3.jeg_post_title a")

        if not articles:
            print("❌ Tidak ada artikel ditemukan.")
            break

        print(f"📄 Ditemukan {len(articles)} artikel.")

        for a in articles:
            if article_count >= max_articles:
                break

            link = a['href']
            title = a.get_text(strip=True)

            if link in seen_links:
                continue

            try:
                # Kunjungi halaman detail
                driver_detail = webdriver.Chrome(options=options)
                driver_detail.get(link)
                time.sleep(2)
                detail_soup = BeautifulSoup(driver_detail.page_source, "html.parser")

                # Ambil tanggal
                date_tag = detail_soup.select_one("div.jeg_meta_date a")
                date_str = date_tag.get_text(strip=True) if date_tag else ""
                tanggal = None

                try:
                    # Format tanggal di halaman: 24/07/25 - 19:09
                    tanggal = datetime.strptime(date_str.split(" -")[0], "%d/%m/%y").date()
                except Exception as e:
                    print(f"⚠️ Gagal parsing tanggal dari '{date_str}': {e}")
                    driver_detail.quit()
                    continue

                # Filter tanggal
                if start_date_obj and tanggal < start_date_obj:
                    print(f"🛑 Artikel terlalu lama ({tanggal}), berhenti.")
                    driver_detail.quit()
                    driver.quit()
                    df = pd.DataFrame(results)
                    if not df.empty:
                        df.to_excel(output_file, index=False)
                        print(f"✅ Disimpan ke {output_file}")
                    else:
                        print("❌ Tidak ada data untuk disimpan.")
                    return

                if end_date_obj and tanggal > end_date_obj:
                    driver_detail.quit()
                    continue

                # Ambil isi artikel
                content_div = detail_soup.find("div", class_="content-inner")
                content = content_div.get_text(separator="\n").strip() if content_div else ""

                results.append({
                    "judul": title,
                    "tanggal": tanggal.strftime("%Y-%m-%d"),
                    "link": link,
                    "isi": content
                })

                article_count += 1
                seen_links.add(link)
                driver_detail.quit()
                print(f"✅ Artikel ke-{article_count}: {title} ({tanggal})")

            except Exception as e:
                print(f"⚠️ Gagal memproses artikel: {e}")
                continue

        page += 1

    driver.quit()
    df = pd.DataFrame(results)
    if not df.empty:
        df.to_excel(output_file, index=False)
        print(f"✅ Selesai. Total artikel disimpan: {len(results)} → {output_file}")
    else:
        print("❌ Tidak ada data untuk disimpan.")

    if simpan:
        if not df.empty:
            df.to_excel(output_file, index=False)
            print(f"✅ Selesai. Total artikel disimpan: {len(df)} → {output_file}")
        else:
            print("❌ Tidak ada data yang disimpan.")

    return df

