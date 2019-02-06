# yummly
> Async crawler to fetch as many recipes possible starting from https://www.yummly.com/recipes

## Contents
- Scrapy crawler to spec out requirements
- Custom crawler using asyncio

## Prerequisites
- Python 3.7+ with `pip`
- Pipenv (`pip install pipenv`)

## Install
```pipenv install```


## Scrapy crawler
- Run using
  ```pipenv run scrapy crawl recipes```
- Add `--nolog` flag to run without logs
- `Ctrl + c` twice to stop crawler
- To log the results into JSON
  1. Go to `settings.py`
  2. Uncomment lines 68-70
  3. Check `recipes.json` with results

  > WARNING: Large file may be generated if crawler had run for long

## Custom crawler
- Run using
  ```pipenv run python crawler.py --url https://www.yummly.com/recipes```
- To get all commandline options
  ```pipenv run python crawler.py --help```

## Improvements
- Implement classes for async functions and prevent usage of global vars
- Make it faster by debugging workers' context switches
