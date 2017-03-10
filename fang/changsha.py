#!/usr/bin/python
# -*- coding: utf-8 -*-

from link_crawler import link_crawler
from crawler import ScrapeCallback

def newhouse(zone):
    sc = ScrapeCallback('newhouse_%s' % zone)
    for i in range(1,7):
        link_crawler('http://newhouse.cs.fang.com/house/s/%s/b9%d' % (zone, i), delay=2,
                     num_retries=1, max_depth=1, scrape_callback=sc)

if __name__ == '__main__':
    newhouse('yuhua')
    # link_crawler('http://newhouse.cs.fang.com', delay=2, num_retries=1, max_depth=1)

