import requests
import datetime
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import time

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

item ={}

def monitor():
    source = requests.get('https://brandshop.ru/obuv/?limit=240&mfp=manufacturers[11,308,47,811,46]',headers = headers).text
    soup = BeautifulSoup(source,'lxml')
    for hrefs in soup.findAll('div', attrs ={'class':'product-container'}):
        if (getName(hrefs) != 'Not right'):
            if checkBlackList(hrefs):
                send_webhook(hrefs)

    time.sleep(7)

def monitoring():
    source = requests.get('https://brandshop.ru/goods/259038/c-bb550ae1/',headers).text
    soup = BeautifulSoup(source, 'lxml')
    send_webhook(soup)

    time.sleep(10)
# проверяю на ненужные вещи
def checkBlackList(hrefs):
    # черный список айтемов
    filename = 'brandshop/BS_blacklist.txt'
    with open(filename, 'r') as rf:
        with open(filename, 'a') as af:
            read = rf.read()
            # если текущего айтема нет в черном листе
            if getLink(hrefs) not in read:
                # закрываю файлы
                rf.close()
                af.close()
                # возвращаем добро
                return True
            # иначе все плохо
            else:
                # закрываю файлы
                rf.close()
                af.close()
                return False


#   получаю картинку
def getPic(hrefs):
    picture = hrefs.find('div',attrs = {'class':'product'}).find('img').get('src')
    return(picture)


#   пока не используется данная функция
#   получаю тип вещи, по нему буду делать решение, нужно ли выводить вещи впоследствии
def getType(hrefs):
    type = hrefs.find('span').get_text()
    if (type.find('/') !=- 1):
        type = hrefs.find_all('span')[3].get_text()
    if (type.startswith('Кроссовки') or type.endswith('кроссовки')):
        return(type)
    else:
        return('Not right')


#   получаю название модели
#   задаю кейворды
def getName(hrefs):
    #   по каким кейвордам будет поиск
    # keywords = ('Dunk','dunk','YEEZY','Jordan','Yeezy','SB','Force', 'Air Jordan 1')
    keywords =('YEEZY Boost 350', 'YEEZY Boost 380', 'Air Jordan 1 Retro High OG','Air Jordan 1','Dunk','dunk','SB','Travis Scott', 'Cactus Jack', 'Air Jordan', 'P550')
    name = hrefs.find('h2').find_all('span')[1].get_text()

    if (name.startswith(keywords) or name.endswith(keywords)):
        return (name)
    else:
        return ('Not right')



#   получаю размер
def getSize(hrefs):
    item_size = []
    ssize=''
    link = getLink(hrefs)
    source = requests.get(link,headers=headers).text
    soup = BeautifulSoup(source, 'lxml')
    try:
        # статичные
        option_id = soup.find('div',attrs={'class':'product-size'}).findAll('input')[0]['name'][7:-1]
        product_id = soup.find('div', attrs={'class': 'product-size'})['data-product-id']
    except:
        pass

    try:
        sizes = soup.findAll('div', attrs={'class': 'sizeselect'})
        for i in sizes:
            # меняющиеся
            data_option_id = i.get('data-option-id')
            option_value_id = i.get('data-option-value-id')
            ssize+= i.get_text() + '\n'
            # массив размеров, который буду клеить
            item_size.append(i.get_text() +  '[['+'ATC'+']]('+ f'https://pasichniy-private.com/pages/brandshop?product_id={product_id}&option_value_id={option_value_id}&option_id={option_id}&option={data_option_id}' +')' +"\n")
        return(ssize, item_size)

    except:
        return('no sizes')

#   записываю в словарь
#   проверяю новизну размеров
def write_json(link,size):
    # если вещь есть в словаре
    try:
        if (item[link]):
            # если размеры одинаковы
            if (size in item[link]):
                # не выводим эмед
                # print(item[link])
                return False
            else:
                # обновляем размеры
                item[link] = size
                # выводим эмбед
                # print(item[link])
                return True
        # если ее нет
        else:
            # просто добавляем
            item[link] = size
            # выводим эмбед
            # print(item[link])
            return True
    except:
        # просто добавляем
        item[link] = size
        # выводим эмбед
        # print(item[link])
        return True

# новая функция проверки размера
def sizeCheck(link,size):
    sum = 0
    for i in size:
        sum += ord(i)
    print(sum)
    try:
        # если с размерами ничего не изменилось
        if item[link] == sum:
            return False
        # произошли изменения
        else:
            # записываю последние данные в словарь
            item[link] = sum
            return True
    # если записи о размерах нет
    except:
        item[link] = sum
        return True

