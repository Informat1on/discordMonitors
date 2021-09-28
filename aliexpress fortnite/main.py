import requests
from bs4 import BeautifulSoup

headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}


def main():
    source = requests.get('https://www.mvideo.ru/products/igrovaya-pristavka-nintendo-switch-osoboe-izdanie-fortnite-40074554?cityId=CityCZ_2128',headers=headers).text
    soup = BeautifulSoup(source,'lxml')

    info = soup.find()


    print(soup)

main()