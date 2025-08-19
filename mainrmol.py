import pandas as pd
from parser_rmol import parse_rmol_lampung

if __name__ == "__main__":
    # Ubah sesuai kebutuhan
    hasil = parse_rmol_lampung(
        start_date="2025-07-01",
        end_date="2025-07-25",
        max_articles=10,
        max_pages=2
    )

