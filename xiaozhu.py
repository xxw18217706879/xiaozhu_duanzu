import requests
import re
import json
import pymongo
from bs4 import BeautifulSoup
from config import *

client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]

headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
}
def proxy():
    response=requests.get('http://api.logicjake.xyz/get_proxy/?_action=getIP&validcode=xuxiaowu')
    if response.status_code==200:
        response_proxy=response.text
        response_proxy=json.loads(response_proxy)
        if response_proxy['code']==0:
            ip_port=response_proxy['data']
            proxy_=ip_port['IP']+":"+ip_port['PORT']
            return proxy_


def get_page(url):
    try:
        proxy_=proxy()
        print(proxy_)
        proxies={"http":'http://'+proxy_}#使用代理
        response=requests.get(url,headers=headers,proxies=proxies,timeout=10)
        print(response.status_code )
        if response.status_code==200:
            return response.text
        else:
            return get_page(url)
    except Exception :
        print("请求网页失败")
        return get_page(url)

def get_page_detail(html):
    soup=BeautifulSoup(html,'lxml')
    results=soup.find_all(name='li',lodgeunitid=re.compile("lodgeunit_"))
    for result in results:
        href=(result.find('a',class_='resule_img_a')['href'])
        image_src=(result.find(name='img')['lazy_src'])
        title=(result.find('span',class_='result_title hiddenTxt').get_text())
        price=(result.find('span',class_='result_price').get_text())
        hiddentxt=(result.find(name='em').get_text().split('-')[0].strip())
        comment=(result.find(name='em').get_text().split('-')[1].strip())
        informations=(result.find_all(name='span',title=re.compile("")))
        other_information=[]
        for information in informations:
            other_information.append(information['title'])
        yield{
            "href":href,
            "image_src":image_src,
            "title":title,
            "price":price,
            "hiddentxt":hiddentxt,
            "comment":comment,
            "other_information":other_information
        }

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("save to mongo succesfully",result)
    except Exception as e:
        print(e)
        print("fail")


def main():
    if db[MONGO_TABLE]:
            db[MONGO_TABLE].drop()
    urls=["http://{}.xiaozhu.com/search-duanzufang-p{}-0/".format(CITY,str(i)) for i in range (1,14)]
    for url in urls:
        print("正在爬取",url)
        html=get_page(url)
        for item in get_page_detail(html):
            save_to_mongo(item)

if __name__=="__main__":
    main()

