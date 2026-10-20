"""
Интерактивный дашборд аналитики волонтёрской активности Республики Татарстан.
Запуск: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path
import subprocess
import sys


DB_PATH = Path("data/analytics.db")

DB_PATH = Path("data/analytics.db")

# --- Проверка и автоматическое создание БД при первом запуске ---
if not DB_PATH.exists():
    st.info("База данных не найдена. Выполняется первичная генерация данных...")
    try:
        # Запускаем ETL-конвейер из корня проекта
        subprocess.run([sys.executable, "-m", "etl.pipeline"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Ошибка при создании базы данных: {e}")
        st.stop()


st.set_page_config(
    page_title="Добро.Аналитика · Татарстан",
    page_icon="🤝",
    layout="wide",
)

@st.cache_data(ttl=600)
def load_data():
    if not DB_PATH.exists():
        st.error("База данных не найдена. Сначала запустите ETL: `python -m etl.pipeline`")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    muni = pd.read_sql("SELECT * FROM municipality_summary", conn)
    monthly = pd.read_sql("SELECT * FROM monthly_dynamics ORDER BY month", conn)
    detail = pd.read_sql("SELECT * FROM municipality_area_stats", conn)
    conn.close()
    return muni, monthly, detail

muni_df, monthly_df, detail_df = load_data()

# ---------- Боковая панель: фильтры ----------
st.sidebar.header("Фильтры")

selected_munis = st.sidebar.multiselect(
    "Муниципалитеты",
    options=sorted(muni_df["municipality"].unique()),
    default=None,
    placeholder="Все муниципалитеты",
)

if selected_munis:
    filtered_muni = muni_df[muni_df["municipality"].isin(selected_munis)]
    filtered_detail = detail_df[detail_df["municipality"].isin(selected_munis)]
else:
    filtered_muni = muni_df
    filtered_detail = detail_df

# ---------- Заголовок ----------
st.title("🤝 Аналитика волонтёрской активности")
st.caption("Республика Татарстан · данные платформы «Добро.рф» (демонстрационный прототип)")

# ---------- KPI-карточки ----------
total_volunteers = int(filtered_muni["volunteers"].sum())
total_orgs = int(filtered_muni["organizations"].sum())
total_events = int(filtered_muni["events"].sum())
total_hours = int(filtered_muni["hours"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Волонтёры", f"{total_volunteers:,}".replace(",", " "))
col2.metric("Организации", f"{total_orgs:,}".replace(",", " "))
col3.metric("Мероприятия", f"{total_events:,}".replace(",", " "))
col4.metric("Волонтёрские часы", f"{total_hours:,}".replace(",", " "))

st.divider()

# ---------- Вкладки ----------
tab1, tab2, tab3 = st.tabs(["📊 Муниципалитеты", "📈 Динамика", "🎯 Направления"])

with tab1:
    st.subheader("Показатели по муниципалитетам")
    muni_sorted = filtered_muni.sort_values("volunteers", ascending=False)

    fig_bar = px.bar(
        muni_sorted.head(20),
        x="municipality",
        y="volunteers",
        color="volunteers",
        color_continuous_scale="Blues",
        labels={"municipality": "Муниципалитет", "volunteers": "Волонтёры"},
        title="Топ-20 муниципалитетов по числу волонтёров",
    )
    fig_bar.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.dataframe(
        muni_sorted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "municipality": "Муниципалитет",
            "volunteers": "Волонтёры",
            "organizations": "Организации",
            "events": "Мероприятия",
            "hours": "Часы",
            "hours_per_volunteer": "Часов на волонтёра",
        },
    )

with tab2:
    st.subheader("Динамика по месяцам")
    fig_line = px.line(
        monthly_df,
        x="month",
        y=["volunteers", "hours"],
        markers=True,
        labels={"value": "Значение", "month": "Месяц", "variable": "Показатель"},
        title="Динамика волонтёров и отработанных часов",
    )
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("Распределение по направлениям деятельности")
    area_agg = (
        filtered_detail.groupby("area", as_index=False)["volunteers"]
        .sum()
        .sort_values("volunteers", ascending=False)
    )
    fig_pie = px.pie(
        area_agg,
        names="area",
        values="volunteers",
        title="Доли направлений по числу волонтёров",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)