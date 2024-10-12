import pandas as pd
import glob
import json
import re

def run_code():  #триггер для запуска кода
    if keyword.__contains__():
     run_code()

def load_data(file_pattern):
    files = glob.glob(file_pattern)
    dataframes = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            df = pd.DataFrame(data)
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def determine_criteria(keyword, primary=True):
    primary_criteria = ["Description", "Developer", "Location", "Project"]
    secondary_criteria = ["Developer", "Project", "Area"]
    criteria = primary_criteria if primary else secondary_criteria
    for criterion in criteria:
        if re.search(re.escape(keyword), criterion, re.IGNORECASE):
            return criterion
    return None

def search_properties(file_path, search_criteria, primary=True):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        for key, value in search_criteria.items():
            if isinstance(value, dict):
                if 'min' in value and 'max' in value:
                    df = df[(df[key] >= value['min']) & (df[key] <= value['max'])]
            else:
                pattern = re.compile(re.escape(value), re.IGNORECASE)
                df = df[df[key].astype(str).str.contains(pattern)]
        return df

def find_similar_locations(data, keyword):
    keyword_pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    filtered_data = data[data.apply(lambda row: row.astype(str).str.contains(keyword_pattern).any(), axis=1)]
    similar_locations = filtered_data[[ "Developer", "Project", "City", "Area", "Floor", "Unit Type", "Unit Size (sqft)", "Unit Size (m2)", "Beds", "Sale or Rental", "Sale Value (AED)", "Sale Value (USD)", "Ownership", "Launch Date", "Broker", "Phone", "Email", "Media Link" ]].drop_duplicates()
    return similar_locations

def search_by_keyword(file_path, keyword, primary=True):
    criterion = determine_criteria(keyword, primary)
    if criterion:
        search_criteria = {criterion: keyword}
        results = search_properties(file_path, search_criteria, primary)
        return results
    else:
        return pd.DataFrame()  # Return empty DataFrame if no criterion is found

def search_secondary_market(df, keyword):
    # Поиск по полям Developer, Project и Area во вторичном рынке. Поиск всегда на английском
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    results = df[
        df['Developer'].str.contains(pattern) |
        df['Project'].str.contains(pattern) |
        df['Area'].str.contains(pattern)
    ]
    return results

def search_primary_market(df, keyword):
    # Поиск по полям Project и Developer в первичном рынке поиск всегда на английском
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    results = df[
        df['Project'].str.contains(pattern) |
        df['Developer'].str.contains(pattern)
    ]
    return results

# Функция для поиска вторичного рынка
def search_secondary(keyword, rental=False, sale=False):
    if rental:
        secondary_data_path = "file-KAyE5MSRGFroLOzPMkEhsx69"
    elif sale:
        secondary_data_path = " file-2gGaShQQT9filoVKUa3IGAoP"
    else:
        # Если клиент не обозначил, что предпочитает, выполняем поиск в обоих файлах
        rental_data_path = "file-KAyE5MSRGFroLOzPMkEhsx69"
        sale_data_path = " file-2gGaShQQT9filoVKUa3IGAoP"
        rental_df = load_data(rental_data_path)
        sale_df = load_data(sale_data_path)
        rental_results = search_secondary_market(rental_df, keyword)
        sale_results = search_secondary_market(sale_df, keyword)
        return rental_results, sale_results

    secondary_df = load_data(secondary_data_path)
    secondary_results = search_secondary_market(secondary_df, keyword)
    return secondary_results

# Загрузка данных для первичного рынка
primary_data_path = "/mnt/data/file-TpPCm43durn4M83GJAFGXEAU"
primary_df = load_data(primary_data_path)

# Выполнение поиска по ключевому слову который ввел пользователь на первичном рынке
keyword = [] 
primary_results = search_primary_market(primary_df, keyword)

# Отбор только нужных столбцов для первичного рынка
if not primary_results.empty:
    filtered_primary_results = primary_results[[ "Project", "Developer", "Sale Value (USD) from", "Installment_Plan", "Location", "Description" ]] #поиск по полю Location и Description всегда на русском языке
