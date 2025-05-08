import os
import datetime
import pandas as pd
import seaborn as sns
import urllib.request
import streamlit as st
import matplotlib.pyplot as plt

###########################
# Функції з лабораторної 2 #
###########################

def download_data(province_ID, start_year=1981, end_year=2024):
    # Створюю теку для зберігання, якщо її не існує
    if not os.path.exists("lab2_VHI"):
        os.makedirs("lab2_VHI")
    
    # Формую патерн для перевірки існуючих файлів
    filename_pattern = f"VHI-ID_{province_ID}_"
    existing_files = [file for file in os.listdir("lab2_VHI") if file.startswith(filename_pattern)]
    if existing_files:
        st.write(f"=] Файл для VHI-ID №{province_ID} вже існує: {existing_files[0]}")
        return
    
    url_download = (
        f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?"
        f"country=UKR&provinceID={province_ID}&year1={start_year}&year2={end_year}&type=Mean"
    )
    try:
        vhi_url_open = urllib.request.urlopen(url_download)
    except Exception as e:
        st.error(f"Помилка завантаження даних для province {province_ID}: {e}")
        return
    
    # формую назву файлу з поточною датою та часом
    year_month_now = datetime.datetime.now().strftime("%d-%m-%Y")
    h_m_s_time_now = datetime.datetime.now().strftime("%H-%M-%S")
    filename = f"VHI-ID_{province_ID}_{year_month_now}_{h_m_s_time_now}.csv"
    
    file_path = os.path.join("lab2_VHI", filename)
    with open(file_path, 'wb') as output:
        output.write(vhi_url_open.read())

    st.write(f"=] VHI-файл {filename} завантажений успішно!")
    return

def dataframer(folder_path):
    fr = []
    columns  = ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI", "empty"]
    
    csv_files = filter(lambda x: x.endswith('.csv'), os.listdir(folder_path))
    
    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)
        try:
            province_ID = int(file_name.split('_')[1])
        except Exception as e:
            st.warning(f"Не вдалося зчитати province_ID з файлу {file_name}: {e}")
            continue
        
        # зчитування CSV , задаю свої назви колонок
        try:
            df = pd.read_csv(file_path, header=1, names=columns)
        except Exception as e:
            st.warning(f"Помилка зчитування файлу {file_name}: {e}")
            continue
        
        df.at[0, "Year"] = df.at[0, "Year"][9:]
        
        # видаляю останній рядок та рядки з VHI = -1
        df = df.drop(df.index[-1])
        df = df.drop(df.loc[df["VHI"] == -1].index)
        # видаляю порожній стовпець
        df = df.drop("empty", axis=1)
        
        # додаю стовпець province_ID
        df.insert(0, "province_ID", province_ID, True)
        df['Year'] = df['Year'].astype(int)
        df["Week"] = df["Week"].astype(int)
        
        fr.append(df)
    
    if not fr:
        st.error("Не знайдено даних для обробки!")
        return pd.DataFrame()
    
    # об'єднуємо всі DataFrame, видаляю дублікати
    df_res = pd.concat(fr).drop_duplicates().reset_index(drop=True)
    df_res = df_res.loc[(df_res.province_ID != 12) & (df_res.province_ID != 20)]
    
    return df_res
def change_province_id(df):
    province_mapping = {
        1: 22,
        2: 24,
        3: 23,
        4: 25,
        5: 3,
        6: 4,
        7: 8,
        8: 19,
        9: 20,
        10: 21,
        11: 9,
        13: 10,
        14: 11,
        15: 12,
        16: 13,
        17: 14,
        18: 15,
        19: 16,
        21: 17,
        22: 18,
        23: 6,
        24: 1,
        25: 2,
        26: 7,
        27: 5,
    }
    df_copy = df.copy()
    df_copy['province_ID'] = df_copy['province_ID'].replace(province_mapping)
    return df_copy

###########################
# Основна логіка  Streamlit
###########################

st.set_page_config(page_title="LAB3", layout="wide")
st.title("LAB3")

