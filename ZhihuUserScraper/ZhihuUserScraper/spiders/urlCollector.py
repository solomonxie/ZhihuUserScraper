# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlparse, urlencode


class UrlCollector(scrapy.Spider):
    name = 'UrlCollector'
    allowed_domains = ['zhihu.com']
    ids = [
        'sizhuren',
    ]
    url_followers = 'https://www.zhihu.com/api/v4/members/{}/followers'
    url_followees = 'https://www.zhihu.com/api/v4/members/{}/followees'

    def start_requests(self):
        for id in self.ids:
            url = furl( self.url_followers.format(id) )
            yield scrapy.Request(url=url, callback=self.parse)
            url = furl( self.url_followees.format(id) )
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pass


def furl(url, params={}):
    return url + ('&' if urlparse(url).query else '?') + urlencode(params)
