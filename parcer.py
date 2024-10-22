import numpy as np
from bs4 import BeautifulSoup 
import requests
import matplotlib.pyplot as plt

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0',
}

# Параметры запроса на hhru для парсинга вакансий Data Analyst, Data Science и Data Engineer соответственно: 
data_analyst_params = {
    'text': '"data analyst"',   # Названия подходящих вакансий
    'salary': '',                                   # Зарплата не важна
    'items_on_page': '20',                         # Количество вакансий на странице
    'search_field': 'name',                         # Поиск по названию вакансии
    'area': '1',                                    # Регион 1 (Москва)
    'page': '0'                                     # Номер страницы
}

data_science_params = {
    'text': '"data scientist" OR "data science"',   
    'salary': '',                                   
    'items_on_page': '20',                         
    'search_field': 'name',                         
    'area': '1',                                    
    'page': '0'                                     
}

data_engineer_params = {
    'text': '"data engineer"',   
    'salary': '',                                   
    'items_on_page': '20',                         
    'search_field': 'name',                         
    'area': '1',                                    
    'page': '0'                                     
}

#Массив со всеми параметрами
all_params = [data_analyst_params, data_science_params, data_engineer_params] 

# Массив с количеством вакансий по направлениям
# data_analyst[0][], data_scientist[1][], data_engineers[2][]
# в разрезах junior[][0], middle[][1], senior[][2] 
vacancies_table = np.zeros((3, 3))

# Массивы с ключевыми словами, на случай если в вакансии не указан опыт работы, но указана должность
junior_keywords = ["младший", "junior", "стажер", "стажёр"]      
middle_seywords = ["middle"]                                        
senior_keywords = ["senior", "team lead", "tech lead", "ведущий"]   

for i in range(3):   
    hh_web = requests.get('https://hh.ru/search/vacancy', params=all_params[i], headers=headers)   
    hh_web_converted = BeautifulSoup(hh_web.text, "lxml")

    search_result = hh_web_converted.find("h1").text.split()    # Поиск строки с количеством вакансий
    amount_of_all_vacancies = int(search_result[0])             # Извлечение числа вакансий
    
    if amount_of_all_vacancies % 20 == 0:
        number_of_pages = amount_of_all_vacancies // 20
    else:
        number_of_pages = amount_of_all_vacancies // 20 + 1

    for j in range(number_of_pages):
        if j != 0:
            all_params[i]['page'] = str(i)    # Передаем в параметры следущую страницу поиска
            hh_web = requests.get('https://hh.ru/search/vacancy', params=all_params[i], headers=headers)
            hh_web_converted = BeautifulSoup(hh_web.text, "lxml")

        vacancies = hh_web_converted.find_all("h2", attrs = {'data-qa' : 'bloko-header-2'})     # Ищем блоки с названиями вакансии

        for p in vacancies:
            name = p.find("span", attrs = {'class' : 'magritte-text___tkzIl_4-3-2'}).text.lower()               # Ищем название вакансии
            experience = p.parent.find("div", attrs = {'class' : 'magritte-tag__label___YHV-o_3-0-13'}).text    # Ищем требуемый опыт

            # Поскольку в вакансии могут быть указаны ключевые слова для разных уровней
            # Необходимо пройти по каждому из массивов ключевых слов
            # Например, "Middle / Senior"
            keyword_is_found = 0
            for word in junior_keywords:
                if name.find(word) != -1:
                    keyword_is_found = 1
                    vacancies_table[i][0] += 1
                    break
            for word in middle_seywords:
                if name.find(word) != -1:
                    keyword_is_found = 1
                    vacancies_table[i][1] += 1
                    break
            for word in senior_keywords:
                if name.find(word) != -1:
                    keyword_is_found = 1
                    vacancies_table[i][2] += 1
                    break

            # Если в вакансии не указано ключевое слово,
            # Уровень определяется по требуемому опыту работы
            if not keyword_is_found:
                if experience == "Без опыта":
                    vacancies_table[i][0] += 1
                elif experience == "Опыт 1-3 года":
                    vacancies_table[i][0] += 1
                    vacancies_table[i][1] += 1
                elif experience == "Опыт 3-6 лет":
                    vacancies_table[i][1] += 1
                    vacancies_table[i][2] += 1
                elif experience == "Опыт более 6 лет":
                    vacancies_table[i][2] += 1


labels = ["Junior", "Middle", "Senior"]
titles = ["Data Analyst", "Data Scientist", "Data Engineer"]

x = np.arange(3)
width = 0.25  
multiplier = 0

fig, ax = plt.subplots(layout='constrained')
transposed_table = np.transpose(vacancies_table)

for w in range(3):
        offset = width * multiplier
        rects = ax.bar(x + offset, transposed_table[w], width, label=labels[w])
        ax.bar_label(rects, padding=3)
        multiplier += 1

ax.set_ylabel('Количество')
ax.set_title('Вакансии в сфере Data Science на HH.ru в Москве')
ax.set_xticks(x + width, titles)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 300)

plt.show()