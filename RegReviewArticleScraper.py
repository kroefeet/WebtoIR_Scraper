# A web scraper using BeautifulSoup to capture blog post data from https://www.theregreview.org
# This program captures all relevant metadata for each post and dumps it into an Excel sheet for Digital Commons batch uploading
# Also uses the OS module to run wkHTMLtoPDF for each article to capture a clean PDF of each article

import requests
import time
from openpyxl import Workbook
from bs4 import BeautifulSoup

def getArticleMeta(url):
    #Takes an article URL as input and returns a dictionary of the metadata

    article_meta = {}

    article_URL=url
    article_meta["url"] = article_URL
    #The article URL is the first returned field
    agent = {"User-Agent":"Mozilla/5.0"}
    
    #Sometimes the article request doesn't complete or times out, the following code gives each URL three chances
    for i in range(3):
        try:
            page = requests.get(article_URL, headers=agent)
        except requests.exceptions.RequestException as e:
            print("Error loading page: " + article_URL + ", retrying")
            time.sleep(3) # wait 3 seconds before retrying after an exception
            continue
        else:
            break
    else:
        print("Couldn't make this one work, trying next URL")
        article_meta = {'url': article_URL, 'id': '?', 'posttype': '?', 'category': '?', 'date': '?', 'title': '?', 'authors': '?', 'img_src': '?', 'excerpt': '?', 'full_text': '?', 'links': '?', 'author_bios': '?', 'author_urls': '?', 'tags': '?'}
        return(article_meta)
        #If the URL doesn't work after three tries, end this process and return an incomplete result

    soup = BeautifulSoup(page.content, "html.parser") 
    #Run the BS4 HTML parser on the page

    results = soup.find(id="page_content")
    #"results" is just the part of the HTML we are trying to scrape, on each article we only need the div called "page_content"

    article_meta["id"] = results.find("article")["id"][5:] #Pulls the numeric article id (useful as a short unique identifier)
    
    #This part is a bit messy.  RegReview articles all have a post "type" and zero to many "categories"
    #I would like to store the post types and categories in separate fields, but I haven't been able to
    #find a way to programmatically distinguish between them.  So I just created lists of all possible types
    #and categories, and I'm comparing every term that appears in this field against those lists to figure out
    #where they need to go.
    article_type = ""
    article_category = ""
    atypes = ["News", "Analysis", "Synopsis", "Opinion", "Series", "PPR", "PPR News", "Books", "Saturday Seminar", "Week in Review", "Year in Review"]
    acats = ["Business", "Education", "Environment", "Health", "Infrastructure", "International", "Process", "Regulatory Recap", "Rights", "Technology"]
    entry_cats = results.find("span", class_="entry-category").findAll("a") #Find every link in the "entry-category" section
    for entry in entry_cats:
        if entry.text in atypes and entry.text not in article_type: #Checks each term against the list, and checks for duplicates
            article_type += entry.text + ","
        if entry.text in acats and entry.text not in article_category:
            article_category += entry.text + ","

    article_meta["posttype"] = article_type[:-1] #stores the string of post types, cutting off the last trailing comma

    article_meta["category"] = article_category[:-1] #stores the string of post categories, cutting off the last trailing comma

    article_meta["date"] = results.find("span", class_="entry-date").text[3:] #pulls the posted date of the article

    article_meta["title"] = results.find("h1").text #pulls the article title

    #Articles can have multiple authors, this code pulls each author name and separates them with a pipe delimiter in a single string
    article_authors = ""
    authors = results.find("h3", class_="article-author").find_all("a")
    for author in authors:
        article_authors += author.text + "|"
    article_meta["authors"] = article_authors[:-1] #remove the final trailing pipe delimiter

    #This code pulls the url for the image in each article.  Not sure I need this, but for now I'm pulling
    #Everything that could have any use
    image_area = results.find("div", class_="post_img")
    image_src = image_area.find("img")['src']
    article_meta["img_src"] = image_src

    #Pulls the article excerpt
    post_excerpt = results.find("div", class_="post_excerpt").find("p")
    article_meta["excerpt"] = post_excerpt.text

    #Another section I may or may not need.  This code does two things:
    #- Go through the text of the article and combines every paragraph into a single string separated by newlines
    #- Find any links in the article body, and store all the URLs in a single string separated by pipe delimiters
    #The links could be useful to keep a list of references handy for data projects, but I don't think they would have any use in the IR
    post_body = ""
    post_links = ""
    post_body_area = results.find("div", class_="entry_content").find_all("p", recursive=False)
    for paragraph in post_body_area:
        post_body += paragraph.text + "\n "
        if(paragraph.find("a") != None):
            body_links = paragraph.find_all("a")
            for link in body_links:
                post_links += link["href"] + "|"
    article_meta["full_text"] = post_body.replace(u'\xa0', u' ') #This removes some weird unicode stuff, I think there's a more modern way to do this in Python
    article_meta["links"] = post_links[:-1] #Remove the trailing pipe delimiter from the links list

    #MOST of the time, there is a box at the bottom of the article with short bios of each author
    #These bios are not pulled from a central database, I think they are custom written for each article,
    #which means they reflect the author's institution and status at the time of posting.  Most
    #of these bios also have a URL linking to the author's primary affiliation.  I might be able to extract a domain from
    #these URLs to get some data on the organizations we've collaborated with over the 10+ years of the website.
    author_bios = ""
    author_urls = ""
    authors = results.find_all("div", class_="author-description")
    for author in authors:
        if author.find("p") != None: #Need to check to make sure this section of the page exists, otherwise it throws an error
            author_bios += author.find("p").text.replace(u'\xa0', u' ') + "|"
        if author.find("a") != None:
            author_urls += author.find("a")["href"] + "|"
    article_meta["author_bios"] = author_bios[:-1]
    article_meta["author_urls"] = author_urls[:-1]

    #Most articles have a list of linked tags, this pulls the tag text into a single string separated by pipe delimiters
    article_tags = ""
    post_tags = results.find("div", class_="post_tags").find_all("a")
    for tag in post_tags:
        article_tags += tag.text + "|"
    article_meta["tags"] = article_tags[:-1]

    #The code below calls the wkhtmltopdf command line app on each URL to create a PDF of each article, and names it according to the article_id
    #The PDF conversion takes a while, so I generally turn it off while I've been testing.  This doesn't really need to be part of the metadata
    #collection process, down the line I may separate this into a different program that just goes through a list of URLs and article ids
    system_string = "wkhtmltopdf " + article_URL + " ~/Documents/RegReview/" + article_meta["id"] + ".pdf"
    #os.system(system_string)

    return(article_meta) #return the dictionary of all metadata fields


