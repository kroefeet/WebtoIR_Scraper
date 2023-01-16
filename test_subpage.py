# First get a list of URLs to crawl this will serve as a comparison point for future crawls

import urllib.request
import requests
import re
import json
import csv

article_list = [
"https://www.ecologylawquarterly.org/currents/currents35-11-boutrous-2008-0915/",
"https://www.ecologylawquarterly.org/currents/currents35-12-jones-2008-0915/",
"https://www.ecologylawquarterly.org/currents/currents35-01-chamberlain-2008-0411/",
    "https://www.ecologylawquarterly.org/currents/currents35-02-smith-2008-0411/","https://www.ecologylawquarterly.org/currents/networkedfederalism/"
]

# from a list of all the URLs that I want to grab data from, grab specific data
def get_article_list(article_url_list):
# the articles container will contain all the fields scraped from individual articles
    articles = []
    title_pattern = re.compile(r'<h1\s?class=\s?"page-title"\s?>([^<]+)</h1>', re.I)
    date_pattern = re.compile(r'<p\s?class=\s?"single-date"\s?>([^<]+)</p>', re.I)
    #cat_pattern needs work to actually capture subjects
 #   cat_pattern = re.compile(r'<p\s?class=\s?"single-cat"\s?><a\s?href=\s?([^<]+)</p>', re.I)
    auth_pattern = re.compile(r'<p\s?style="text-align: center;"\s?>([^<]+)<a', re.I)
    alt_auth_pattern = re.compile(r'<p\s?class=\s?"single-editor-list"\s?>([^<]+)</p>', re.I)
    pdf_pattern = re.compile(r'.*href=\"([^\"]+\.pdf)\".*', re.I)
    for article in article_url_list:
        f = urllib.request.urlopen(article)
        contents = str(f.read())
        f.close()
        title = re.findall(title_pattern, contents)
        date = re.findall(date_pattern, contents)
#        categories = re.findall(cat_pattern, contents)
        authors = re.findall(auth_pattern, contents)
        alt_authors = re.findall(alt_auth_pattern, contents)
        pdf_location = re.findall(pdf_pattern, contents)
        print(len(pdf_location))
        if len(pdf_location) == 0:
            pdf_location = ["no pdf found"]
        articles.append({"URL":article, "Title":title[0], "Date":date[0], "Authors":authors, "More Authors":alt_authors, "PDF Location":pdf_location})
    return articles



print(get_article_list(article_list))
items = get_article_list(article_list)

filename = "scrapedCurrentsData.json"
with open(filename, 'w') as f:
    json.dump(items, f)

uploader = "currents_to_add.csv"
field_names=["Date", "Title", "Authors", "More Authors", "URL", "PDF Location"]

with open(uploader, 'w') as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(items)
