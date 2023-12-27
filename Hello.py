# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import seaborn as sns

LOGGER = get_logger(__name__)


# Загрузка данных из CSV___
@st.cache
def load_data():
    data = pd.read_csv('flats_with_predict.csv')  # Замените 'your_data.csv' на имя вашего файла CSV
    return data

data = load_data()
print(data.columns)

# Заголовок приложения
st.title('Анализ флиппинг проекта')

# Сайдбар для выбора города
selected_city = st.sidebar.selectbox('Выберите город', data['city'].unique())

# Фильтрация данных по выбранному городу
filtered_data = data[data['city'] == selected_city]

# Сайдбар для выбора квартиры из отфильтрованных данных
selected_flat_id = st.sidebar.selectbox('Выберите квартиру', filtered_data['id'])

# Отображение характеристик выбранной квартиры
selected_flat = data[data['id'] == selected_flat_id].squeeze()
st.subheader(f'Характеристики квартиры {selected_flat_id}')
st.write(selected_flat)

st.subheader('Анализ стоимости квартиры')
# График цен за квадратный метр
chart, ax = plt.subplots(figsize=(8, 6))

# Фоновый график для всех квартир
sns.stripplot(
    data=data,
    y='price_sq',
    color='white',
    jitter=0.3,
    size=8,
    linewidth=1,
    edgecolor='gainsboro',
    alpha=0.7
)

# Выделение выбранной квартиры
sns.stripplot(
    data=data[data['id'] == selected_flat_id],
    y='price_sq',
    color='red',
    size=12,
    linewidth=1,
    edgecolor='black',
    label=f'Selected Flat {selected_flat_id}'
)

# Отображение графика
ax.set_ylabel('Price per Square Meter (R$)')
ax.set_title('Prices per Square Meter for Different Flats')
ax.legend()
st.pyplot(chart)

# Карта конкурентов в радиусе 1500 метров
st.subheader('Карта конкурентов в радиусе 1500 метров')
m = folium.Map(location=[selected_flat['lat'], selected_flat['lon']], zoom_start=14, tooltip=True)

# Перебор всех квартир и добавление маркеров в радиусе 1500 метров
for index, flat in filtered_data.iterrows():
    flat_location = (flat['lat'], flat['lon'])
    selected_location = (selected_flat['lat'], selected_flat['lon'])
    
    # Вычисление расстояния между квартирами в метрах
    distance = geodesic(flat_location, selected_location).meters
    
    if distance <= 1500:
        # Определение цвета маркера для выбранной квартиры
        marker_color = 'red' if flat['id'] == selected_flat_id else 'blue'
        
        folium.Marker([flat['lat'], flat['lon']],
                      popup=f"{flat['city']}, {flat['price_sq']} руб/м²",
                      tooltip=f"{flat['city']}, {flat['price_sq']} руб/м²",
                      icon=folium.Icon(color=marker_color),
                      auto_open=True).add_to(m)

# Отображение карты
folium_static(m)
