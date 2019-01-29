#/usr/bin/env
"""A simple async web crawler"""

import asyncio
import argparse
import logging
import sys
import json
import re
from typing import Dict
from urllib import parse

import aiohttp
import async_timeout
import html5lib
from bs4 import BeautifulSoup
from pprint import pformat

from utils import get_parent_url


parser = argparse.ArgumentParser(description='Run web crawler asynchronously')
parser.add_argument('--url', type=str, required=True, help='Source URL to start the crawler from')
parser.add_argument('--workers', type=int, default=5, help='Number of workers to crawl')
parser.add_argument('--verbose', action='store_true', help='Detailed output to stdout')
parser.add_argument('--save', action='store_true', help='Save to crawler_recipes.json file')

logging.basicConfig(stream=sys.stdout, format="%(message)s")
log = logging.getLogger()
log.setLevel(logging.INFO)

crawled_urls = set()


def update_queue(queue: asyncio.Queue, soup: BeautifulSoup, regexp: str, parent_url: str) -> None:
  """Update queue with new links

  Args:
    queue (asyncio.Queue): The asyncio queue that the work has to be done on
    soup (BeautifulSoup): BeautifulSoup object for the page
    regex (str): Reg exp to validate recipe URL
    parent_url (str): Parent URL
  """

  for link in soup.find_all('a', href=True):
    new_link = parse.urljoin(parent_url, link['href'])
    if re.search(regexp, new_link) and get_parent_url(new_link) == parent_url and new_link not in crawled_urls:
      queue.put_nowait(new_link)


def process_recipe(recipe: Dict, verbose: bool = False, save: bool = False) -> None:
  """Process recipe dictionary based on verbose printing option or saving to JSON

  Args:
    recipe (Dict): Recipe information
    verbose (bool, optional): Defaults to False. Flag to log out to terminal
    save (bool, optional): Defaults to False. Flag to save to crawler_recipes.json file
  """

  if verbose:
    log.info(pformat(recipe))
  elif save:
    with open('crawler_recipes.json', 'a+') as f:
      f.write(json.dumps(recipe) + '\n')


def parse_page_soup(url: str, soup: bytes) -> Dict:
  """Parse the recipe page soup to get required recipe information

  Args:
    url (str): Recipe URL from which the page bytes are fetched
    soup (BeautifulSoup): BeautifulSoup object for the page

  Returns:
    Dict: Recipe information
  """

  recipe_name = soup.select('h1')[0].text
  recipe_photo = soup.select('div.recipe-details-image > img')[0]['src']
  ingredients = [' '.join([t.text for t in li.find_all('span', recursive=False)]).replace(
      u'\xa0', u' ').strip() for li in soup.select('div.recipe-ingredients li')]
  half_star_tags = soup.select('#reviews span.half-star')
  full_stars_tags = soup.select('a.recipe-details-rating span.full-star')
  half_star = float(half_star_tags[0]['data-star-number']) if half_star_tags else 0.0
  full_stars = float(full_stars_tags[-1]['data-star-number']) if full_stars_tags else 0.0
  ratings = full_stars + (0.5 if full_stars < 5 and half_star else 0.0)
  reviews = int(soup.select('#reviews span')[0].text.strip('()'))
  cook_time = ' '.join(t.text for t in soup.select(
      'div.recipe-summary-item.unit span')).replace(u'\xa0', u' ')
  serve_tags = soup.select('div.servings input')
  serve = int(serve_tags[0]['value']) if serve_tags else 1
  return dict(recipeName=recipe_name,
              recipePhoto=recipe_photo,
              ingredients=ingredients,
              ratings=ratings,
              reviews=reviews,
              cookTime=cook_time,
              serve=serve)


async def get_page_bytes(url: str) -> bytes:
  """Get page in bytes from URL

  Args:
    url (str): URL to fetch the page from

  Returns:
    bytes: Page in bytes
  """

  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        page_bytes = await response.read()
        return page_bytes
      return None


async def crawl(queue: asyncio.Queue,
                parent_url,
                verbose: bool = False,
                save: bool = False,
                regex: str = r'/recipe/.+') -> None:
  """Crawls URLs in the queue while updating the queue itself with URLs

  Args:
    queue (asyncio.Queue): The asyncio queue that the work has to be done on
    parent_url (str): Parent URL
    verbose (bool, optional): Defaults to False. Flag to log out to terminal
    save (bool, optional): Defaults to False. Flag to save to crawler_recipes.json file
    regex (str, optional): Defaults to r'/recipe/.+'. Reg exp to validate recipe URL
  """

  global crawled_urls
  try:
    while True:
      url = await queue.get()
      if url not in crawled_urls:
        crawled_urls.add(url)
        page_bytes = await get_page_bytes(url)
        if page_bytes:
          soup = BeautifulSoup(page_bytes.decode('utf-8'), 'html5lib')
          recipe = parse_page_soup(url, soup)
          process_recipe(recipe, verbose, save)
          update_queue(queue, soup, regex, parent_url)
      queue.task_done()
  except asyncio.CancelledError:
    log.debug('Error: The worker has been cancelled; perhaps on purpose')
    pass


def main() -> None:
  """Parses commandline arguments, starts async IO events loop and creates workers to work on queue
  """

  args = parser.parse_args()
  parent_url = get_parent_url(args.url)
  if not parent_url:
    raise Exception('Unsupported URL provided')
  if not args.verbose and args.save:
    with open('crawler_recipes.json', 'w'):
      pass
  loop = asyncio.get_event_loop()
  queue = asyncio.Queue()
  queue.put_nowait(args.url)
  workers = [asyncio.ensure_future(crawl(queue, parent_url, verbose=args.verbose, save=args.save)) for _ in range(args.workers)]
  loop.run_until_complete(queue.join())
  for w in workers:
    w.cancel()
  loop.close()


if __name__ == '__main__':
  main()
