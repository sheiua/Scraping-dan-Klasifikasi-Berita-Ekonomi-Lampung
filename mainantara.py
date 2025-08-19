from datetime import date
from parsersAntara import parse_antara

if __name__ == "__main__":
    df = parse_antara(
        start_date="2025-07-25",
        end_date="2025-07-29",
        max_pages=2,
        max_articles=10,
        simpan=True,
        output_file="hasil_antara_fix.xlsx"
    )
    print(df.head())

