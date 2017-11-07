# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GamePageItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    path = scrapy.Field()
    referer = scrapy.Field()


class LinkItem(scrapy.Item):
    last = scrapy.Field()
    next = scrapy.Field()
