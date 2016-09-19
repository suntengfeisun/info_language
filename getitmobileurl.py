# -*- coding: utf-8 -*-

import time
import requests
import re
from lxml import etree
from public.mysqlpooldao import MysqlDao
from public.headers import Headers


def get_category():
    mysql_dao = MysqlDao()
    sql = 'select * from  it_category'
    res = mysql_dao.execute(sql)
    return res


def get_myexception(cate_id, cate_url):
    headers = Headers.get_headers()
    req = requests.get(cate_url, headers=headers, timeout=30)
    if req.status_code == 200:
        html = req.content
        selector = etree.HTML(html)
        last_pages = selector.xpath('//div[@class="c_p_s"]/ul/font/li[last()]/a/@href')
        if len(last_pages) > 0:
            last_page = last_pages[0]
            match_obj = re.match(r'index_(.*?).html', last_page, re.M | re.I)
            page_num = int(match_obj.group(1))
            mysql_dao = MysqlDao()
            while True:
                if page_num <= 0:
                    break
                list_url = cate_url + 'index_%s.html' % page_num
                headers = Headers.get_headers()
                try:
                    print(list_url)
                    req = requests.get(list_url, headers=headers, timeout=10)
                    if req.status_code == 200:
                        html = req.content
                        selector = etree.HTML(html)
                        urls = selector.xpath('//div[@class="c_c"]/ul/li/a[1]/@href')
                        for url in urls:
                            sql = 'insert ignore into it_url(`url`,`cate`,`type`) VALUES ("%s",%s,0)' % (
                                url, cate_id)
                            mysql_dao.execute(sql)
                except:
                    print(list_url, 'timeout')
                page_num = page_num - 1


def get_51cto_lastpage_word(url):
    match_obj = re.search(r'keywords=(.*?)&sort=(.*?)&p=(.*)', url, re.M | re.I)
    last_page = int(match_obj.group(3))
    word = match_obj.group(1)
    return (last_page, word)


def get_51cto_url(url, page_num):
    match_obj = re.search(r'(.*?)%s' % page_num, url, re.M | re.I)
    list_url = match_obj.group(1)
    return list_url


def get_51cto(cate_id, cate_url):
    (page_num, word) = get_51cto_lastpage_word(cate_url)
    list_urll = get_51cto_url(cate_url, page_num)
    mysql_dao = MysqlDao()
    while True:
        if page_num == 0:
            break
        list_url = list_urll + str(page_num)
        headers = Headers.get_headers()
        try:
            print(list_url)
            req = requests.get(list_url, headers=headers, timeout=10)
            if req.status_code == 200:
                html = req.content
                selector = etree.HTML(html)
                urls = selector.xpath('//div[@class="res-doc"]/h2/a[1]/@href')
                for url in urls:
                    print(url)
                    sql = 'insert ignore into it_url(`url`,`cate`,`type`) VALUES ("%s",%s,0)' % (
                        url, cate_id)
                    mysql_dao.execute(sql)
        except:
            print(list_url, 'timeout')
        page_num = page_num - 1


def get_iteye_lastpage_word(url):
    match_obj = re.search(r'page=(.*?)&query=(.*?)&type', url, re.M | re.I)
    last_page = int(match_obj.group(1))
    word = match_obj.group(2)
    return (last_page, word)


def get_iteye(cate_id, cate_url):
    (page_num, word) = get_iteye_lastpage_word(cate_url)
    mysql_dao = MysqlDao()
    while True:
        if page_num == 0:
            break
        list_url = 'http://www.iteye.com/search?page=%s&query=%s&type=blog' % (page_num, word)
        headers = Headers.get_headers()
        try:
            print(list_url)
            req = requests.get(list_url, headers=headers, timeout=10)
            if req.status_code == 200:
                html = req.content
                selector = etree.HTML(html)
                urls = selector.xpath('//div[@class="content"]/h4/a[1]/@href')
                for url in urls:
                    print(url)
                    sql = 'insert ignore into it_url(`url`,`cate`,`type`) VALUES ("%s",%s,0)' % (
                        url, cate_id)
                    mysql_dao.execute(sql)
        except:
            print(list_url, 'timeout')
        page_num = page_num - 1


def get_url(cates):
    for cate in cates:
        print(cate)
        cate_id = cate[0]
        cate_urls = []
        cate_urls.append(cate[2])
        cate_urls.append(cate[3])
        cate_urls.append(cate[4])
        for cate_url in cate_urls:
            if 'myexception' in cate_url:
                get_myexception(cate_id, cate_url)
            elif 'iteye' in cate_url:
                get_iteye(cate_id, cate_url)
            elif '51cto' in cate_url:
                get_51cto(cate_id, cate_url)


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(u'开始获取分类url...')
    cates = get_category()
    print(u'获取分类url完成...')
    print(u'开始获取分类下文章url...')
    get_url(cates)
    print(u'获取完成...')
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
