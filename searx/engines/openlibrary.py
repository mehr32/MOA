# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 openlibrary (books)
"""

from json import loads
from urllib.parse import urlencode

# about
about = {
    "website": 'https://openlibrary.org',
    "wikidata_id": 'Q1201876',
    "official_api_documentation": 'https://openlibrary.org/dev/docs/api',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

# engine dependent config
categories = ['it']

# search-url
search_url = 'https://openlibrary.org/search.json?q={query}'  # noqa

accept_header = 'application/vnd.openlibrary.preview.text-match+json'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))

    params['headers']['Accept'] = accept_header

    return params




site_url = 'https://openlibrary.org'
# get response from search-request
def response(resp):
    results = []
    book_info = []
    data = resp.json()
    results = data.get('docs', [])
    for result in results:
        book_info.append({'key': result.get('key', ''), 'title': result.get('title', '')})
    url_k = "https://openlibrary.org"
    content = ""
    for info in book_info:
        results.append({'url': url_k + info['key'], 'title': info['title'], 'content': content})
    # return results
    return results
