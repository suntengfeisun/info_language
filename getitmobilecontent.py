# -*- coding: utf-8 -*-

import time
import requests
from lxml import etree
from public.mysqlpooldao import MysqlDao
from public.headers import Headers


def get_content():
    mysql_dao = MysqlDao()
    no_xpath = False
    while True:
        sql = 'select `url`,`cate` FROM it_url WHERE `type`=0 limit 10'
        res = mysql_dao.execute(sql)
        if len(res) == 0:
            break
        if len(res) > 0:
            for r in res:
                url = r[0]
                cate = r[1]
                sql = 'update it_url SET `type`=2 WHERE `url`="%s"' % url
                try:
                    mysql_dao.execute(sql)
                except:
                    mysql_dao = MysqlDao()
                headers = Headers.get_headers()
                print(url)
                try:
                    req = requests.get(url, headers=headers)
                except:
                    time.sleep(600)
                    req = requests.get(url, headers=headers)

                if req.status_code == 200:
                    try:
                        html = req.content
                        selector = etree.HTML(html)
                        if 'myexception' in url:
                            titles = selector.xpath('//div[@class="c_t"]/h1[1]/text()')
                            contents = selector.xpath('//div[@class="c_txt"]/descendant::text()')
                        if '51cto' in url:
                            if 'blog' in url:
                                titles = selector.xpath('//div[@class="showTitle"]/text()')
                                contents = selector.xpath('//div[@class="showContent"]/descendant::text()')
                            else:
                                titles = selector.xpath('//div[@class="brief bgF8F8F8"]/h1[1]/text()')
                                contents = selector.xpath('//div[@id="content"]/descendant::text()')
                                if len(titles) == 0 or len(contents) == 0:
                                    titles = selector.xpath('//div[@class="wznr"]/h2[1]/text()')
                                    contents = selector.xpath('//div[@class="zwnr"]/descendant::text()')
                        if 'iteye' in url:
                            titles = selector.xpath('//div[@class="blog_title"]/h3[1]/a/text()')
                            contents = selector.xpath('//div[@id="blog_content"]/descendant::text()')
                        if len(titles) > 0 and len(contents) > 0:
                            title = titles[0].replace('\n', '').replace('\t', '').replace(' ', '')
                            if title == '':
                                title = titles[1].replace('\n', '').replace('\t', '').replace(' ', '')
                            content = ''
                            for c in contents:
                                content = content + '{ycontent}' + c.replace('"', '').replace('\'', '')
                            sql = 'insert ignore into it_content (`title`,`content`,`category_id`) VALUES ("%s","%s","%s")' % (
                                title, content, cate)
                            try:
                                mysql_dao.execute(sql)
                            except:
                                mysql_dao = MysqlDao()
                        else:
                            no_xpath = True
                    except Exception as e:
                        print(e)
                if no_xpath:
                    sql = 'update it_url SET `type`=3 WHERE `url`="%s"' % url
                    no_xpath = False
                else:
                    sql = 'update it_url SET `type`=1 WHERE `url`="%s"' % url
                try:
                    mysql_dao.execute(sql)
                except:
                    mysql_dao = MysqlDao()


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(u'开始获取分类下文章内容...')
    get_content()
    print(u'获取完成...')
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
