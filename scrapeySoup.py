""" This project is based on using a html parser to scrape data from SSRN profiles.
One way is to us a html parser (Beautiful Soup in this example).
Another way is regular expressions and brute force - which proved too difficult.
"""
# import necessary packages
from bs4 import BeautifulSoup as soup
#from urllib import request
from urllib.request import Request, urlopen
import requests
import re
import json
import csv



# This is the beautiful soup method

def getSSRN(author):
    url =  "https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=" + author
    request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    f = urlopen(request_site)
    soup_page_html = str(f.read())
    f.close

    page_soup = soup(soup_page_html, 'html.parser')

    results = page_soup.find(id="scholarly-papers")

    articles = results.find_all("div", id=re.compile('div_\d+'))
    abstracts = results.find_all("div", class_="abstract-row")

    incoming_ssrn = []

    for i, article in enumerate(articles):
        print(i)
        article_link = article.find("a", {"class":"title"})
        article_URL = article_link["href"]
        article_title = article_link.find("span")
        article_citation = article.find("div", class_="reference")
        article_notes = article.find("div", class_="note-list")
        article_numPages = article_notes.find("span", string=re.compile('Number'))
        article_postDate = article_notes.find("span", string=re.compile('Posted'))
        article_revisedDate = article_notes.find("span", string=re.compile('Revised'))
        article_authors = article.find("div", class_="authors-list")
        article_affiliations = article.find("div", class_="afiliations")
        downloads = article.find("div", class_="downloads")
        article_downloads = downloads.find('span', string=re.compile('(\d+)'))
        article_rank = downloads.find('span', string=re.compile("\("))
        article_citations = article.find("a", onclick=re.compile('goToCitation'))
        article_keywords = abstracts[i].find("p", id=re.compile('keywords'))

        print("New Article")
        ssrn_abstract_url = article_URL
        print(f'Abstract URL: {ssrn_abstract_url}')
        article_id = article_URL.split('=')[1]
        print(f'Article ID: {article_id}')
        article_title = article_title.text
        print(f'Title: {article_title}')
        if article_citation:
            article_citation = article_citation.text.strip('\\r,\\n,\\t')
            print(f'Citation(s): {article_citation}')
                    
        if article_numPages:
            article_numPages = article_numPages.text
            match_numPages = re.match(r'Number of pages: (\d+)',article_numPages)
            article_numPages = match_numPages[1]
            print(f'Number of Pages: {article_numPages}')
        if article_postDate:
            article_postDate = article_postDate.text
            print(f'Date Posted: {article_postDate}')
            match_postDate = re.match(r'Posted:\s(\d{1,2})\s(\w+)\s(\d{4})',article_postDate)
            formatted_postDate = match_postDate.group(3)+'-'+match_postDate.group(2)+'-'+match_postDate.group(1)
            print(formatted_postDate)
        
        if article_revisedDate:
            revision_date = article_revisedDate.text
            print("Date Revised: " + revision_date)
            match_revisionDate = re.match(r'Last Revised:\s(\d{1,2})\s(\w+)\s(\d{4})',revision_date)
            formatted_revisionDate = match_revisionDate.group(3)+'-'+match_revisionDate.group(2)+'-'+match_revisionDate.group(1)
        else:
            formatted_revisionDate = 'None'
        authlist = article_authors.text.strip('\\r,\\n\\t')
        authlist = authlist.replace(" and ", "|")
        autharray = authlist.split("|")
        affList = article_affiliations.text.strip('\\r,\\n,\\t')
        affList = affList.replace(" and ", "|")
        affarray = affList.split("|")
        auth_affil = {}
        for key in autharray:
            for value in affarray:
                auth_affil[key] = value
                affarray.remove(value)
        print('Author(s):')
        for key in auth_affil:
            print(f'{key}, Affiliation: {auth_affil[key]}')
        if article_downloads:
            ssrn_downloads = article_downloads.text.strip()
            print(f'SSRN Downloads: {ssrn_downloads}')
        else:
            ssrn_downloads = 'none'
        if article_rank:
            ssrn_article_rank = article_rank.text.strip('\(,\)')
            print(f'SSRN Article Rank: {ssrn_article_rank}')
        else:
            ssrn_article_rank = 'none'
        if article_citations:
            ssrn_citations = article_citations.text.strip()
            print(f'SSRN Citations to this article: {ssrn_citations}')
        else:
            ssrn_citations = 'none'
        if article_keywords:
            article_keywords = article_keywords.text
            print(f'Keywords: {article_keywords}')

        incoming_ssrn.append({"SSRN Abstract URL":ssrn_abstract_url, "SSRN Article id":article_id, "Article Title":article_title, "Article Citation":article_citation, "Number of pages":article_numPages, "Posted date": formatted_postDate, "Last Revised":formatted_revisionDate, "Authors":auth_affil, "SSRN Downloads":ssrn_downloads, "SSRN Article Rank":ssrn_article_rank, "SSRN Citations":ssrn_citations, "Keywords":article_keywords})

    return incoming_ssrn
