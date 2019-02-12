# Sophia Saint-Val
# IS 392-002
# Assignment 02

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import ssl
import os

queue = []
visitedUrlList = [] # prevent a single URL from entering the queue repeatedly
pageCounter = 0
savedUrlList = []
pageContent = ""
seedUrls = ["https://en.wikipedia.org/wiki/Climate_change","https://en.wikipedia.org/wiki/Global_warming"] # populate list with URLs
relatedTerms = ["climate change", "climate", "global warming", "pollution", "ozone layer", "greenhouse gases", "climatology", "meteorology", "atmosphere", "weather"] # populate list with related terms

# set up SSL Environment
try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context

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
    for url in seedUrls:
        is_url_valid(url)
        queue.append(url)
        visitedUrlList.append(url)
    while len(queue) > 0:
        queue.pop(0) # get the URL in the front of the queue and remove it
        pageContent = get_page_content(url) # get the content of the webpage via HTTP
        if pageContent is None:
            continue
        termCounter = 0
        soup = BeautifulSoup(pageContent, 'html.parser') # parse page content using BeautifulSoup
        page_text = soup.get_text()  # extract main text of a page
        for term in relatedTerms:
            if re.search(term, page_text, re.I): #check if term is included in page text
                termCounter += 1
                if termCounter >= 2: # if a page is topical / relevant
                    title = soup.title.string
                    title = clean_title(title)
                    save(title, pageContent)
                    savedUrlList.append(url)
                    pageCounter += 1
                    print("page #" + termCounter + ": " + url) # print information
                    break
        if pageCounter >= 500:
            break
        outGoingUrls = get_urls(pageContent)
        for outGoingUrl in outGoingUrls:
            if reformat_url(url) and outGoingUrl not in visitedUrlList:
                queue.append(outGoingUrl)
                visitedUrlList.append(outGoingUrl)
    # save crawled URLs
    #crawled_urls = open('crawled_urls.txt', 'w')
    #i = 1
    #for url in crawled_urls:
            #crawled_urls.write(str(i) + ': ' + url + '\n')
            #i += 1
    #crawled_urls.close()
            
crawler(seedUrls, relatedTerms)
