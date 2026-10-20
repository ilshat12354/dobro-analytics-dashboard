"""
Модуль загрузки данных в SQLite.
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/analytics.db")

def load(detailed_df: pd.DataFrame, muni_df: pd.DataFrame, monthly_df: pd.DataFrame):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    detailed_df.to_sql("municipality_area_stats", conn, if_exists="replace", index=False)
    muni_df.to_sql("municipality_summary", conn, if_exists="replace", index=False)
    monthly_df.to_sql("monthly_dynamics", conn, if_exists="replace", index=False)

    conn.close()
    print(f"[load] Данные загружены в {DB_PATH}")