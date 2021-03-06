from bs4 import BeautifulSoup
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import time

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
    monitor(links,status,proxie_status)
    print(f'{time.asctime()} success! all sent to discord')
    time.sleep(refresh_time)


def monitor(links,status,proxie_status):
    for link in links:
        try:
            if proxie_status == 'No':
                source = requests.get(link,headers=headers).text
                proxie_status = 'Yes'
            else:
                source = requests.get(link, headers=headers,proxies=proxies).text
                proxie_status = 'No'

            source = requests.get(link, headers=headers).text
            soup = BeautifulSoup(source,'lxml')
            # print(soup)

            try:
                title = soup.find('h1',attrs={'id':'pdp_product_title'}).text
                price = soup.find('div',class_='product-price').text
                image = soup.find_all('picture')[1].find('source').get('srcset')
                print(image)
                # главное отличие от инсток - soon_butt
                # если есть - вещь еще оос
                # Уже скоро
                try:
                    soon_butt = soup.find('div',attrs={'data-test':'comingSoon'}).find('span',class_='headline-5').text
                except:
                    soon_butt = 'В наличии'
                print(soon_butt)

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
                        # либо она солд
                        else:
                            item_dict[link] = {'price': price, 'title': title, 'image': image, 'status': 'sold'}
                except:
                    pass




            except:
                pass


        except:
            pass



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