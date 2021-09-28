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
a = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
b = 'https://discord.com/api/webhooks/807887671329685534/zMdV4CqOxzqpMphItQie7lgtthz40bZDJtf3ny2W97fd4MsBdg_4gf19BPymKvwthiYy'
status = a

proxies = {
    'http': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
    'https': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
}

proxie_status = 'No'

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
def main():
    config = json.load(open('config.json'))
    links = config['links']
    refresh_time = config['refresh_time']

    print(f'{time.asctime()} started checking items..')
    monitor(links[0],status,proxie_status)
    print(f'{time.asctime()} success! all sent to discord')
    time.sleep(refresh_time)


def monitor(url,status,proxie_status):
        try:
            driver.get(url)
            time.sleep(1)
            source = driver.page_source
            # source = requests.get(url, headers=headers).text
            soup = BeautifulSoup(source,'lxml')

            products = soup.find_all('tr',class_='cart_item')


            for item in products:

                try:
                    link = item.find('a',class_='product_link__js').get('href')
                    try:
                        title = item.find('a',class_='product_link__js').find('img').get('alt')
                        image = item.find('a', class_='product_link__js').find('img').get('src')
                    except:
                        title = item.find('a',class_='product_link__js').text.replace('\n','').replace('  ','')
                        image = 'https://www.eduprizeschools.net/wp-content/uploads/2016/06/No_Image_Available.jpg'
                    # нет в наличии или цена будет
                    price = item.find('span',class_='price').text.replace('\n','').replace('  ','')




                    # если появилась в наличии
                    # два статуса - ресток и солд
                    try:
                        # если есть запись - значит выводили
                        # нужно проверить еще раз
                        if item_dict.get(link):
                            # значит она еще инсток
                            if price != 'Нет в наличии':
                                # если она рестокнулась
                                if item_dict[link]['status'] == 'sold':
                                    item_dict[link] = {'price': price, 'title': title, 'image': image,
                                                       'status': 'restock'}
                                    # отправляем в дискорд
                                    send_to_discord(link, title, image, price)
                                    print(f'sending {title}')
                                # если просто висит
                                else:
                                    pass
                            else:
                                # значит она продана
                                item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}

                        # если не было записи - новый предмет либо солд
                        else:
                            # если инсток
                            if price != 'Нет в наличии':
                                item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'new-item'}
                                # отправляем в дискорд
                                send_to_discord(link, title, image, price)
                                print(f'sending {title}')
                            # либо она солд
                            else:
                                item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}


                    except Exception as e:
                        print(e)
                        continue

                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            print(e)
            time.sleep(30)



def send_to_discord(link,title,image,price):
    webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title=title, url=link, color='16711680')
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name='Price', value=price, inline=True)
    webhook.add_embed(embed)
    webhook.execute()

while True:
    main()