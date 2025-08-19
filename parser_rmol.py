from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd

def convert_date(date_str):
    try:
        bulan_map = {
            "Januari": "January", "Februari": "February", "Maret": "March",
            "April": "April", "Mei": "May", "Juni": "June",
            "Juli": "July", "Agustus": "August", "September": "September",
            "Oktober": "October", "November": "November", "Desember": "December"
        }
        hari_map = {
            "Senin": "Monday", "Selasa": "Tuesday", "Rabu": "Wednesday",
            "Kamis": "Thursday", "Jumat": "Friday", "Sabtu": "Saturday", "Minggu": "Sunday"
        }

        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)
        for indo, eng in hari_map.items():
            date_str = date_str.replace(indo, eng)

        # Hapus jam jika ada
        if "|" in date_str:
            date_str = date_str.split("|")[0].strip()

        return datetime.strptime(date_str.strip(), "%A, %d %B %Y").date()
    except Exception as e:
        print(f"⚠️ Gagal parsing tanggal '{date_str}': {e}")
        return None

def parse_rmol_lampung(start_date=None, end_date=None, max_articles=10, max_pages=2, simpan=False, output_file="hasil_rmol_lampung.xlsx"):
    base_url = "https://www.rmollampung.id/category/daerah?page={}"
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    results = []
    seen_links = set()
    article_count = 0

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    for page in range(1, max_pages + 1):
        url = base_url.format(page)
        print(f"🔄 Memuat halaman {page} → {url}")
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.select("div.bussiness-post-item")  # ✅ fix selector

        if not articles:
            print("❌ Tidak ada artikel ditemukan.")
            continue

        for article in articles:
            if article_count >= max_articles:
                break
            try:
                link_tag = article.select_one("h3.title a")
                if not link_tag:
                    continue

                link = link_tag["href"]
                if not link.startswith("http"):
                    link = "https://www.rmollampung.id" + link
                title = link_tag.get_text(strip=True)

                if link in seen_links:
                    continue

                # Ambil isi dan tanggal dari halaman detail
                driver_detail = webdriver.Chrome(options=options)
                driver_detail.get(link)
                time.sleep(3)
                soup_detail = BeautifulSoup(driver_detail.page_source, "html.parser")

                # Ambil tanggal dari <ul><li>....</li></ul>
                                # Ambil semua <li> dan cari yang mengandung nama hari
                date_str = ""
                for li in soup_detail.select("ul li"):
                    teks = li.get_text(strip=True)
                    if any(hari in teks for hari in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]):
                        date_str = teks
                        break

                if not date_str:
                    print("⚠️ Tidak ada tanggal ditemukan di halaman detail.")
                    driver_detail.quit()
                    continue

                tanggal = convert_date(date_str)
                if not tanggal:
                    driver_detail.quit()
                    continue
                if start_date_obj and tanggal < start_date_obj:
                    driver_detail.quit()
                    continue
                if end_date_obj and tanggal > end_date_obj:
                    driver_detail.quit()
                    continue

                content_paragraphs = soup_detail.select("div.post-text.mt-30 p")
                content = "\n".join(p.get_text(strip=True) for p in content_paragraphs)
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

    driver.quit()
    df = pd.DataFrame(results)

    if simpan:
        if not df.empty:
            df.to_excel(output_file, index=False)
            print(f"✅ Selesai. Total artikel disimpan: {len(df)} → {output_file}")
        else:
            print("❌ Tidak ada data yang disimpan.")

    return df