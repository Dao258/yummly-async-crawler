# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YummlyItem(scrapy.Item):
  recipeUrl  = scrapy.Field()
  recipeName = scrapy.Field()
  recipePhoto = scrapy.Field()
  ingredients = scrapy.Field()
  ratings = scrapy.Field()
  reviews = scrapy.Field()
  cookTime = scrapy.Field()
  serve = scrapy.Field()
