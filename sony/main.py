from bs4 import BeautifulSoup
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import time
import random

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
proxies = {
    'http': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
    'https': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
}

item_dict = {}
def main():
    config = json.load(open('config.json'))
    links = config['links']
    refresh_time = config['refresh_time']

    print(f'{time.asctime()} started checking items..')
    monitor(links)
    print(f'{time.asctime()} success! all sent to discord')
    # рандомное время мониторинга
    time.sleep(refresh_time + random.randint(0,5))

def monitor(links):
    for link in links:

        source = requests.get(link,headers=headers, proxies=proxies).text
        soup = BeautifulSoup(source,'lxml')

        try:
            title = soup.find('div',class_='visible-dv h1-bottom').text.replace('\n','')
            price = soup.find('div',class_='price font-bold').get('content')
            image = 'https://store.sony.ru' + soup.find('img',class_='img-responsive').get('src')
            button = soup.find('div',class_='item-button').find('span').get('href')
            delete_index = button.rfind('/')
            button = button[delete_index+1:]

        except Exception as e:
            print(e)
            time.sleep(150)
            continue

        # если появилась в наличии
        # два статуса - ресток и солд
        try:
            # если есть запись - значит выводили
            # нужно проверить еще раз
            if item_dict.get(link):
                # значит она еще инсток
                if button != 'OutOfStock':
                    # если она рестокнулась
                    if item_dict[link]['status'] == 'sold':
                        item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'restock'}
                        # отправляем в дискорд
                        send_to_discord(link, title, image, price)
                    # если просто висит
                    else:
                        pass
                else:
                    # значит она продана
                    item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}

            # если не было записи - новый предмет либо солд
            else:
                # если инсток
                if button != 'OutOfStock':
                    item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'new-item'}
                    # отправляем в дискорд
                    send_to_discord(link, title, image, price)
                # либо она солд
                else:
                    item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}


        except Exception as e:
            print(e)

def send_to_discord(link, title, image, price):
    webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title=title, url=link, color='16711680')
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name='Price', value=price, inline=True)
    webhook.add_embed(embed)
    webhook.execute()

while True:
    main()