# ініціалізація початкових значень, якщо їх немає
if "data_type" not in st.session_state:
    st.session_state["data_type"] = "VHI"
if "selected_province" not in st.session_state:
    st.session_state["selected_province"] = 1
if "week_range_str" not in st.session_state:
    st.session_state["week_range_str"] = "1-52"
if "year_range_str" not in st.session_state:
    st.session_state["year_range_str"] = "All"
if "color_map" not in st.session_state:
    st.session_state["color_map"] = "YlGnBu"
if "sort_asc" not in st.session_state:
    st.session_state["sort_asc"] = False
if "sort_desc" not in st.session_state:
    st.session_state["sort_desc"] = False

# словник 
ids_with_names = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 
    4: 'Донецька', 5: 'Житомирська', 6: 'Закарпатська', 
    7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 
    10: 'Кіровоградська', 11: 'Луганська', 12: 'Львівська', 
    13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 
    19: 'Харківська', 20: 'Херсонська', 21: 'Хмельницька',
    22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

# бічна панель
st.sidebar.header("Налаштування фільтрів")

# кнопка для завантаження даних
if st.sidebar.button("Завантажити дані (якщо потрібно)"):
    st.info("Запуск завантаження CSV-файлів")
    for idx in range(1, 28):
        st.write(f"!] Завантаження CSV-файлу за VHI-ID №{idx}...")
        download_data(idx, 1981, 2024)
    st.success("Завантаження завершено!")

# віджети фільтрів
data_type_local = st.sidebar.selectbox(
    "Оберіть часовий ряд",
    options=["VCI", "TCI", "VHI"],
    index=["VCI", "TCI", "VHI"].index(st.session_state["data_type"])  
)
st.session_state["data_type"] = data_type_local

province_options = [p for p in range(1, 26) if p not in [12, 20]]
if st.session_state["selected_province"] not in province_options:
    st.session_state["selected_province"] = province_options[0]

selected_province_local = st.sidebar.selectbox(
    "Оберіть область",
    options=province_options,
    format_func=lambda x: ids_with_names[x],
    index=province_options.index(st.session_state["selected_province"])
)
st.session_state["selected_province"] = selected_province_local

week_range_local = st.sidebar.text_input(
    "Інтервал тижнів (наприклад, 1-52)",
    value=st.session_state["week_range_str"]
)
st.session_state["week_range_str"] = week_range_local

year_range_local = st.sidebar.text_input(
    "Інтервал років (наприклад, 1981-2024 або All)",
    value=st.session_state["year_range_str"]
)
st.session_state["year_range_str"] = year_range_local

all_color_maps = ["YlGnBu", "RdBu", "GnBu", "viridis", "plasma", "inferno", 
                  "magma", "cividis", "coolwarm", "jet", "hot", "Spectral",
                  "spring", "summer", "autumn", "winter"]

color_map_local = st.sidebar.selectbox(
    "Оберіть колірну палітру для графіків",
    options=all_color_maps,
    index=all_color_maps.index(st.session_state["color_map"]) if st.session_state["color_map"] in all_color_maps else 0
)
st.session_state["color_map"] = color_map_local

sort_asc_local = st.sidebar.checkbox(
    "Сортувати за зростанням",
    value=st.session_state["sort_asc"]
)
st.session_state["sort_asc"] = sort_asc_local

sort_desc_local = st.sidebar.checkbox(
    "Сортувати за спаданням",
    value=st.session_state["sort_desc"]
)
st.session_state["sort_desc"] = sort_desc_local

if st.session_state["sort_asc"] and st.session_state["sort_desc"]:
    st.sidebar.warning("Обрано обидва варіанти сортування. Буде застосовано сортування за зростанням.")

#  кнопка скидання фільтрів 
if st.sidebar.button("Скинути фільтри"):
    st.session_state["data_type"] = "VHI"
    st.session_state["selected_province"] = 1
    st.session_state["week_range_str"] = "1-52"
    st.session_state["year_range_str"] = "All"
    st.session_state["color_map"] = "YlGnBu"
    st.session_state["sort_asc"] = False
    st.session_state["sort_desc"] = False
    st.rerun()

