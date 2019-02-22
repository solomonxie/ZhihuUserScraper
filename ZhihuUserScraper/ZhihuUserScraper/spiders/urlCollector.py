# -*- coding: utf-8 -*-
import scrapy


class UrlCollector(scrapy.Spider):
    name = 'UrlCollector'
    allowed_domains = ['zhihu.com']

    def start_requests(self):
        urls = [
            'https://www.zhihu.com/api/v4/members/{}/followees'
        ]
        for u in urls:
            yield scrapy.Request(url=u, headers={}, callback=self.parse)

    def parse(self, response):
        pass
