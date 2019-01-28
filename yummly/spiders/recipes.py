# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from yummly.items import YummlyItem


class RecipesSpider(CrawlSpider):
    name = 'recipes'
    allowed_domains = ['yummly.com']
    start_urls = ['https://yummly.com/recipes/']

    rules = [
        Rule(
            LinkExtractor(allow=[r'recipe/\w+']),
            callback='parse_recipe_page',
            follow=True
        )
    ]

    def parse_recipe_page(self, response):
      title = response.css('h1::text').extract_first().strip()
      recipe_photo = response.css('div.recipe-details-image > img::attr(src)').extract_first()
      ingredients = [''.join(li.css('span::text').extract()).replace(
          u'\xa0', u' ').strip() for li in response.css('div.recipe-ingredients li')]
      half_stars = float(response.css(
          '#reviews span.half-star ::attr(data-star-number)').extract_first(default=0))
      full_stars = float((response.css(
          'a.recipe-details-rating span.full-star ::attr(data-star-number)').extract() or [0])[-1])
      ratings = full_stars + (0.5 if full_stars < 5 and half_stars else 0.0)
      reviews = int(response.css('#reviews span::text').extract_first().strip('()'))
      cook_time = ' '.join(response.css('div.recipe-summary-item.unit span::text').extract()).replace(u'\xa0', u' ').strip()
      serve = int(response.css('div.servings input::attr(value)').extract_first(default=1))
      item = YummlyItem()
      item['recipeUrl'] = response.url
      item['recipeName'] = title
      item['recipePhoto'] = recipe_photo
      item['ingredients'] = ingredients
      item['ratings'] = ratings
      item['reviews'] = reviews
      item['cookTime'] = cook_time
      item['serve'] = serve
      yield item
