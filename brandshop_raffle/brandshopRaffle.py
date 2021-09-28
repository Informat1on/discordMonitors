import requests
import time
import datetime
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

def monitor():
    source = requests.get('https://brandshop.ru/lottery',headers = headers).text
    soup = BeautifulSoup(source,'lxml')
    webhook = 'https://discordapp.com/api/webhooks/624896662380347392/pLeTBU6nggmZkRTYl3Nce_XOQWBV6DOe3cjoqrBgPOrZNp29IcwP7dGIRQubT6RL3QNn'
    webhookMaks = 'https://discordapp.com/api/webhooks/675761414299975689/xnd-dmRmtsZ9_D116-U2yGCIgW7kvd_9hinDVTv3ork4OtNILKjDd9x14e5mIdOQoB-F'
    currentItem = soup.find('h1').get_text()
    #достаю картинку
    if (currentItem != 'Air Jordan 1 High OG Defiant'):
        image = soup.find('div',attrs={'class':'yeezy'}).find('img').get('src')
        # print(image)
        filename = 'brandshopItems.txt'
        with open(filename, 'r') as rf:
            with open(filename, 'a') as af:
                read = rf.read()
                if currentItem not in read:
                    print(currentItem)
                    af.write(currentItem + '\n')
                    webHook(webhookMaks,'https://brandshop.ru/lottery',image)
                else:
                    print('Нет новых раффлов')
    else:
        print('Нету лоттереи')
    time.sleep(60)

def webHook(webhook,raffleLink,image):
    webhook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(title='Новый раффл БШ', url=raffleLink, color='14177041')

    now_date = datetime.datetime.now()

    embed.set_footer(icon_url='https://media.discordapp.net/attachments/671713320683962369/691618026252140574/unnamed_2.jpg?width=400&height=400',text='Exclusive for "BLESSED" \nGot at : {}'.format(now_date))  # картинка блессед маленькая внизу в кружке
    embed.set_thumbnail(url=image)

    webhook.add_embed(embed)

    webhook.execute()

while True:
    monitor()