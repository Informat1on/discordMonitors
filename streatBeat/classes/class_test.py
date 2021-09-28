import time
from datetime import datetime
from threading import Thread
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
from selenium import webdriver


class StreatBeatMonitor():
    def __init__(self, webhooks, refresh_time):
        self.webhooks = webhooks
        self.refresh_time = refresh_time
        self.item = {}
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        }

        self.option = webdriver.ChromeOptions()
        self.chrome_prefs = {}
        self.option.experimental_options["prefs"] = self.chrome_prefs
        self.chrome_prefs["profile.default_content_settings"] = {"images": 2}
        self.chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        self.option.add_argument('--window-size=480,100')
        self.driver = webdriver.Chrome(options=self.option)

    # функция логирования
    def log(self, msg):
        print("[{}]: {}".format(datetime.now(), msg))

    # фунция запуска ядер
    def start(self):
        t = Thread(target=self.monitor_thread)
        t.start()

    def monitor_thread(self):
        while True:
            try:
                # перехожу по ссылке, с которой буду доставать вещи
                self.driver.get('https://street-beat.ru/cat/man/krossovki;kedy/nike;jordan/air-force;air-jordan-1/new/for_basketball;lifestyle/')

                # сканирую все ссылки на вещи
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                item_links = soup.find_all('a', attrs={'class': 'link catalog-item__img-wrapper ddl_product_link'})

                for href in item_links:
                    item_link = 'https://street-beat.ru' + href.get('href')

                    # если ссылки нет в черном листе
                    # делаем парсинг
                    if self.check_blacklist(item_link):
                        a = time.time()
                        self.monitor(item_link)
                        print(
                            time.time() - a
                        )
                    else:
                        pass
            except Exception as e:
                self.log("Error: " + str(e))
            time.sleep(self.refresh_time)

    def monitor(self, item_link):
        # открываю ссылку с айтемом
        self.driver.get(url=item_link)
        html = self.driver.page_source

        soup = BeautifulSoup(html, 'lxml')

        # получаю инсток размеры
        sizes = self.get_size(soup)

        # далее проверяю на новизну
        choice = self.check_notification(sizes, item_link)

        if choice:
            #     выполняю все операции ниже
            # получаю картинку
            img = self.get_image(soup)

            # получаю цену вещи
            price = self.get_item_price(soup)

            # получаю имя товара
            item_name = self.get_item_name(soup)
            # print(item_name)
            # отправляю в дискорд
            self.send_to_discord(item_name, item_link, img, sizes, price)

        else:
            pass

    def get_size(self, soup):
        spisok = []
        # тестовый парсинг размеров
        for i in soup.find('ul', attrs={'class': 'sizes__table hidden', 'data-size-type': 'tab_us'}):
            if str(i).find('<li class="missing">'):
                try:
                    spisok.append(i.text.replace('\n', ''))

                except:
                    pass
        return spisok

    def check_blacklist(self, item_link):
        filename = 'blacklist.txt'

        with open(filename, 'r') as rf:
            read = rf.read()
            # если ссылки на айтем нет в черном листе
            if item_link not in read:
                return True

            # если она есть
            else:
                return False

    def get_image(self, soup):
        img = str(soup.find('div', attrs={'data-slick-index': '1'}).find('img').get('src')).replace('100_100_1',
                                                                                                    '500_500_1')

        return img

    def get_item_name(self, soup):
        item_name = soup.find('h1', attrs={'class': 'product-heading'}).select('span')[0].text

        return item_name

    def get_item_price(self, soup):
        price = soup.find('div', attrs={'class': 'price--current'}).text

        return price

    def check_notification(self, actual_sizes, link):
        # берет текущие размеры и сверяет с последними размерами, которые выводились
        # далее по алгоритму и выводим решение

        try:
            # если есть запись о размере в словаре то проделываем алгоритм
            if self.item.get(link):
                # если размеры сохраненные и текущие идентичны, то ничего не выводим
                if self.item.get(link) == actual_sizes:
                    return False

                else:
                    print(f"sizes of {link} changed")
                    return True

            # иначе просто добавляем эти размеры в словарь
            else:
                print(f"sizes of {link} added")
                self.item[link] = actual_sizes

                return True

        except Exception as e:
            print(e)

    def send_to_discord(self, item_name, item_link, img, actual_sizes, price):
        webhook = 'https://discordapp.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
        webhook = DiscordWebhook(url=webhook)
        embed = DiscordEmbed(title=item_name, url=item_link, color='16711680')
        embed.set_thumbnail(url=img)

        embed.add_embed_field(name='Price', value=price, inline=False)
        # обработчик размеров
        i = 0
        string = ''
        while i != (len(actual_sizes)):

            # создание колонки
            if (i % 5 == 0 and i != 0) or (i == len(actual_sizes) - 1):
                string += actual_sizes[i]
                embed.add_embed_field(name='Sizes', value=string, inline=True)
                string = ''
            # иначе простое добавление текста
            else:
                string += actual_sizes[i] + '\n'

            i += 1

        webhook.add_embed(embed)
        webhook.execute()




