# yummly - Chefling task
> Crawler to fetch as many recipes possible starting from https://www.yummly.com/recipes

## Prerequisites
- Python 3.7+ with `pip`
- Pipenv (`pip install pipenv`)

## Install
```pipenv install```

## Scrapy crawler
- Run using
  ```scrapy crawl recipes```
- Add `--nolog` flag to run without logs
- `Ctrl + C` twice to stop crawler
- To log the results into JSON
  1. Go to `settings.py`
  2. Uncomment lines 68-70
  > WARNING: Large file may be generated if crawler had run for long
  1. Check `recipes.json` with results

## Run custom crawler
> In Progress
