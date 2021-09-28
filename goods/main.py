from bs4 import BeautifulSoup
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import time
from selenium import webdriver
proxies = {
    'http': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
    'https': 'http://MYMpC4:2Hvu2A@194.67.214.169:9780',
}

proxie_status = 'No'

item_dict = {}

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
def main():
    config = json.load(open('config.json'))
    links = config['links']
    refresh_time = config['refresh_time']

    print(f'{time.asctime()} started checking items..')
    monitor(links,proxie_status)
    print(f'{time.asctime()} success! all sent to discord')
    time.sleep(refresh_time)

def monitor(links,proxie_status):
    # перебор по ссылкам
    for link in links:
        try:
            if proxie_status == 'No':
                source = requests.get(link, headers=headers).text
                proxie_status = 'Yes'
            else:
                source = requests.get(link, headers=headers, proxies=proxies).text
                proxie_status = 'No'

            soup = BeautifulSoup(source,'lxml')
            title = soup.find('header',class_='title-page').text.replace('\n','')
            image = soup.find('div',class_='image-zoom-wrapper').find('img').get('src')

            # если находит кнопку - инсток
            try:
                button = soup.find('div',class_='c-web-buyProduct').text.replace('\n','')
            except:
                button = 'None'

            try:
                price = soup.find('div',class_='price__final').text.replace(' ','')[:-1]

            except:
                price = 'None'

            # если появилась в наличии
            # два статуса - ресток и солд
            try:
                # если есть запись - значит выводили
                # нужно проверить еще раз
                if item_dict.get(link):
                    # значит она еще инсток
                    if button != 'None':
                        # если она рестокнулась
                        if item_dict[link]['status'] == 'sold':
                            item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'restock'}
                            # отправляем в дискорд
                            print(f'Sending to discord {title}')
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
                    if button != 'None':
                        item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'new-item'}
                        # отправляем в дискорд
                        print(f'Sending to discord {title}')
                        send_to_discord(link, title, image, price)
                    # либо она солд
                    else:
                        item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}
            except Exception as e:
                print(e)

        except Exception as e:
            print(e)
            time.sleep(180)
            continue


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