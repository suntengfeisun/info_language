# -*- coding: utf-8 -*-

import time
import requests
import re
from lxml import etree
from public.mysqlpooldao import MysqlDao
from public.headers import Headers

last_url = 'http://so.51cto.com/index.php?project=blog&keywords=C%23&sort=&p=953'
match_obj = re.search(r'keywords=(.*?)&sort=(.*?)&p=(.*)', last_url, re.M | re.I)
last_page = match_obj.group(3)
print(last_page)