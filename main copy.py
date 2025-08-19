from parser_rmol import parse_rmol_lampung
from parser_detik import parse_detik_lampung
from parsersAntara import parse_antara
from lampost_parser import parse_lampost
import pandas as pd

def main():
    # Masukkan tanggal dari user
    start_date = input("🗓️ Masukkan tanggal mulai (YYYY-MM-DD): ")
    end_date = input("🗓️ Masukkan tanggal akhir (YYYY-MM-DD): ")

    max_articles = 10
    max_pages = 2

    print("\n🚀 Mulai proses scraping...\n")

    # Scrape dari masing-masing portal (tidak simpan Excel per portal)
    df_rmol = parse_rmol_lampung(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)
    df_detik = parse_detik_lampung(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)
    df_antara = parse_antara(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)
    df_lampost = parse_lampost(start_date, end_date, max_articles=max_articles, max_pages=max_pages, simpan=False)

    # Gabungkan semua DataFrame
    df_all = pd.concat([df_rmol, df_detik, df_antara, df_lampost], ignore_index=True)

    # Simpan hasil akhir
    if not df_all.empty:
        output_file = "hasil_semua_portal.xlsx"
        df_all.to_excel(output_file, index=False)
        print(f"\n✅ Selesai. Total artikel dari semua portal: {len(df_all)} → {output_file}")
    else:
        print("\n❌ Tidak ada artikel yang ditemukan dari semua portal.")

if __name__ == "__main__":
    main()
