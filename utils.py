"""Misc utils"""

from urllib.parse import urlparse


def get_parent_url(url: str) -> str:
  """Get parent url e.g., https://google.com/asdasda/1 -> https://google.com

  Args:
    url (str): Given url

  Returns:
    str: Parent url
  """

  try:
    url = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=url)
  except:
    return ''
