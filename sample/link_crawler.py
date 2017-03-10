#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urlparse
import urllib2
import time
import datetime
import robotparser
from downloader import Downloader
from util import *
from bs4 import BeautifulSoup
import lxml.html
import csv

class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('/tmp/countries.csv', 'w'))
        self.fields = ('country', 'area')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                tv = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))
                if tv:
                    row.append(tv[0].text_content())
            self.writer.writerow(row)

def get_country_area(url, html):
    if re.search("/view/", url):
        get_country_area_lxml(html)

def get_country_area_bs(html):
    country = ""
    area = ""
    soup = BeautifulSoup(html, 'html.parser')
    if soup:
        tr = soup.find('tr', attrs={"id": "places_country__row"})
        if tr:
            td = tr.find('td', attrs={'class': 'w2p_fw'})
            if td:
                country = td.text

        tr = soup.find('tr', attrs={"id":"places_area__row"})
        if tr:
            td = tr.find('td', attrs={'class':'w2p_fw'})
            if td:
                area = td.text
    if country or area:
        print "%s area : %s" % (country, area)

def get_country_area_lxml(html):
    country = ""
    area = ""
    tree = lxml.html.fromstring(html)
    countrytree = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format('country'))
    if countrytree:
        country = countrytree[0].text_content()

    areatree = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format('area'))
    if areatree:
        area = areatree[0].text_content()
    if country or area:
        print "%s area : %s" % (country, area)

def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, user_agent='wswp', proxies=None,
                 num_retries=1, scrape_callback=None, cache=None):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # the queue of URL's that still need to be crawled
    debug_print("first crawler url %s ua %s" % (seed_url, user_agent))
    crawl_queue = [seed_url]
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    while crawl_queue:
        url = crawl_queue.pop()
        debug_print("start crawler url %s" % url)
        depth = seen[url]
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            html = D(url)
            get_country_area(url, html)
            # debug_print("get url %s --> html %s" % (url, html))
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])

            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            debug_print('Blocked by robots.txt:%s' % url)


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link)  # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def get_links(html):
    """Return a list of links from html
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=2, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=2, num_retries=1, max_depth=1,
                 user_agent='GoodCrawler', scrape_callback=ScrapeCallback())
