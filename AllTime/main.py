import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
from time import gmtime, strftime

status = ['oos']
def main(status):
    inStock = 'https://www.alltime.ru/watch/casio/GA-2000WM-1AER/516738/'
    try:
        outStock = 'https://www.alltime.ru/watch/casio/GA-2100SKE-7AER/525952/'
        source = requests.get(outStock).text
        soup = BeautifulSoup(source, 'lxml')

        try:
            title = soup.find('div', class_='product-empty-title').text
            status[0] = 'oos'
        except:
            title = soup.find('h1', attrs={'itemprop': 'name'}).text
            if (status[0] == 'oos'):
                timing = strftime("%d %b %Y %H:%M:%S", gmtime())
                print(f'[{timing}] : Found watch. Trying to send to Discord.')

                webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
                webhook = DiscordWebhook(url=webhook,content=f'IN stock {outStock}')

                webhook.execute()
                status[0] = 'inStock'

        time.sleep(15)

    except:
        timing = strftime("%d %b %Y %H:%M:%S", gmtime())
        print(f'[{timing}] : Found Exception.')

        webhook = 'https://discord.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
        webhook = DiscordWebhook(url=webhook, content=f'Exception')

        webhook.execute()

        time.sleep(60)


while True:
    main(status)
