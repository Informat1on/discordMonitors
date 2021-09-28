from bs4 import BeautifulSoup
import time
from selenium import webdriver
from multiprocessing import Process


# настройки браузера Хром, через который будет производиться парсинг
option = webdriver.ChromeOptions()
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
# отключаю загрузки изображений для ускорения закгрузки страницы
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
# запускаю хром в фоне (невидимка)
option.add_argument('--headless')


# функция парсинга сайта Мелбет
def parse_melbet():
    # Мелбет
    koef_name_list_melbet = []
    main_dict_melbet = {}

    # начинаю работу
    driver = webdriver.Chrome(options=option)
    # выбираю ссылку для парсинга
    parse_link = 'https://melbet.ru/line/football/'
    # перехожу по ней в браузере
    driver.get(url=parse_link)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    #     получаю таблицу где названия лиг и сами матчи
    table = soup.find('div', attrs={'class': 'kofsTableBody'})

    # делаю перебор каждого элемента в таблице, тк там и названия лиг и матчи
    for element in table:
        koef_melbet = {}

        # пытаюсь найти названия коэффициентов
        try:
            # если уже есть - пропускаем
            if koef_name_list_melbet:
                pass
            else:
                # нахожу названия коэффициентов
                koeffs_head = element.find_all('div', attrs={'class': 'fl'})

                # добавляю каждое название в список
                for i in koeffs_head:
                    koef_name_list_melbet.append(i.text)

        except:
            pass

        # буду находить теперь матчи
        # нахожу названия команд
        try:
            # получаю ссылку на событие
            link = 'https://melbet.ru/' + element.find('a', attrs={'class': 'nameLink fl clear'})['href']

            # нахожу названия команад
            find_teams = element.find_all('span', attrs={'class': 'team'})
            teams = find_teams[0].text + '- ' + find_teams[1].text

            # нахожу коэффициенты
            find_koeffs = element.find_all('span', attrs={'class': 'kof'})

            for i in range(len(find_koeffs)):
                koef_melbet[koef_name_list_melbet[i]] = find_koeffs[i].text

            # нахожу время события
            date_time = element.find('span', attrs={'class': 'time'}).text + ' ' + element.find('span', attrs={
                'class': 'date'}).text


            # далее нужно записать все в словарь
            add_to_dict_melbet(main_dict_melbet, date_time, teams, link, koef_melbet)

        # ловлю исключения
        except:
            pass

    return main_dict_melbet

# функция  добавления в словарь Мелбет
def add_to_dict_melbet(main_dict_melbet, date_time, teams, link, koef_melbet):
        main_dict_melbet[link] = {'date': date_time, 'teams': teams, 'koeffs': koef_melbet, 'link': link}


# функция парсинга сайта Париматч
def parse_parimatch():
    # Париматч
    koef_name_list_parimatch = ['ФОРА', 'КФ', 'Т', 'Б', 'М', 'П1', 'Х', ' П2']
    main_dict_parimatch = {}

    # начинаю работу
    driver = webdriver.Chrome(options=option)
    # выбираю ссылку для парсинга
    parse_link = 'https://www.parimatch.ru/prematch/all/1%7CF'
    # перехожу по ней в браузере
    driver.get(url=parse_link)
    time.sleep(6)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    events = soup.find_all('prematch-block',attrs={'class':'prematch-block'})

    for match in events:
        koef_parimatch = {}
        try:

            # нахожу команды
            find_teams = match.find_all('span',attrs={'class':'competitor-name'})
            # соединяю их для красивого вывода
            teams = find_teams[0].text + "-" + find_teams[1].text
            # нахожу дату и время игры
            date = match.find('div',attrs={'class':'live-block-time'}).text
            # нахожу ссылку на матч
            link = "https://www.parimatch.ru" + match.find('a',attrs={'class':'live-block-competitors'})['href']

            # выбираю блок, в котором коэффициенты
            blocks = match.find('div',attrs={'class':'main-markets'})
            # тк все коэффы с тегом спан, то сразу выбираю их всех
            blocks = blocks.find_all('span')

            # запускаю перебор по коэффициентам
            for i in range(len(blocks)):
                if i == 0:
                    # тк фора - 2 коэфф-та, кладу каждый в список
                    fora = [blocks[i].text, blocks[i+2].text]
                    # тк кф - 2 коэфф-та, кладу каждый в список
                    kf = [blocks[i+1].text, blocks[i+3].text]
                    # добавляю в словарб коэффов
                    koef_parimatch[koef_name_list_parimatch[i]] = fora
                    koef_parimatch[koef_name_list_parimatch[i+1]] = kf

                elif i > 3:
                    koef_parimatch[koef_name_list_parimatch[i-2]] = blocks[i].text
                else:
                    pass

                # добавляю в словарь
                add_to_dict_parimatch(main_dict_parimatch, koef_parimatch,teams,date,link)

        except:
            pass

    return main_dict_parimatch

