# First get a list of URLs to crawl this will serve as a comparison point for future crawls

import urllib.request
import requests
import re

article_list = [
"https://www.ecologylawquarterly.org/currents/currents35-11-boutrous-2008-0915/",
"https://www.ecologylawquarterly.org/currents/currents35-12-jones-2008-0915/",
"https://www.ecologylawquarterly.org/currents/currents35-01-chamberlain-2008-0411/",
"https://www.ecologylawquarterly.org/currents/currents35-02-smith-2008-0411/"
]

# from a list of all the URLs that I want to grab data from, grab specific data
def get_article_list(article_url_list):

    articles = {}
    titles = []
    title_pattern = re.compile(r'<h1\s?class=\s?"page-title"\s?>([^<]+)</h1>', re.I)
    for article in article_url_list:
        f = urllib.request.urlopen(article)
        contents = str(f.read())
        f.close()
        result = re.findall(title_pattern, contents)
        titles.extend(result)
    return titles



print(get_article_list(article_list))
