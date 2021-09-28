from bs4 import BeautifulSoup
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import time

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

item_dict = {}

proxies = {
    'http': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
    'https': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
}

def main():
    config = json.load(open('mir_config.json'))
    links = config['links']
    refresh_time = config['refresh_time']

    print(f'{time.asctime()} started checking items..')
    monitor(links)
    print(f'{time.asctime()} success! all sent to discord')
    time.sleep(refresh_time)

def monitor(links):
    for link in links:
        try:
            source = requests.get(link,headers = headers, proxies=proxies).text
        except:
            time.sleep(180)
            continue

        soup = BeautifulSoup(source,'lxml')

        try:
            title = soup.find('div',class_='first_l').text
        except:
            title = 'No title'
        try:
            price = soup.find('div',class_='price').text
        except:
            price = 'Error getting price'

        try:
            image = soup.find('div',class_='Imgblock').find('img').get('src')
        except:
            image = 'Error getting image'

        try:
            button = soup.find('div',class_='pselect').find('form').text.split('\n')[1]
        except Exception as e:
            print(e)

        # если появилась в наличии
        # два статуса - ресток и солд
        try:
            # если есть запись - значит выводили
            # нужно проверить еще раз
            if item_dict.get(link):
                # значит она еще инсток
                if button != 'Нет в наличии':
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
                if button != 'Нет в наличии':
                    item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'new-item'}
                    # отправляем в дискорд
                    send_to_discord(link, title, image, price)
                # либо она солд
                else:
                    item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}


        except Exception as e:
            print(e)

def send_to_discord(link, titile, image, price):
    webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title=titile, url=link, color='16711680')
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name='Price', value=price, inline=True)
    webhook.add_embed(embed)
    webhook.execute()


while True:
    main()