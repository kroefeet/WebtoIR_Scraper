# First get a list of URLs to crawl this will serve as a comparison point for future crawls

import urllib.request
import requests
import re
import json
import csv

# grab the contents from the base page
def get_url_list(url):
# now grab a list of the sub pages that have the content I want
# it should match https://www.ecologylawquarterly.org/currents/?yr=[year]
    archive_pattern = re.compile(r'https:\/\/www\.ecologylawquarterly\.org\/currents\/\?yr=\d{4}', re.I)

    f = urllib.request.urlopen(url)
    contents = str(f.read())
    f.close()
    result = re.findall(archive_pattern, contents)
    return result


# for each yr, there is the idea of pages until it runs out in the form
# https://www.ecologylawquarterly.org/currents/?yr=[year]&pg=[optional to some number]
def get_url_subpages(urls_list):
    subpage_pattern = re.compile(r'\?yr=\d{4}(\&pg=\d*)', re.I)
    list_of_urls = []
    for page_url in urls_list:
         list_of_urls.append(page_url)
         print(page_url)
         f = urllib.request.urlopen(page_url)
         contents = str(f.read())
         f.close()
         result = re.findall(subpage_pattern, contents)
         if result:
             for item in result:
                 list_of_urls.append(page_url+item)

    return list_of_urls

def get_article_urls(list_of_subpages):
    article_pattern = re.compile(r'<a[^>]*href=\s?\"([^"]+)"\s?class="tit"[^>]*>', re.I)
    #regex magic provided by: https://www.rapiddg.com/article/regex-corner-extract-image-tags-html
    list_of_articles = []
    for subpage in list_of_subpages:
        print(subpage)
        f = urllib.request.urlopen(subpage)
        contents = str(f.read())
        f.close()
        result = re.findall(article_pattern, contents)
        for item in result:
            print(item)
            list_of_articles.append(item)

    return list_of_articles

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



webpage = input("What is the URL for the list of publications to scrape? ")
url_list = get_url_list(webpage)
print(f'This is the output from get_url_list {url_list}')
all_urls = get_url_subpages(url_list)
print(f'This is the output from get_url_subpages {all_urls}')
all_article_urls = get_article_urls(all_urls)
print(f'This is the ouput from get_article_urls {all_article_urls}')
all_article_titles = get_article_list(all_article_urls)
print(f'This is the output from get_article_list {all_article_titles}')

filename = "scrapedCurrentsData.json"
with open(filename, 'w') as f:
    json.dump(all_article_titles, f)

uploader = "currents_to_add.csv"
field_names=["Date", "Title", "Authors", "More Authors", "URL", "PDF Location"]

with open(uploader, 'w') as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(all_article_titles)
