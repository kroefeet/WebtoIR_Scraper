""" This project is based on using a html parser to scrape data from SSRN profiles.
One way is to us a html parser (Beautiful Soup in this example).
Another way is regular expressions and brute force - which proved too difficult.
"""
# import necessary packages
#from bs4 import BeautifulSoup as soup
#from urllib.request import Request, urlopen
#import requests
#import re
import json
import csv
from scrapeySoup import getSSRN
import time


author_soup = []

with open('SSRNidList.csv', mode = 'r') as SSRNids:
    SSRNlist = csv.DictReader(SSRNids)

    for item in SSRNlist:
        for key,value in item.items():
            if key == 'SSRNidValue':
                author_soup.append(value)

print(author_soup)

ssrn_final = []
for author in author_soup:
    incoming_ssrn = getSSRN(author)
    print(f'incoming_ssrn is the type: {type(incoming_ssrn)}')
    ssrn_final.extend(incoming_ssrn)
    
    print('-------------------------')
    time.sleep(5)

print(ssrn_final)
# Append the results to a JSON file
filename = "SSRNData.json"
with open(filename, 'a') as f:
    json.dump(ssrn_final, f)


# Append results into a CSV file with headers for IR upload
updater = "ssrn_data.csv"
field_names=["SSRN Abstract URL", "SSRN Article id", "Article Title", "Article Citation", "Number of pages", "Posted date", "Last Revised", "Authors", "SSRN Downloads", "SSRN Article Rank", "SSRN Citations", "Keywords"]

with open(updater, 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(ssrn_final)
    
