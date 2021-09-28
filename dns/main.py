from bs4 import BeautifulSoup
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import time
from selenium import webdriver

option = webdriver.ChromeOptions()
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
option.add_argument('--window-size=480,100')
# option.add_argument('--headless')
# option.add_argument('--window-size=1000,1000')
driver = webdriver.Chrome(options=option)

item_dict = {}

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
def main():
    # перехожу на главный сайт для установки города
    # driver.get('https://www.dns-shop.ru/')
    # time.sleep(2)
    # driver.find_element_by_xpath('/html/body/header/div[3]/div/ul[1]/li[1]/div/div[1]').click()
    # field = driver.find_element_by_xpath('//*[@id="select-city"]/div[1]/div[2]/div/input')
    # field.send_keys('Краснодар')
    # driver.find_element_by_xpath('//*[@id="select-city"]/div[4]/ul[5]/li[1]').click()
    # ссылки по которым мониторить
    config = json.load(open('config.json'))
    links = config['links']
    refresh_time = config['refresh_time']

    print(f'{time.asctime()} started checking items..')
    monitor(links)
    # print('sending to discord..')
    # prepare()
    print(f'{time.asctime()} success! all sent to discord')
    time.sleep(refresh_time)
    # print(f'{time.asctime()} closing driver')
    # driver.close()

def monitor(links):
    # перебор по ссылкам
    for link in links:
        # мониторим каждую
        # перехожу по ссылке, с которой будем доставать вещи
        driver.get(url=link)
        time.sleep(1)
        # сканирую все ссылки на вещи
        html = driver.page_source
        # source = requests.get(link,headers=headers).text
        soup = BeautifulSoup(html,'lxml')

        try:
            # нахожу все товары на сайте
            items = soup.find_all("div",class_="catalog-item")

            # запускаю цикл перебора каждой вещи
            for item in items:
                # достаю ссылку на вещь
                try:
                    item_link = "https://www.dns-shop.ru" + item.find("a",class_="ui-link")['href']
                except:
                    item_link = None

                # достаю название вещи
                try:
                    item_name = item.find("a",class_="ui-link").text
                except:
                    item_name = None

                # # достаю цену
                try:
                    # item_price = get_price(item_link)
                    # time.sleep(0.5)
                    item_price = item.find('div',class_='product-min-price__current').text

                except:
                    item_price = None
                # достаю картинку
                try:
                    item_image = item.find("picture").find("source")['data-srcset']
                except:
                    item_image = None

                # добавляю в словарь
                try:
                    # если уже есть, то проверяю на наличие колокольчика

                    if item_dict.get(item_link):
                        button = item.find('button',attrs={'data-commerce-tartget':'PRODUCT_NOTIFY'})
                        print('here is notif button')
                    else:
                        item_dict[item_link] = {"name":item_name,"image":item_image,"price":item_price,"status":"new"}
                        print(f'{time.asctime()} sending to discord!')
                        send_to_discord(item_dict[item_link]['name'], item_link, item_dict[item_link]['image'], item_dict[item_link]['price'])
                        # print(item_dict)


                except Exception as e:
                    item_dict[item_link] = "Error"
                    print(f"{time.asctime()} {e}")
                # print(item_link)
                # print(item_name)
                # print(item_price)
                # print(item_image)
                # print("\n")
                # time.sleep(0.5)

            # print(items)
        except:
            print(f"{time.asctime()} can't get items on the site")

        # time.sleep(5)

def send_to_discord(name,link,image,price):
    webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title=name, url=link, color='16711680')
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name='Price', value=price, inline=True)
    webhook.add_embed(embed)
    webhook.execute()

def prepare():
    for i in item_dict:
        send_to_discord(item_dict[i]['name'], i, item_dict[i]['image'],item_dict[i]['price'])


def test():
    source = requests.get('https://www.dns-shop.ru/product/ca20104b76872eb0/videokarta-palit-geforce-rtx-2060-super-dual-ne6206s018p2-1160a-1/', headers=headers).text
    soup = BeautifulSoup(source, 'lxml')
    price = soup.find('span', class_='product-card-price__current')


    print(
        price, soup
    )


def get_price(link):
    source = requests.get(link,headers=headers).text
    soup = BeautifulSoup(source,'lxml')
    price = soup.find('span',class_='product-card-price__current').text

    # print(price)

    return price

while True:
    main()