# функция  добавления в словарь Париматч
def add_to_dict_parimatch(main_dict_parimatch, koef_parimatch, teams, date, link):
    main_dict_parimatch[link] = {'date': date, 'teams': teams, 'koeffs': koef_parimatch, 'link':link}


# функция парсинга сайта Фонбет
def parse_fonbet():
    # Фонбет
    koef_name_list_fonbet_new = ['1', 'X', '2', '1X', '12', 'X2', 'Фора', 'Коэфф', 'Тотал', 'Б', 'М']
    main_dict_fonbet = {}

    # начинаю работу
    driver = webdriver.Chrome(options=option)
    parse_link = 'https://www.fonbet.ru/bets/football/'
    # перехожу по ней в браузере
    driver.get(url=parse_link)

    # жду прогрузки матчей
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    events = soup.find_all('tr',attrs={'class':'table__row'})

    for match in events:
        koef_fonbet = {}
        try:

            # нахожу названия команд
            teams = match.find('div', attrs={'class':'table__match-title-text'}).text
            # нахожу дату
            date = match.find('div',attrs={'class':'table__time'}).text
            # нахожу ссылку на матч
            link = match.find('a',attrs={'class':'table__match-title-text'})['href']
            # нахожу список с коэфф которые прожимаются мышкой
            find_koeffs = match.find_all('td',attrs={'class':'table__col _type_btn _type_normal'})
            # нахожу форы и тотал
            find_other_koeffs = match.find_all('td',attrs={'class':'table__col _type_fora'})

            for i in range(11):

                if i < 6:
                    koef_fonbet[koef_name_list_fonbet_new[i]] = find_koeffs[i].text

                elif i == 6:
                    koef_fonbet[koef_name_list_fonbet_new[i]] = [find_other_koeffs[0].text, find_other_koeffs[1].text]
                elif i == 7:
                    koef_fonbet[koef_name_list_fonbet_new[i]] = [find_koeffs[i-1].text, find_koeffs[i].text]

                elif i == 8:
                    koef_fonbet[koef_name_list_fonbet_new[i]] = find_other_koeffs[2].text

                else:
                    koef_fonbet[koef_name_list_fonbet_new[i]] = find_koeffs[i-1].text

            add_to_dict_fonbet(main_dict_fonbet, koef_fonbet, teams, date, link)


        except:
            pass

    return main_dict_fonbet

# функция  добавления в словарь Фонбет
def add_to_dict_fonbet(main_dict_fonbet, koef_fonbet, teams, date, link):
    main_dict_fonbet[link] = {'date': date, 'teams': teams, 'koeffs': koef_fonbet, 'link':link}

# запускаю бесконечный цикл (мониторинг) с задержкой time.sleep 15 секунд
while True:
    # создаю процессы для параллельного выполнения
    melbet = Process(target=print(parse_melbet()))
    parimatch = Process(target=print(parse_parimatch()))
    fonbet = Process(target=print(parse_fonbet()))

    # запускаю процессы
    melbet.start()
    parimatch.start()
    fonbet.start()

    # присоединяю процессы
    melbet.join()
    parimatch.join()
    fonbet.join()

    # спим
    time.sleep(15)
