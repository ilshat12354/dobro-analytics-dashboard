"""
Оркестратор ETL-конвейера.
Запуск: python -m etl.pipeline
"""

from etl.extract import extract
from etl.transform import transform
from etl.load import load

def run_pipeline():
    print("=== Старт ETL ===")
    extract()
    detailed_df, muni_df, monthly_df = transform()
    load(detailed_df, muni_df, monthly_df)
    print("=== ETL завершён ===")

if __name__ == "__main__":
    run_pipeline()