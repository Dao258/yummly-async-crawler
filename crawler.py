"""A simple async web crawler"""

import asyncio
import argparse
import logging
import sys
import json
from typing import Dict

import aiohttp
import async_timeout
import html5lib
from bs4 import BeautifulSoup
from pprint import pformat

parser = argparse.ArgumentParser(description='Run web crawler asynchronously')
parser.add_argument('--url', type=str, required=True, help='Source url to start the crawler from')
parser.add_argument('--workers', type=int, default=5, help='Number of workers to crawl')
parser.add_argument('--verbose', action='store_true', help='Detailed output')
parser.add_argument('--save', action='store_true', help='Save to crawler_recipes file')

logging.basicConfig(stream=sys.stdout, format="%(message)s")
log = logging.getLogger()
log.setLevel(logging.INFO)

crawled_urls = set()


def update_queue(queue: asyncio.Queue, soup: BeautifulSoup) -> None:
  """Update queue with new links

  Args:
    queue (asyncio.Queue): The asyncio queue that the work has to be done on
    soup (BeautifulSoup): BeautifulSoup object for the page
  """

  for url in soup.find_all('a', href=True):
    if url not in crawled_urls:
      queue.put_nowait(url)


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
    with open('crawler_recipes.json', 'w+') as f:
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
      await asyncio.sleep(0)
      if response.status == 200:
        page_bytes = await response.read()
        return page_bytes
      return None


async def process(url, verbose=False, save=False):
  page_bytes = await get_page_bytes(url)
  if page_bytes:
    soup = BeautifulSoup(page_bytes.decode('utf-8'), 'html5lib')
    recipe = parse_page_soup(url, soup)
    process_recipe(recipe, verbose, save)
    for link in soup.find_all('a', href=True):
      if link['href'] not in crawled_urls:
        log.info(link['href'])


async def crawl(queue: asyncio.Queue, verbose: bool = False, save: bool = False) -> None:
  """Crawls URLs in the queue while updating the queue itself with URLs

  Args:
    queue (asyncio.Queue): The asyncio queue that the work has to be done on
    verbose (bool, optional): Defaults to False. Flag to log out to terminal
    save (bool, optional): Defaults to False. Flag to save to crawler_recipes.json file
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
      queue.task_done()
  except asyncio.CancelledError:
    log.debug('Error: The worker has been cancelled; perhaps on purpose')
    pass


def main() -> None:
  """Parses commandline arguments, starts async IO events loop and creates workers to work on queue
  """

  args = parser.parse_args()
  if not args.verbose and args.save:
    with open('crawler_recipes.json', 'w'):
      pass
  # loop = asyncio.get_event_loop()
  # queue = asyncio.Queue()
  # queue.put_nowait(args.url)
  # workers = [asyncio.ensure_future(crawl(queue)) for _ in range(args.workers)]
  # loop.run_until_complete(queue.join())
  # for w in workers:
  #   w.cancel()
  # loop.close()
  event_loop = asyncio.get_event_loop()
  try:
      event_loop.run_until_complete(process(args.url, args.verbose, args.save))
  finally:
      event_loop.close()


if __name__ == '__main__':
  main()
