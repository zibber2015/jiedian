# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JiedianItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    location = scrapy.Field()
    menu = scrapy.Field()
    category = scrapy.Field()
    district = scrapy.Field()
    area = scrapy.Field()
    shop_name = scrapy.Field()
    vote_star = scrapy.Field()
    commit_num = scrapy.Field()
    taste = scrapy.Field()
    consume = scrapy.Field()
    env = scrapy.Field()
    server = scrapy.Field()
    address = scrapy.Field()
    tel = scrapy.Field()
    business_time = scrapy.Field()
    long = scrapy.Field()
    lat = scrapy.Field()
    created_at = scrapy.Field()
    dbname = scrapy.Field()