import bs4
import requests
from lxml import etree
import re
import threading
import csv

site = requests.get('https://yacht-parts.ru/sitemap.xml')

class Item:
    def __init__(self,category,name,price,article,brand,imgs,description) -> None:
        self._category = category
        self._name = name
        self._price = price
        self._article = article
        self._brand = brand
        self._imgs = imgs
        self._description = description

    @property
    def category(self):
        return self._category

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def article(self):
        return self._article

    @property
    def brand(self):
        return self._brand

    @property
    def imgs(self):
        return self._imgs

    @property
    def description(self):
        return self._description

items_list = []

def parse_site(site_text):
    site = bs4.BeautifulSoup(site_text)
    category, name, price, article, brand, imgs, description = (None for i in range(7))
    # category
    category = site.find('div',attrs={'class':'breadcrumbs'}).find_all('span',attrs={'itemprop':'itemListElement'})[-2].find('a').attrs['title']
    # name
    name = site.find('h1',attrs={'id':'pagetitle'}).text.strip()
    if site.find('div',attrs={'class':'price'}).text.strip():
        price = site.find('div',attrs={'class':'price'}).text.strip()
    else:
        price = 'Под заказ'
    article = site.find('div',attrs={'class':'article'}).find_next('span',attrs={'class':'value'}).text.strip()
    if site.find('a',attrs={'class':'brand_picture'}):
        brand = site.find('a',attrs={'class':'brand_picture'}).find_next('img').attrs['title'].strip()
    else:
        brand = 'Бренд не указан'
    if site.find('div',attrs={'class':'thumbs'}):
        if site.find('div',attrs={'class':'thumbs'}).find_all('img'):
            imgs = ', '.join([ 'https://yacht-parts.ru'+i.attrs['src'] if 'https://yacht-parts.ru' not in i.attrs['src'] else i.attrs['src'] for i in site.find('div',attrs={'class':'thumbs'}).find_all('img')])
        else:
            imgs = 'https://yacht-parts.ru'+site.find('div',attrs={'class':'slides'}).find('img').attrs['src'] if 'https://yacht-parts.ru' not in site.find('div',attrs={'class':'slides'}).find('img').attrs['src'] else site.find('div',attrs={'class':'slides'}).find('img').attrs['src']

    else:
        imgs = 'https://yacht-parts.ru'+site.find('div',attrs={'class':'slides'}).find('img').attrs['src'] if 'https://yacht-parts.ru' not in site.find('div',attrs={'class':'slides'}).find('img').attrs['src'] else site.find('div',attrs={'class':'slides'}).find('img').attrs['src']
    description =  site.find('div',attrs={'class':'preview_text'}).text.strip()
    items_list.append(Item(category,name,price, article, brand, imgs, description))
    print('Done')

def get_req_url(url):
    site_text = requests.get(url).text
    print('\n'+url+'\n')
    if site_text.find('detail_page'):
        parse_site(site_text)

#print(site.text)

if __name__ == '__main__':
    all_url = []
    etr = etree.XML(site.content)
    nxml = etr.nsmap[None]
    thread_list = []
    list_urls = [ i.text for i in etr.findall('.//{%s}loc'%nxml) ]

    for url in list_urls:
        node = etree.XML(requests.get(url).content)
        node_nxml = node.nsmap[None]
        all_url.extend([i.text for  i in node.findall('.//{%s}loc'%node_nxml) if re.match(r'https://yacht-parts\.ru/catalog/\w+/\w+/.+/',i.text)])
    for index, url in enumerate(all_url):
        print(index+1,len(all_url))
        print('\n'+url+'\n')
        t = threading.Thread(target=get_req_url,args=(url,))
        t.start()
        thread_list.append(t)
        if index == 999:
            break

    for thred in thread_list:
        thred.join()

    with open('main.csv','w',encoding='utf-8') as file:
        wr_csv = csv.writer(file,delimiter=';')
        wr_csv.writerow(['name','category','brand','price','article','description'])
        for i in items_list:
            wr_csv.writerow([i.name,i.category,i.brand,i.price,i.article,i.description])

            #parse_site(site_text)
