# -*- coding: utf-8 -*-
import scrapy
import json


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['https://httpbin.org/ip']

    def start_requests(self):
        urls = [
            'http://httpbin.org/user-agent'
        ]
        for u in urls:
            yield scrapy.Request(url=u, callback=self.parse)

    def parse(self, response):
        item = {}
        # item['url_token'] = 'Jason123'
        item['user-agent'] = json.loads(response.body).get('user-agent')
        print('[SPIDER]', item, response.url)
        yield item

        url = 'http://quotes.toscrape.com/page/{}/'
        # for i in range(3,4):
            # yield scrapy.Request(url=url.format(i), callback=self.parse)
