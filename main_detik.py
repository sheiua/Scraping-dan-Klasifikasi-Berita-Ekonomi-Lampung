from parser_detik import parse_detik_lampung

parse_detik_lampung(
    start_date="2025-07-01",
    end_date="2025-07-25",
    max_articles=10,
    max_pages=2,
    output_file="detik_lampung_test.xlsx"
)

