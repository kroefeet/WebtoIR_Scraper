"""This script is intended to check against the most recently updated SSRN scrape to see if any items have been updated"""

import json
import csv

filename = 'SSRNData.json'
existing = 'previousSSRNData.json'

with open(filename) as f:
            incoming = json.load(f)
            #print(incoming)

with open(existing) as e:
            existing = json.load(e)
            #print(existing)

new_items = []
existing_items = []

for item in existing:
    #create a comparison identifier for records based on id and last revised date
    existing_items.append(item['SSRN Article id']+item['Last Revised'])

print(existing_items)

for item in incoming:
    compare_id = item['SSRN Article id']+item['Last Revised']
    if compare_id not in existing_items and item not in new_items:
        new_items.append(item)


print(new_items)

updater = "review_new_SSRN.csv"
field_names=["SSRN Abstract URL", "SSRN Article id", "Article Title", "Article Citation", "Number of pages", "Posted date", "Last Revised", "Authors", "SSRN Downloads", "SSRN Article Rank", "SSRN Citations", "Keywords"]

with open(updater, 'w') as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(new_items)
