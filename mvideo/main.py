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
    time.sleep(refresh_time + random.randint(0,15))

def monitor(links):
    # region = ''
    # name = ''
    # price = 0
    # availability = ''
    # image = ''
    for link in links:
        time.sleep(random.randint(1,10))
        source = requests.get(link,headers=headers).text
        soup = BeautifulSoup(source,'lxml')

        info = soup.find('body',class_='facelift faceliftPDP').find('script').text.split(',')

        keywords = ("cityName",'productName','productPriceLocal','productAvailability','productId')
        try:
            for i in info:
                if (keywords[0] in i):
                    region = i.replace('\n','').replace('\t','').split(':')[1].replace(' ','').replace('\'','')
                elif (keywords[1] in i):
                    name = i.replace('\n','').replace('\t','').split(':')[1].replace('\'','')
                elif (keywords[2] in i):
                    price = i.replace('\n', '').replace('\t', '').split(':')[1].replace(' ', '').replace('\'', '')
                elif (keywords[3] in i):
                    availability = i.replace('\n', '').replace('\t', '').split(':')[1].replace(' ', '').replace('\'', '')
                elif (keywords[4] in i):
                    productId = i.replace('\n', '').replace('\t', '').split(':')[1].replace(' ', '').replace('\'', '')
                    image = f'https://img.mvideo.ru/Pdb/{productId}.jpg'
        except:
            pass

        # если появилась в наличии
        # два статуса - ресток и солд
        try:
            # если есть запись - значит выводили
            # нужно проверить еще раз
            if item_dict.get(link):
                # значит она еще инсток
                if availability != 'unavailable':
                    # если она рестокнулась
                    if item_dict[link]['status'] == 'sold':
                        item_dict[link] = {'price': price, 'name': name, 'image': image, 'status': 'restock', 'region':region}
                        # отправляем в дискорд
                        send_to_discord(link, name, image, price, region)
                    # если просто висит
                    else:
                        pass
                else:
                    # значит она продана
                    item_dict[link] = {'price': price, 'name': name, 'image': image, 'status': 'sold', 'region':region}

            # если не было записи - новый предмет либо солд
            else:
                # если инсток
                if availability != 'unavailable':
                    item_dict[link] = {'price': price, 'name': name, 'image': image, 'status': 'new-item', 'region':region}
                    # отправляем в дискорд
                    send_to_discord(link, name, image, price,region)
                # либо она солд
                else:
                    item_dict[link] = {'price': price, 'name': name, 'image': image, 'status': 'sold', 'region':region}


        except Exception as e:
            print(e)

def send_to_discord(link, name, image, price, region):
    webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title=name, url=link, color='16711680')
    embed.set_thumbnail(url=image)
    embed.add_embed_field(name='Price', value=price, inline=True)
    embed.add_embed_field(name='Region', value=region, inline=True)
    webhook.add_embed(embed)
    webhook.execute()

while True:
    main()