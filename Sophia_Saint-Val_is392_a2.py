# Sophia Saint-Val
# IS 392-002
# Assignment 02

from bs4 import BeautifulSoup
from urllib.request import urlopen
from queue import *
import re
import ssl
import os

queue = Queue()
visitedUrlList = [] # prevent a single URL from entering the queue repeatedly
global pageCounter
savedUrlList = []
pageContent = ""
seedUrls = ["https://en.wikipedia.org/wiki/Global_warming", "https://en.wikipedia.org/wiki/Climate_change"] # populate list with URLs
relatedTerms = ["climate change", "climate", "global warming", "pollution", "ozone layer", "greenhouse gases", "climatology", "meteorology", "atmosphere", "weather"] # populate list with related terms

# get page content
def get_page_content(url):
    try:
        html_response_text = urlopen(url).read()
        page_content = html_response_text.decode('utf-8')
        return page_content
    except Exception as e:
        return None

# extract title of a page and clean it
def clean_title(title):
    invalid_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for c in invalid_characters:
        title = title.replace(c, '')
    return title

#extract outgoing(inner) URLs from page content
def get_urls(soup):
    links = soup.find_all('a')
    urls=[]
    for link in links:
        urls.append(link.get('href'))
    return urls

#check if URL is valid
def is_url_valid(url):
    if url is None:
        return False
    if re.search('#', url):
        return False
    match = re.search('^/wiki/', url)
    if match:
        return True
    else:
        return False

# reformat URL / change relative URL into full URL
def reformat_url(url):
    match=re.search('^/wiki/', url)
    if match:
        return "https://en.wikipedia.org" + url
    else:
        return url

# save a page
def save(text, path):
    f = open(path, 'w', encoding = 'utf-8', errors = 'ignore')
    f.write(text)
    f.close()

# focused crawler function  
def crawler(seedUrls, relatedTerms):
    # set up SSL Environment
    try:
            _create_unverified_https_contect = ssl.create_unverified_context
    except AttributeError:
            pass
    else:
            ssl._create_default_https:_context = _create_unverified_https_context
            
    for url in seedUrls:
        if is_url_valid(url) == False:
                reformat_url(url)
        queue.put(url)
        visitedUrlList.append(url)
    while queue.qsize() > 0:
        i = 0
        pageCounter = 0
        currentUrl = queue.get() # get the URL in the front of the queue and remove it
        pageContent = get_page_content(currentUrl) # get the content of the webpage via HTTP
        if pageContent is None:
            continue
        termCounter = 0
        soup = BeautifulSoup(pageContent, 'html.parser') # parse page content using BeautifulSoup
        page_text = soup.get_text()  # extract main text of a page
        for term in relatedTerms:
            if re.search(term, page_text, re.I): #check if term is included in page text
                termCounter = termCounter + 1
                if termCounter >= 2: # if a page is topical / relevant
                    title = soup.title.string
                    title = clean_title(title)
                    path = "savedPages\\" + title
                    #save(title, path)
                    save(str(soup), path)
                    savedUrlList.append(currentUrl)
                    pageCounter = pageCounter + 1
                    print("page #" + str(pageCounter) + ": " + currentUrl) # print information
                    break
        i = i + 1
        if pageCounter >= 500:
            break
        outGoingUrls = get_urls(soup)
        for outGoingUrl in outGoingUrls:
            if reformat_url(currentUrl) and outGoingUrl not in visitedUrlList:
                queue.put(outGoingUrl)
                visitedUrlList.append(outGoingUrl)
        # save crawled URLs
        f = open('crawled_urls.txt', 'w')
        i = 1
        for url in savedUrlList:
            f.write(str(i) + ': ' + url + '\n')
            i += 1
        f.close()
            
crawler(seedUrls, relatedTerms)