#   отправляю вебхук
def send_webhook(hrefs):
    # строка с сайзами(для проверки)
    size = getSize(hrefs)[0]
    # массив с сайзами и атк(для красивого вывода)
    item_size = getSize(hrefs)[1]
    # ссылка на айтем
    link = getLink(hrefs)
    # название айтема
    name = getName(hrefs)

    if (len(size)>0 and sizeCheck(link,size)):
        # webhook = 'https://discordapp.com/api/webhooks/692754545113038868/XhJ6dvwII-TDdoIX2MMA3SrnmFXdZXp8PbeSDAgl8p0UqdIktDK6O4nd2gjpJAryTBXt'
        webhook = 'https://discordapp.com/api/webhooks/706058068512866325/fuicGAprHTGZ86FQE0TED62Ik6VaHrHcI1-UE-MN3KCI12cKarI5MrAkDoBg1M1rWXm9'
        webhook = DiscordWebhook(url=webhook)
        embed = DiscordEmbed(title=name, url=link, color='16711680')
        now_date = datetime.datetime.now()
        embed.set_footer(
            icon_url='https://media.discordapp.net/attachments/672887506328617011/705884836807573564/BLESSED_LOGO_HAND_final.png?width=523&height=523',
            text='Exclusive for "BLESSED" \nGot at : {}'.format(now_date))
        embed.set_thumbnail(url=getPic(hrefs))
        embed.add_embed_field(name='Type', value=checkStatus(hrefs), inline=True)
        embed.add_embed_field(name='Price', value=getPrice(hrefs), inline=True)
        embed.add_embed_field(name='Site', value='[Brandshop](https://brandshop.ru)', inline=True)

        # обработчик размеров
        i = 0
        string = ''
        while i != (len(item_size)):

            # создание колонки
            if (i % 5 == 0 and i != 0) or (i == len(item_size)-1):
                string += item_size[i]
                embed.add_embed_field(name='Sizes', value=string, inline=True)
                string = ''
            # иначе простое добавление текста
            else:
                string += item_size[i]

            i += 1

        embed.add_embed_field(name='Important links',
                              value="[Brandshop login](https://brandshop.ru/login/)\n [Cart](https://brandshop.ru/cart/)"
                                    "\n [Checkout](https://brandshop.ru/checkout/)\n [Lottery](https://lottery.brandshop.ru/)")
        webhook.add_embed(embed)
        webhook.execute()

        print(name)
    else:
        pass


#   получаю ссылку на айтем
def getLink(hrefs):
    name = getName(hrefs)
    # Если подходит название под кейворды
    if (name != 'Not right'):
        # если есть надпись подробности скоро
        if (hrefs.find('div',attrs={'class':'special'})):
            if (hrefs.find('div',attrs={'class':'special'}).findChild().get_text() == 'Подробности скоро'):
                # print('Item soon')
                name = name.replace(" ","")
                return 'https://brandshop.ru/sneakers/?' + name
            else:
                productLink = hrefs.find('a').get('href')
                return(productLink)
        else:
            productLink = hrefs.find('a').get('href')
            return (productLink)


#   получаю тип уведомления
def checkStatus(hrefs):
    link = getLink(hrefs)
    if (link == 'https://brandshop.ru/sneakers/'):
        return 'Soon'

    filename = 'brandshop/BS.txt'
    with open(filename, 'r') as rf:
        with open(filename, 'a') as af:
            read = rf.read()
            if link not in read:
                af.write(link + '\n')
                # закрываю файлы
                rf.close()
                af.close()
                return 'New item'
            else:
                if (hrefs.find('div',attrs={'class':'special'}) and hrefs.find('div',attrs={'class':'special'}).findChild().get_text() == 'Нет в наличии'):
                    # закрываю файлы
                    rf.close()
                    af.close()
                    return 'Sold out'
                else:
                    # закрываю файлы
                    rf.close()
                    af.close()
                    return 'Restock'


#   получаю цену вещи
def getPrice(hrefs):
    if(hrefs.find_all('div',attrs={'class':'price'})):
        price = hrefs.find('div', attrs={'class': 'price'}).get_text().replace(' ','').replace('\n','')
        return price
    else:
        return 'Soon'

while True:
    try:
        monitor()
    except:
        pass

