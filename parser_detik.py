from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import time
import pandas as pd

def parse_detik_lampung(start_date=None, end_date=None, max_articles=10, max_pages=2, simpan=False, output_file="hasil_detik_lampung.xlsx"):
    base_url = "https://www.detik.com/tag/lampung/?sortby=time&page={}"
    results = []

    # Setup headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    # Konversi tanggal parameter
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    def parse_date(tanggal_str):
        try:
            # Ganti nama bulan
            bulan_map = {
                "Jan": "Jan", "Feb": "Feb", "Mar": "Mar", "Apr": "Apr",
                "Mei": "May", "Jun": "Jun", "Jul": "Jul", "Agu": "Aug",
                "Sep": "Sep", "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
            }
            for indo, eng in bulan_map.items():
                if indo in tanggal_str:
                    tanggal_str = tanggal_str.replace(indo, eng)
                    break

            # Ganti nama hari
            hari_map = {
                "Senin": "Monday", "Selasa": "Tuesday", "Rabu": "Wednesday",
                "Kamis": "Thursday", "Jumat": "Friday", "Sabtu": "Saturday", "Minggu": "Sunday"
            }
            for indo, eng in hari_map.items():
                if indo in tanggal_str:
                    tanggal_str = tanggal_str.replace(indo, eng)
                    break

            # Hapus WIB
            cleaned = tanggal_str.replace(" WIB", "").strip()

            # Parsing
            return datetime.strptime(cleaned, "%A, %d %b %Y %H:%M").date()

        except Exception as e:
            print(f"⚠️ Parsing gagal untuk '{tanggal_str}': {e}")
            return None

    seen_links = set()
    article_count = 0
    page = 1

    while article_count < max_articles and page <= max_pages:
        url = base_url.format(page)
        print(f"🔄 Memuat halaman {page} → {url}")
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.select("div.list.media_rows.list-berita article")

        if not articles:
            print("❌ Tidak ada artikel ditemukan di halaman ini, berhenti.")
            break

        print(f"📄 Ditemukan {len(articles)} artikel.")

        for art in articles:
            if article_count >= max_articles:
                break

            try:
                a_tag = art.find("a")
                if not a_tag:
                    continue

                link = a_tag["href"]
                title_tag = a_tag.find("h2", class_="title")
                title = title_tag.text.strip() if title_tag else "-"

                # Ambil tanggal dari <span class="date">, skip <span class="category">
                date_container = art.select_one("span.date")
                date_str = ""
                if date_container:
                    for item in date_container.contents:
                        if isinstance(item, NavigableString):
                            date_str = item.strip()
                            break

                tanggal = parse_date(date_str)
                if not tanggal:
                    print(f"⚠️ Gagal parsing tanggal: '{date_str}', dilewati.")
                    continue

                # Filter tanggal
                if start_date_obj and tanggal < start_date_obj:
                    print(f"🛑 Artikel terlalu lama ({tanggal}), berhenti.")
                    driver.quit()
                    df = pd.DataFrame(results)
                    if not df.empty:
                        df.to_excel(output_file, index=False)
                        print(f"✅ Disimpan ke {output_file}")
                    else:
                        print("❌ Tidak ada data untuk disimpan.")
                    return

                if end_date_obj and tanggal > end_date_obj:
                    continue

                if link in seen_links:
                    continue

                # Ambil isi artikel detail
                driver_detail = webdriver.Chrome(options=options)
                driver_detail.get(link)
                time.sleep(3)
                soup_detail = BeautifulSoup(driver_detail.page_source, "html.parser")
                body = soup_detail.find("div", class_="detail__body-text")
                content = body.get_text(separator="\n").strip() if body else ""
                driver_detail.quit()

                results.append({
                    "judul": title,
                    "tanggal": tanggal.strftime("%Y-%m-%d"),
                    "link": link,
                    "isi": content
                })

                article_count += 1
                seen_links.add(link)
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
