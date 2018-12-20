# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EatItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    calories = scrapy.Field()
    proteins = scrapy.Field()
    fats = scrapy.Field()
    carbohydrates = scrapy.Field()
    ingredients = scrapy.Field()
    portionsCount = scrapy.Field()
    cookingTime = scrapy.Field()
    link = scrapy.Field()
    tags = scrapy.Field()
    imagesLinks = scrapy.Field()
