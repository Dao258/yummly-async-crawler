# yummly
> Async crawler to fetch as many recipes possible starting from https://www.yummly.com/recipes

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

## Suggestions on adding bonus features
- `tags`
  1. Use NLTK library to filter webpage text with a predefined cooking related list of stopwords
  2. Extend 1 by intersecting the above mentioned extracted tag words of a recipe with those of the immediate neighboring recipes (may require caching)
- `recipeType`
  1. ???Maybe use LSA???

## Improvements
- Implement classes for async functions and prevent usage of global vars
- Make it faster by debugging workers' context switches
