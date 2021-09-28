import requests
import datetime
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import time

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

last_price = 0

def monitor():
    global last_price
    link = 'https://www.farfetch.com/ru/shopping/women/adidas-yeezy-yeezy-500-item-13140651.aspx'
    source = requests.get(link,headers=headers).text
    soup = BeautifulSoup(source, 'lxml')

    current_price = soup.find('span',attrs={'data-tstid':'priceInfo-original'}).text
    int_string = ''
    for i in current_price:
        if (i >='0' and i<='9'):
            int_string+=i
    current_price=int(int_string)

    print(last_price)
    if (last_price == 0):
        last_price = current_price
        print(last_price)
        send_webhook(last_price, soup, link)


    elif (current_price != last_price):
        print(f'Price has changed to {current_price}')
        last_price = current_price
        send_webhook(last_price, soup, link)

    else:
        pass



def send_webhook(last_price,soup,link):

    img = soup.find_all('img')[4].get('src')
    title = soup.find('span', attrs={'data-tstid': 'cardInfo-description'}).text

    sizes = ''
    size_field = soup.find('div', attrs={'class': '_fe40d4'})
    for i in size_field:
        for j in i:
            try:
                if ('UK' in j.text):
                    sizes += j.text + '\n'
            except:
                pass
    webhook = 'https://discordapp.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
    webhook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(title=title, url=link, color='16711680')
    now_date = datetime.datetime.now()
    embed.set_footer(
        icon_url='https://media.discordapp.net/attachments/672887506328617011/705884836807573564/BLESSED_LOGO_HAND_final.png?width=523&height=523',
        text='Exclusive for "BLESSED" \nGot at : {}'.format(now_date))
    embed.set_thumbnail(url=img)
    embed.add_embed_field(name='Price', value=f'{last_price}₽', inline=True)
    embed.add_embed_field(name='Sizes', value=sizes, inline=True)
    webhook.add_embed(embed)
    webhook.execute()


while True:
    monitor()
    time.sleep(60)