#Since there are over 3000 articles, I had some issues letting the program run over the entire site, since errors meant that none of the data was saved
#RegReview has a great "archive" page that lists all articles in chronological order, twelve articles per page, currently 300+ pages
#This version of the code breaks up the archive into blocks of 50 pages, each block gets saved to a separate excel file, I can combine these later
#Ideally this routine would read in the total number of pages first and then dynamically adjust based on that, but I'm not there yet.
def main():
    fieldnames = ['url', 'id', 'posttype', 'category', 'date', 'title', 'authors', 'img_src', 'excerpt', 'full_text', 'links', 'author_bios', 'author_urls', 'tags']
    #Sets up the column headers for the Excel sheet
    xlpage = 1
    for j in range(1, 7): #create a separate excel sheet for each block of 50 archive pages
        metafile = Workbook() #Workbook is a function from the Excel library openpyxl
        dest_filename = "RegReviewMeta" + str(xlpage) + ".xlsx" #generate the filename for each workbook
        print("Writing to file: " + dest_filename)
        ws1 = metafile.active #indicates the active worksheet in the file
        ws1.append(fieldnames) #add the column headers to the worksheet

        for i in range((50 * (xlpage - 1) + 1), ((50 * xlpage) + 1)):
            print("Scraping page: " + str(i)) #console output, helps to figure out what pages are causing errors
            index_URL = "https://www.theregreview.org/archive/page/" + str(i)
            agent = {"User-Agent":"Mozilla/5.0"}
            page = requests.get(index_URL, headers=agent) #use requests to visit each page in the archive
            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find(id="body_content")

            entries = results.find_all("div", class_="post_img") #the "post_img" div is the best way to find the URL for each article on the archive pages
            currArticle = 1
            for entry in entries:
                print("Scraping article:" + str(currArticle)) #more error-checking console output
                entry_url = entry.find("a")["href"] #find the article URL
                metadata = getArticleMeta(entry_url) #call the top function on the url to get the metadata
                values = (metadata[k] for k in fieldnames) #pull the metadata fields from the article into a list
                ws1.append(values) #add the article fields to the next row of the Excel sheet
                metadata={} #clear the variable
                currArticle += 1

        metafile.save(filename = dest_filename) #save the file
        xlpage += 1

if __name__ == '__main__':
    main()