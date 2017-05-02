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
shortListedSites = []

#Open webpage for domain name scraping
def createSession(crawlingWebsite):
    print "\nCrawler Initiated. Searching in '" + crawlingWebsite + "' for domains.\n\n"
    dryscrape.start_xvfb()
    #Begin new session with loaded scripts
    try:
    	session = dryscrape.Session()
    	session.visit(crawlingWebsite)
    	response = session.body()
    	#Reset session for handling memory issues
    	session.reset()
    except InvalidResponseError as e:
	print "Cannot open " + crawlingWebsite + "\n"
	print 'InvalidResponseError:', e
	quit()
    soup = BeautifulSoup(response, "html.parser")
    #Searches for hyperrefs in a page. This is the hardcoded bit.
    #Searching for items is webpage-specific. For a different website, please refer to its HTML content
    #to find out which tags are needed to obtain a list of domains if any.
    tableFound = soup.findAll("a", {"target": "_blank"})

    if len(tableFound) == 0:
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
	    print "Moving on to the next website.\n\n"
            driver.quit() #Close browser
            display.stop() #Close display
        except TimeoutException, NoSuchElementException:
            print website + " supports HTTPS!"
	    driver.quit()
            display.stop()
	    httpsSiteList.append(website)
	    checkAtlas(website)

#Check if site is present in the atlas and create ruleset
def checkAtlas(wSite):
    hyperLinks = []
    try:
	siteChunks = wSite.lower().split(".")
        if "www" in siteChunks[0]:
           del siteChunks[0]
	elif "http://" in siteChunks[0] or "https://" in siteChunks[0]:
	   siteChunks[0] = siteChunks[0].split('/')[2]
        r = requests.get("http://www.eff.org/https-everywhere/atlas/letters/" + siteChunks[0][0].lower() + ".html")
        resp = urllib2.urlopen(r.url)
        soup = BeautifulSoup(resp.read(), "html.parser")

        domainList = soup.findAll('ul', id='domain-list')
	#Loop through all domains starting with the first letter of the
	#website currently being checked
        for link in domainList:
            for site in link.findAll('li'):
                hyperLinks.append(site.text)
        for atlasSite in hyperLinks:
            if siteChunks[0].lower() == atlasSite.split(".")[0]:
                print siteChunks[0].lower() + " is in the atlas and already has a ruleset.\n\n"
                break
            else:
	        if atlasSite == hyperLinks[-1]:
		   print siteChunks[0].lower() + " is NOT in the atlas. Creating ruleset..."
		   ruleSite = ".".join(str(x) for x in siteChunks)
		   #Create ruleset for the website
    		   ruleOutput = subprocess.call(["bash make-trivial-rule " + ruleSite.split('/')[0]], shell = True, cwd = "/home/osboxes/Documents/https-everywhere/rules")
		   if (ruleOutput == 0):
		      print "Successfully created a ruleset for '" + ruleSite + "'!\n\n"
		      shortListedSites.append(ruleSite)
		   else:
		      print "Oops! '" + ruleSite + "' seems to already have a ruleset in your repository. Please examine it!\n\n"
		   break
		continue
    #Catch some exceptions
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
print "Sites found: " + str(len(siteList)) + "\n"
for foundSite in siteList:
    print foundSite
print "\n\n"
checkHTTPS()
print "The crawler successfully created rulesets for " + str(len(shortListedSites)) +" websites:\n"
for shortSite in shortListedSites:
	print shortSite
