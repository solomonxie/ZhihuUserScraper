# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ZhihuuserscraperPipeline(object):

    def open_spider(self, spider):
        pass
        print('[PIPELINE] open:', spider)

    def process_item(self, item, spider):
        print('[PIPELINE] process:', item, spider)
        return item

    def close_spider(self, spider):
        pass
        print('[PIPELINE] close:', spider)
