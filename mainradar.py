from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from parser_radarlampung import parse_radar_lampung
import pandas as pd
from datetime import date

def get_headless_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--use-gl=swiftshader')
    options.add_argument('--enable-webgl')
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

if __name__ == "__main__":
    print("🚀 Memulai scraping Radar Lampung...")
    driver = get_headless_driver()

    try:
        results = parse_radar_lampung(
            driver=driver,
            start_date=None,
            end_date=None,
            max_articles=30,
            max_pages=2
        )

        df = pd.DataFrame(results)
        df.to_excel("hasil_radarlampung.xlsx", index=False)
        print("📁 Data berhasil disimpan ke 'hasil_radarlampung.xlsx'")
    finally:
        driver.quit()
