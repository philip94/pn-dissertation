from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
import dryscrape
import os
import requests
import urllib2
import subprocess

siteList = []

def createSession(crawlingWebsite):
    dryscrape.start_xvfb()
    session = dryscrape.Session()
    session.visit(crawlingWebsite)
#site = session.at_xpath("//input[@name='host']")
#site.set(websiteName)
    response = session.body()
#for link in session.xpath('//table'):
#    print link['table']
#print response
#response = session.body()
    session.reset()
#session.wait_for_safe(lambda: session.at_xpath("//table"))
    soup = BeautifulSoup(response, "html.parser")
#print response
    #tableFound = soup.findAll("span", {"class": "listItem__properties black default"})
    tableFound = soup.findAll("a", {"target": "_blank"})
#print tableFound
#print tableFound.findAll('tr')
    if tableFound == None:
        print "Nothing found. Terminating crawler."
	quit()
    else:
        for row in tableFound:
            #if len(row.get('href') != 0:
            siteList.append(row.get('href'))

def checkHTTPS():
    display = Display(visible = 0, size = (800, 600))
    display.start()
    httpsSiteList = []
    httpSiteList = []
    os.environ['geckodriver'] = "/home/osboxes/Downloads"
#driver = webdriver.Firefox("/home/osboxes/Downloads/")

    for website in siteList:
        print website
        driver = webdriver.Firefox("/home/osboxes/Downloads/")
        driver.get("http://www.sslshopper.com/ssl-checker.html?hostname=" + website)
#os.environ['geckodriver'] = "/home/osboxes/Downloads"
        delay = 40
        try:
   # table = driver.find_element_by_class_name('checker_messages')
    #specTable = table.get_attribute("class")
   # print specTable
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'failed')))
            print website + " does NOT support HTTPS!"
	    httpSiteList.append(website)
        except TimeoutException:
            print website + " supports HTTPS!"
	    httpsSiteList.append(website)
	    checkAtlas(website)
        except NoSuchElementException:
            print "Such element does not exist!"
	    httpsSiteList.append(website)
	    checkAtlas(website)
        driver.quit()
        display.stop()
   # break
#assert "Python" in driver.title
#elem = driver.find_element_by_name("q")
#elem.clear()
#elem.send_keys("pycon")
#elem.send_keys(Keys.RETURN)
#assert "No results found." not in driver.page_source
#driver.quit()
#display.stop()

    print "Sites supporting HTTPS: " + str(len(httpsSiteList))
    for ssite in httpsSiteList:
        print ssite
    print "\n"
    print "Sites NOT supporting HTTPS: " + str(len(httpSiteList))
    for nsite in httpSiteList:
        print nsite
    get_links("http://", httpsSiteList)

def checkAtlas(wSite):
    #print httpsList
    shortListedSites = []
    #for wSite in httpsList:
    hyperLinks = []
    try:
            #request = urllib2.Request(securityString + "www.eff.org/https-everywhere/atlas/letters/e.html")
            #print "Request sent"
        print wSite.lower()
	siteChunks = wSite.lower().split(".")
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
                   shortListedSites.append(".".join(str(x) for x in siteChunks))
		   for shortSite in shortListedSites:
	               print shortSite
    		       subprocess.call(["bash make-trivial-rule " + shortSite.split('/')[0]], shell = True, cwd = "/home/osboxes/Documents/https-everywhere/rules")
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
                        #get_links(http_string)
        else:
            pass
    except ValueError, ex:
        print "Value error\n"
    except:
        print "Unexpected error.\n"
        pass
    #print "Shortlisted sites: " + str(len(shortListedSites))
   # for shortSite in shortListedSites:
#	print shortSite
 #   subprocess.call(["bash make-trivial-rule " + shortSite.split('/')[0]], shell = True, cwd = "/home/osboxes/Documents/https-everywhere/rules")

#createSession("http://www.ranker.com/list/best-gaming-blogs-and-websites/blog-loblaw")
createSession("http://www.appfreak.net/list-of-100-mobile-game-review-sites/")
print siteList
checkHTTPS()
#get_links("http://", httpsSiteList)
