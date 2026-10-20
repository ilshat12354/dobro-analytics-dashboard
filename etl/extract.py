"""
Модуль извлечения данных.
В прототипе генерируются синтетические данные по муниципалитетам Татарстана.
Для замены на реальный источник достаточно переписать функцию extract().
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path

MUNICIPALITIES = [
    "Казань", "Набережные Челны", "Нижнекамск", "Альметьевск",
    "Зеленодольск", "Бугульма", "Елабуга", "Лениногорск",
    "Чистополь", "Заинск", "Азнакаево", "Бавлы",
    "Буинск", "Кукмор", "Мамадыш", "Менделеевск",
    "Мензелинск", "Нурлат", "Тетюши", "Агрыз",
    "Азнакаевский район", "Аксубаевский район", "Актанышский район",
    "Алексеевский район", "Алькеевский район", "Альметьевский район",
    "Апастовский район", "Арский район", "Атнинский район",
    "Бавлинский район", "Балтасинский район", "Бугульминский район",
    "Буинский район", "Верхнеуслонский район", "Высокогорский район",
    "Дрожжановский район", "Елабужский район", "Заинский район",
    "Зеленодольский район", "Казань (город)", "Камско-Устьинский район",
    "Кукморский район", "Лаишевский район", "Лениногорский район",
    "Мамадышский район", "Менделеевский район", "Мензелинский район",
    "Муслюмовский район", "Нижнекамский район", "Новошешминский район",
    "Нурлатский район", "Пестречинский район", "Рыбно-Слободский район",
    "Сабинский район", "Сармановский район", "Спасский район",
    "Тетюшский район", "Тукаевский район", "Тюлячинский район",
    "Черемшанский район", "Чистопольский район", "Ютазинский район"
]

ACTIVITY_AREAS = [
    "Дети и молодёжь", "Образование", "Культура и искусство",
    "Экология", "Спорт и события", "Социальная помощь",
    "Здравоохранение", "Поисковая работа"
]

def extract() -> pd.DataFrame:
    """
    Имитация выгрузки открытой статистики Добро.Аналитика по Республике Татарстан.
    В реальном проекте здесь может быть:
      - requests.get(...) к внутреннему API представительства;
      - pd.read_html() для парсинга страницы dobro.ru/analytics;
      - pd.read_csv() для ручной выгрузки.
    """
    random.seed(42)
    np.random.seed(42)

    rows = []
    for muni in MUNICIPALITIES:
        base_volunteers = random.randint(500, 25000) if muni == "Казань" else random.randint(200, 8000)
        base_orgs = max(5, int(base_volunteers * random.uniform(0.01, 0.05)))
        base_events = random.randint(50, 1500) if muni == "Казань" else random.randint(10, 500)
        base_hours = base_volunteers * random.randint(2, 12)

        for area in ACTIVITY_AREAS:
            share = random.uniform(0.03, 0.25)
            rows.append({
                "municipality": muni,
                "area": area,
                "volunteers": int(base_volunteers * share),
                "organizations": max(1, int(base_orgs * share)),
                "events": max(1, int(base_events * share)),
                "hours": int(base_hours * share),
            })

    df = pd.DataFrame(rows)

    # Добавляем помесячную динамику за 12 месяцев
    months = pd.date_range("2025-01-01", periods=12, freq="MS").strftime("%Y-%m").tolist()
    monthly_rows = []
    for month in months:
        factor = random.uniform(0.7, 1.3)
        monthly_rows.append({
            "month": month,
            "volunteers": int(df["volunteers"].sum() * factor),
            "hours": int(df["hours"].sum() * factor),
            "events": int(df["events"].sum() * factor),
        })
    monthly_df = pd.DataFrame(monthly_rows)

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_dir / "raw_municipalities.csv", index=False, encoding="utf-8-sig")
    monthly_df.to_csv(raw_dir / "raw_monthly.csv", index=False, encoding="utf-8-sig")

    print(f"[extract] Сгенерировано {len(df)} строк по муниципалитетам и {len(monthly_df)} строк по месяцам.")
    return df, monthly_df