from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
from webkit_server import InvalidResponseError
from bs4 import BeautifulSoup
import dryscrape
import os
import requests
import urllib2
import subprocess

siteList = []

#Open webpage for domain name scraping
def createSession(crawlingWebsite):
    dryscrape.start_xvfb()
    #Begin new session with loaded scripts
    try:
    	session = dryscrape.Session()
    	session.visit(crawlingWebsite)
    	response = session.body()
    	#Reset session for handling memory issues
    	session.reset()
    except InvalidResponseError as e:
	print 'InvalidResponseError:', ed
    soup = BeautifulSoup(response, "html.parser")
    #Searches for hyperrefs in a page. This is the hardcoded bit.
    #Searching for items is webpage-specific. For a different website, please refer to its HTML content
    #to find out which tags are needed to obtain a list of domains if any.
    tableFound = soup.findAll("a", {"target": "_blank"})

    if tableFound == None:
        print "Nothing found. Terminating crawler."
	quit()
    else:
        for row in tableFound:
            #Add found domains to the list of sites
            siteList.append(row.get('href'))
		
#Check every domain for HTTPS Support
def checkHTTPS():
    #Selenium opens the web browser by default
    #I have made the display invisible to save time and memory efficiency.
    display = Display(visible = 0, size = (800, 600))
    display.start()
    httpsSiteList = []
    httpSiteList = []
    os.environ['geckodriver'] = "/home/osboxes/Downloads"

    for website in siteList:
        print website
	#Change path depending on the location of your geckodriver
        driver = webdriver.Firefox("/home/osboxes/Downloads/")
        driver.get("http://www.sslshopper.com/ssl-checker.html?hostname=" + website)

        delay = 40
        try:
	    #Wait for 40 seconds before returning any results.
	    #This makes sure that whole page will be loaded before scraping.
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'failed')))
            print website + " does NOT support HTTPS!"
            driver.quit() #Close browser
            display.stop() #Close
	    httpSiteList.append(website)
        except TimeoutException:
            print website + " supports HTTPS!"
	    driver.quit() #Close browser
            display.stop() #Close
	    httpsSiteList.append(website)
	    checkAtlas(website)
        except NoSuchElementException:
            print "Such element does not exist!"
	    driver.quit() #Close browser
            display.stop() #Close
	    httpsSiteList.append(website)
	    checkAtlas(website)

    print "Sites supporting HTTPS: " + str(len(httpsSiteList))
    for ssite in httpsSiteList:
        print ssite
    print "\n"
    print "Sites NOT supporting HTTPS: " + str(len(httpSiteList))
    for nsite in httpSiteList:
        print nsite

#Check if site is present in the atlas and create ruleset
def checkAtlas(wSite):
    #print httpsList
    shortListedSites = []
    #for wSite in httpsList:
    hyperLinks = []
    try:
        print wSite.lower()
	siteChunks = wSite.lower().split(".")
	for bits in siteChunks:
	   print bits
	if "http://www" in siteChunks[0] or "https://www" in siteChunks[0] or "www" in siteChunks[0]:
	   del siteChunks[0]
	   print siteChunks[0]
	print siteChunks[0][0].lower()
        r = requests.get("http://www.eff.org/https-everywhere/atlas/letters/" + siteChunks[0][0].lower() + ".html")
        print "Request accepted"
        resp = urllib2.urlopen(r.url)
        print "URL Opened"
        print r.url
        soup = BeautifulSoup(resp.read(), "html.parser")
        print "Website scraped"
        domainList = soup.findAll('ul', id='domain-list')
        for link in domainList:
	        #hyperLinks = []
            for site in link.findAll('li'):
                hyperLinks.append(site.text)
        print len(hyperLinks)
        for atlasSite in hyperLinks:
            if siteChunks[0].lower() == atlasSite.split(".")[0]:
                print siteChunks[0].lower() + " is in the atlas.\n"
                break
            else:
	        if atlasSite == hyperLinks[-1]:
		   print siteChunks[0].lower() + " is NOT in the atlas. \n"
		   ruleSite = ".".join(str(x) for x in siteChunks
		   print ruleSite
		   print ruleSite.split('/')[0]
                   #shortListedSites.append(".".join(str(x) for x in siteChunks))
    		   #subprocess.call(["bash make-trivial-rule " + ruleSite.split('/')[0]], shell = True, cwd = "/home/osboxes/Documents/https-everywhere/rules")
		   break
		continue

    except IOError, e:
        if hasattr(e, 'code'): # HTTPError
            print "Error loading website " + r.url
            print "HTTP error code: " + str(e.code) + " - " + str(e.reason) + "."
            pass
        elif hasattr(e, 'reason'): # URLError
            print "Cannot connect, reason: " + str(e.reason) + "\n"
            pass
        else:
            pass
    except ValueError, ex:
        print "Value error\n"
    except:
        print "Unexpected error.\n"
        pass

#Hardcoded - need to specify in the function call which site you would like to crawl
createSession("http://www.appfreak.net/list-of-100-mobile-game-review-sites/")
print siteList
checkHTTPS()
