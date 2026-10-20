"""
Модуль трансформации данных: приведение типов, обработка пропусков,
расчёт производных показателей.
"""

import pandas as pd
from pathlib import Path

def transform() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_dir = Path("data/raw")

    df = pd.read_csv(raw_dir / "raw_municipalities.csv", encoding="utf-8-sig")
    monthly_df = pd.read_csv(raw_dir / "raw_monthly.csv", encoding="utf-8-sig")

    # Приводим типы
    numeric_cols = ["volunteers", "organizations", "events", "hours"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Убираем дубликаты
    df = df.drop_duplicates(subset=["municipality", "area"])

    # Производный показатель: среднее число часов на волонтёра
    df["hours_per_volunteer"] = (df["hours"] / df["volunteers"].replace(0, 1)).round(2)

    # Агрегация по муниципалитетам
    muni_agg = (
        df.groupby("municipality", as_index=False)
        .agg(
            volunteers=("volunteers", "sum"),
            organizations=("organizations", "sum"),
            events=("events", "sum"),
            hours=("hours", "sum"),
        )
    )
    muni_agg["hours_per_volunteer"] = (muni_agg["hours"] / muni_agg["volunteers"].replace(0, 1)).round(2)

    # Нормализация месяцев
    monthly_df["month"] = monthly_df["month"].astype(str)
    for col in ["volunteers", "hours", "events"]:
        monthly_df[col] = pd.to_numeric(monthly_df[col], errors="coerce").fillna(0).astype(int)

    print(f"[transform] Очищено {len(df)} строк, агрегировано {len(muni_agg)} муниципалитетов.")
    return df, muni_agg, monthly_df