# завантаження та обробка даних
def load_and_process_data():
    folder_path = "lab2_VHI"
    if not os.path.exists(folder_path):
        return pd.DataFrame()
    df_old = dataframer(folder_path)
    df_new = change_province_id(df_old)
    return df_new

df_all = load_and_process_data()

if df_all.empty:
    st.error("Дані не завантажено. Спочатку натисніть кнопку 'Завантажити дані'.")
    st.stop()

# фільтрація даних
data_type = st.session_state["data_type"]
selected_province = st.session_state["selected_province"]
week_range_str = st.session_state["week_range_str"]
year_range_str = st.session_state["year_range_str"]
color_map = st.session_state["color_map"]
sort_asc = st.session_state["sort_asc"]
sort_desc = st.session_state["sort_desc"]

# фільтр за тижнями
try:
    week_parts = week_range_str.split('-')
    start_week = int(week_parts[0])
    end_week = int(week_parts[1])
except:
    st.error("Неправильний формат інтервалу тижнів. Введіть, наприклад, 1-52.")
    st.stop()

df_filtered = df_all[(df_all['Week'] >= start_week) & (df_all['Week'] <= end_week)]

# фільтр за роками, якщо не олл
if year_range_str.strip().lower() != 'all':
    try:
        year_parts = year_range_str.split('-')
        start_year = int(year_parts[0])
        end_year = int(year_parts[1])
        df_filtered = df_filtered[(df_filtered['Year'] >= start_year) & (df_filtered['Year'] <= end_year)]
        year_range_display = f"{start_year}-{end_year}"
    except:
        st.error("Неправильний формат інтервалу років. Введіть, наприклад, 1981-2024 або All.")
        st.stop()
else:
    year_range_display = "All years"

# фільтр за областю
df_filtered = df_filtered[df_filtered['province_ID'] == selected_province]

# сортування
if sort_asc and not sort_desc:
    df_filtered = df_filtered.sort_values(by=data_type, ascending=True)
elif sort_desc and not sort_asc:
    df_filtered = df_filtered.sort_values(by=data_type, ascending=False)

########################################
# результати
########################################
tabs = st.tabs(["Таблиця", "Графік часових рядів", "Порівняння областей"])

# 1 вкладка
with tabs[0]:
    st.header("Відфільтровані дані")
    st.dataframe(df_filtered[['province_ID', 'Year', 'Week', data_type]])

# 2 вкладка
with tabs[1]:
    st.header(f"Графік {data_type} для області [{ids_with_names[selected_province]}] ({year_range_display})")
    fig, ax = plt.subplots(figsize=(10, 6))
    years = sorted(df_filtered['Year'].unique())
    for yr in years:
        df_year = df_filtered[df_filtered['Year'] == yr]
        ax.plot(df_year['Week'], df_year[data_type], marker='.', linestyle='-', label=yr)
    ax.set_title(f"Часовий ряд {data_type}")
    ax.set_xlabel("Тиждень")
    ax.set_ylabel(data_type)
    ax.grid(True)
    ax.legend(title="Рік", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

# 3 вкладка
with tabs[2]:
    st.header(f"Порівняння {data_type} по областях ({year_range_display})")
    df_comp = df_all.copy()
    if year_range_str.strip().lower() != 'all':
        df_comp = df_comp[(df_comp['Year'] >= start_year) & (df_comp['Year'] <= end_year)]
    df_comp = df_comp[(df_comp['Week'] >= start_week) & (df_comp['Week'] <= end_week)]
    
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df_comp, x='province_ID', y=data_type, ax=ax2, palette=color_map)
    ax2.set_xlabel("Області")
    ax2.set_ylabel(data_type)
    ax2.set_title(f"Порівняльний аналіз {data_type} по областях")
    ax2.set_xticklabels(
        [ids_with_names.get(int(x.get_text()), x.get_text()) for x in ax2.get_xticklabels()],
        rotation=45
    )
    st.pyplot(fig2)
