#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from util import *
import lxml.html
import csv
import sys
import chardet
from bs4 import BeautifulSoup
import codecs

reload(sys)
sys.setdefaultencoding( "utf-8" )

class ScrapeCallback:
    def __init__(self, filename):
        self.fields = ('楼盘', '地点', '价格')
        self.writer_open = open('/tmp/%s.csv' % filename, 'w')
        self.writer_open.write(codecs.BOM_UTF8)
        self.writer = csv.writer(self.writer_open, dialect='excel')
        self.writer.writerow(self.fields)

        self.writer_open_noprice = open('/tmp/%s_noprice.csv' % filename, 'w')
        self.writer_open_noprice.write(codecs.BOM_UTF8)
        self.writer_noprice = csv.writer(self.writer_open_noprice, dialect='excel')
        self.writer_noprice.writerow(self.fields)

    def __call__(self, url, html):
        self.bs_call(url, html)

    def lxml_call(self, url, html):
        if re.search('/house/s/', url):
            type = sys.getfilesystemencoding()
            # html = html.decode('utf-8', 'ignore')
            # print html
            tree = lxml.html.fromstring(html)
            row = []
            print tree
            # tv = tree.cssselect('body > div#bx1 > div.nhouse_list_content > ul > li')
            tv = tree.cssselect('body > div#bx1')
            debug_print(tv[0].text_content())
            # if tv:
            #     row.append(tv[0].text_content())
            # debug_print("row %s" % str(row))
            # self.writer.writerow(row)

    def bs_call(self, url, html):
        if re.search('/house/s/', url):
            soup = BeautifulSoup(html, 'html.parser')
            div1 = soup.find('div', attrs={'id':'bx1', 'class':'main_1200 tf'})
            div2 = div1.find('div', attrs={'class':'content hidden main_1200 contenttwo'})
            div3 = div2.find('div', attrs={'class': 'contentListf fl clearfix'})
            div4 = div3.find('div', attrs={'class': 'nhouse_list_content'})
            div_nhouse_list = div4.find('div', attrs={'class':'nhouse_list'})
            div_nl_con_clearfix = div_nhouse_list.find('div', attrs={'class':'nl_con clearfix'})
            ul = div_nl_con_clearfix.find('ul')
            li_all = ul.find_all('li')
            for li in li_all:
                house_name = ""
                house_addr = ""
                house_price = ""
                div_clearfix = li.find('div', attrs={'class':'clearfix'})
                div_nlc_details = div_clearfix.find('div', attrs={'class':'nlc_details'})
                div_house_value_clearfix = div_nlc_details.find('div', attrs={'class':'house_value clearfix'})
                div_nlcd_name = div_house_value_clearfix.find('div', attrs={'class':'nlcd_name'})
                house_name = div_nlcd_name.find('a').text

                div_relative_message_clearfix = div_nlc_details.find('div', attrs={'class':'relative_message clearfix'})
                div_address = div_relative_message_clearfix.find('div', attrs={'class':'address'})
                house_addr = div_address.find('a')['title']

                div_nhouse_price = div_nlc_details.find('div', attrs={'class':'nhouse_price'})
                if div_nhouse_price:
                    house_price = div_nhouse_price.find('span').text
                if house_price.isdigit():
                    self.writer.writerow([house_name.strip(), house_addr, house_price.strip()])
                elif house_price:
                    self.writer_noprice.writerow([house_name.strip(), house_addr, house_price.strip()])
                # print chardet.detect(house_name)
                print house_name.strip(), " ", house_addr, " ", house_price





