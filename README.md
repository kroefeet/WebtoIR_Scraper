# Scrapey
A Python-based process for scraping publication information and comparing the results to a previously downloaded set

## Steps for using these scripts

### Start with a spreadsheet like the SSRNidList.csv
This spreadsheet can have as much or as little information as possible but must have a column called SSRNidValue in order for this process to work
- Note that each cell should only have the SSRN ID and not the URL

### Run python3 mainScrapeySoup.py
This will create a list object of all IDs in your spreadsheet and create a list of publications for each ID.

The results will create 2 files:
1. SSRNData.json
- You should save a copy of this as 'previousSSRNData.json' for the next part of the process

2. ssrn_data.csv
- This is a more human readable version of all of the data that was collected. You can use this to verify that you have captured what has posted.

### Time passes (as it always does)
You should now run python3 mainScrapeySoup.py again.
At this point you should have two JSON files in your directory:
1. SSRNData.json (newly generated)
2. previousSSRNData.json (generated the last time you ran this process)

Now run python3 check_ssrn.py

This will match publication ids with the last revision date. If this combination matches in the two JSON files, nothing happens. If there is a identifier + revision date combination that exists on the most recent JSON file (SSRNData.json) but not on previousSSRNData.json, then it will be added to a file called 'review_new_SSRN.csv'

This file (review_new_SSRN.csv) should contain items that have either changed or are new since the last time you ran this process.