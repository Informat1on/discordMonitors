import requests
import time
import datetime
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed


headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

def monitor():

    source = requests.get('https://www.nike.com/ru/launch/',headers = headers).text
    soup = BeautifulSoup(source,'lxml')
    webhook = 'https://discordapp.com/api/webhooks/624896662380347392/pLeTBU6nggmZkRTYl3Nce_XOQWBV6DOe3cjoqrBgPOrZNp29IcwP7dGIRQubT6RL3QNn'
    webhookMaks = 'https://discordapp.com/api/webhooks/672798340571988028/m3ThbiGpv1xGNEw8GN2An-UvkI4RDy2Ua-JBe-zdo2ADjxg82ngK1IV1k-wkrNPQ6lkF'
    webhookMaks2 = 'https://discordapp.com/api/webhooks/681889403664203776/XtIqmuxjEsw1iSwfPcozbqZXxYhOprH8eAKTAsj5QOyWUdPenj5A0KEJatpxiqmlcpRh'
    for hrefs in soup.find_all('a',attrs= {'class':'card-link d-sm-b'}):

        hrefs = hrefs.get('href')
        links = 'https://www.nike.com/ru/' + hrefs
        filename = 'nikelinks.txt'
        with open(filename,'r') as rf:
            with open(filename,'a') as af:
                read = rf.read()
                if links not in read:
                    print(links)
                    af.write(links + '\n')
                    itemDate(links)
                    webHook(webhook,links)

                else:
                    print('no new links found')
    time.sleep(60)


def webHook(webhook,links):
    webhook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(title=itemName(links), url=links, color='14177041')

    now_date = datetime.datetime.now()
    embed.set_footer(icon_url='https://media.discordapp.net/attachments/555461264248143878/691928242352947230/outOffon.jpg?width=1366&height=1366',text='Exclusive for "BLESSED" \nGot at : {}'.format(now_date))  # картинка блессед маленькая внизу в кружке
    embed.set_thumbnail(url=itemPic(links))
    embed.add_embed_field(name='Цена', value=itemPrice(links))  # поле с ценой
    webhook.add_embed(embed)

    webhook.execute()

def itemPrice(links): #цена
    source = requests.get(links, headers=headers).text
    soup = BeautifulSoup(source, 'lxml')
    if (soup.find_all('div',attrs={'class':'ncss-brand pb6-sm fs14-sm fs16-md'})):
        price = soup.find('div',attrs={'class':'ncss-brand pb6-sm fs14-sm fs16-md'}).get_text()
    else:
        price = 'Не удалось получить цену'
    return(price)

def itemPic(links): #картинка
    source = requests.get(links, headers=headers).text
    soup = BeautifulSoup(source,'lxml')
    img = soup.find('meta',attrs={'property':'og:image'})
    img = img.get('content')
    return(img)

def itemName(links): #имя
    source = requests.get(links, headers=headers).text
    soup = BeautifulSoup(source, 'lxml')
    if (soup.find('h1')):
        name = soup.find('h1').get_text()
    else:
        name =''
    if (soup.find('h5')):
        name2 = soup.find('h5').get_text()
    else:
        name2 = ''
    name = name +' ' + name2
    return(name)


def itemDate(links):
    source = requests.get(links, headers=headers).text
    soup = BeautifulSoup(source, 'lxml')
    if (soup.find('startEntryDate')):
        print('found')
    else:
        print('not found')
    # if (soup.find('div', attrs={'class': 'test-available-date-component'})):
    #     date = soup.find('div', attrs={'class': 'available-date-component ncss-brand pb6-sm u-uppercase fs14-sm fs16-md'}).get_text()
    # else:
    #     date = 'Не удалось получить дату'
    # print(date)

while True:
    monitor()