else:
    filtered_primary_results = pd.DataFrame()

# Выполнение поиска по ключевому слову который ввел пользователь на вторичном рынке (аренда и продажа)
rental_results, sale_results = search_secondary(keyword)

# Отбор только нужных столбцов для вторичного рынка (аренда)
if not rental_results.empty:
    filtered_rental_results = rental_results[[ "Developer", "Project", "Area", "Unit Size (sqft)", "Beds", "Sale Value (AED)", "Broker", "Phone" ]]
else:
    filtered_rental_results = pd.DataFrame()

# Отбор только нужных столбцов для вторичного рынка (продажа)
if not sale_results.empty:
    filtered_sale_results = sale_results[[ "Developer", "Project", "Area", "Unit Size (sqft)", "Beds", "Sale Value (AED)", "Broker", "Phone" ]]
else:
    filtered_sale_results = pd.DataFrame()

def display_results(results, result_type):
    if len(results) > 5:
        print(f"Found more than 5 results for {result_type}. Here are the first 5.")  # либо если пользователь ведет диалог на русском: Найдено более 5 результатов для {result_type}. Вот первые 5:
        print(results.head(5))
        more_results = input(f"Would you like to see the remaining results for {result_type}? (yes/no):")  # либо если пользователь ведет диалог на русском: Хотите увидеть остальные результаты для {result_type}? (да/нет):
        if more_results.lower() == 'да' or more_results.lower() == 'yes':
            remaining_results = results.iloc[5:]
            display_results(remaining_results, result_type)
        else:
            print(f"All results for {result_type} have been listed.")  # либо если пользователь ведет диалог на русском: Все результаты для {result_type} перечислены.
    else:
        print(f"Found {len(results)} results for {result_type}.")  # либо если пользователь ведет диалог на русском: Найдено {len(results)} результатов для {result_type}.
        print(results)
        print(f"All results for {result_type} have been listed.")  # либо если пользователь ведет диалог на русском: Все результаты для {result_type} перечислены.

# Функция для поиска по размеру для вторичного рынка с преобразованием значений в числовой формат
def search_by_size(file_path, size_criteria):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        
        # Преобразование значений в числовой формат
        df['Unit Size (sqft)'] = pd.to_numeric(df['Unit Size (sqft)'], errors='coerce')
        df['Unit Size (m2)'] = pd.to_numeric(df['Unit Size (m2)'], errors='coerce')
        
        # Поиск по размеру в квадратных футах
        if 'Unit Size (sqft)' in size_criteria:
            min_size_sqft = size_criteria['Unit Size (sqft)']['min']
            max_size_sqft = size_criteria['Unit Size (sqft)']['max']
            df = df[(df['Unit Size (sqft)'] >= min_size_sqft) & (df['Unit Size (sqft)'] <= max_size_sqft)]
        
        # Поиск по размеру в квадратных метрах
        if 'Unit Size (m2)' in size_criteria:
            min_size_m2 = size_criteria['Unit Size (m2)']['min']
            max_size_m2 = size_criteria['Unit Size (m2)']['max']
            df = df[(df['Unit Size (m2)'] >= min_size_m2) & (df['Unit Size (m2)'] <= max_size_m2)]
        
        return df

# Пример использования функции
size_criteria = {
    'Unit Size (sqft)': {'min': 500, 'max': 1500},
    'Unit Size (m2)': {'min': 46.45, 'max': 139.35}
}

# Выполнение поиска по вторичному рынку (аренда и продажа)
rental_data_path = "/mnt/data/file-KAyE5MSRGFroLOzPMkEhsx69"
sale_data_path = "/mnt/data/file-2gGaShQQT9filoVKUa3IGAoP"
rental_results = search_by_size(rental_data_path, size_criteria)
sale_results = search_by_size(sale_data_path, size_criteria)


# Отображение результатов
display_results(filtered_primary_results, "primary")
display_results(filtered_rental_results, "rental")
display_results(filtered_sale_results, "sale")