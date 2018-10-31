from bs4 import BeautifulSoup as bs
from urllib.request import urlretrieve
import os
import requests
import urllib.request
import urllib.error
import wget
import json
import shutil
import time

from urllib.parse import urlparse
#- TODO:
#- Multithreading
#- Download while gathering links (dynamic)
#- keep links saved for later/resume&resume job
#- optimise
#- split the param option domain into two links, one link will be domain to download from, and second link will be the domain to click on
#-      because right now it clicks on the links within domain, no matter if they are within the domain and gathers links from there as well
#-      this extra layer will help restrict opening sites not within the specified domain, which can be left blank.

class WebFileExtractor():
    def __init__(self):
        pass

    def getRootUrl(self,url):
        #- this function returns the netloc
        #- if path is true, also returns path
        parsedUrl = urlparse(url)
        return(parsedUrl.scheme + "://" + parsedUrl.netloc)

    def constructLink(self,pageUrl, link):
        #reconstructs the link to absolute path
        parsedPageUrl = urlparse(pageUrl)
        parsedUrl = urlparse(link)
        tempPageUrl = pageUrl
        tempLink = link

        #checks to see if link is absolute
        if parsedUrl.netloc == '':

            # Cleans parsed mainURL
            if tempPageUrl[-1] is not "/":
                tempPageUrl = tempPageUrl[:tempPageUrl.rfind('/')]
            else:
                tempPageUrl = tempPageUrl[:-1]

            # path by slash
            if tempLink[0] == "/":
                tempLink = parsedPageUrl.scheme +"://" + parsedPageUrl.netloc + link

            # path by dots
            elif tempLink[0] == ".":
                #count number of dots
                dotCount = 1
                for i in range(1,len(tempLink)):
                    if tempLink[i] == ".":
                        dotCount += 1
                    else:
                        break
                #for every dot go back one level
                tempLink = tempPageUrl[:tempPageUrl.rfind('/')]
                for x in range(1,dotCount):
                    tempLink = tempPageUrl[:tempPageUrl.rfind('/')]
                tempLink = tempLink + link[dotCount:]
            else:
                # no back path
                tempLink = tempPageUrl + "/" + tempLink
        return tempLink


    def grabPage(self, url, browserType):
        #- this function opens the url using requested browser types (edge, firefox, defaults to chrome)
        #- inputs url, browseType (edge,firefox)
        #- returns the page (a file-like object with two additional methods from the urllib.response module)

        if browserType.lower() == 'edge':
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
        elif browserType.lower() == 'firefox':
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'
        else: # chrome
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        headers = {'User-Agent': user_agent}

        # creates request object
        req = urllib.request.Request(url,None,headers)

        # returns page if no errors
        try:
            return urllib.request.urlopen(req)
        except urllib.error.URLError as e:
            print("error" + e.reason)
            return None

    #gets all the links in one page
    def getPageLinks(self,page):
        print("Gathering Links From: ", page.geturl())
        parsedPage = bs(page, 'html.parser')
        links = set([])

        #finds all the links
        for link in parsedPage.findAll('img'):
            #checks to see type of link
            link = link.get('src')
            if link is not None and len(link) > 1 and '#' not in link:
                links.add(self.constructLink(page.geturl(),link))
                print("ADDED ",self.constructLink(page.geturl(),link) )

        for link in parsedPage.findAll('a'):
            link = link.get('href')
            #checks to see type of link
            if link is not None and len(link) > 1 and '#' not in link:
                links.add(self.constructLink(page.geturl(),link))

        return links

    #gets all the links from startpage and its pagesRRRRRRRRRR
    def getAllLinks(self,startPage, domain, browserType):
        #avoids opening links containing (will still return them)
        avoid = ['.pdf', '.exe', '#','jpg','.jpeg','.gif','.png', ".json", ".xml", ".xlsx"]

        # grabs all the links within the page domain
        tempdomain = urlparse(domain)

        links = set([startPage.geturl()])

        startPageUrl = tempdomain.netloc + tempdomain.path
        print("TEMP DOM", startPageUrl)

        visited = set([])
        uniqueLinks = links - visited

        while len(uniqueLinks) > 0:
            #visits every unique link not yet visited
            for uniqueLink in uniqueLinks:
                #adds the link into visited list
                visited.add(uniqueLink)
                #checks to see if page is within domain
                tempUL = urlparse(uniqueLink)
                if startPageUrl in tempUL.netloc + tempUL.path:
                    #avoids opening links in avoid
                    if not any(extension in uniqueLink for extension in avoid):
                        #navigates to the page
                        page = self.grabPage(uniqueLink, browserType)
                        #grabs all the links from the page and adds to links
                        if page is not None:
                            links = links.union(self.getPageLinks(page))
            #determines which links have not been visited from updated links
            uniqueLinks = links.difference(visited)
        return links


    def filterLinksEndsIn(self,suffix, links):
        #filters all the links that ends with suffix
        #input suffix, links (list of the links)
        newLinks = set([])
        for link in links:
            if link.endswith(tuple(suffix)):
                newLinks.add(link)
        return newLinks

    def prepareJson(self,path):
        #prepares file for writing
        with open(path, "w") as write_file:
            write_file.write('')

    def addToJson(self,path,url,fileName):
        with open(path, "a") as add_file:
            json.dump({url: fileName}, add_file, indent=4)

    def getFromJson(self,path):
        #opens file
        try:
            read_file = open(path, 'r')
        except IOError:
            open(path, 'x')
            read_file = open(path, 'r')

        #returns the Json object as python object
        stringdata = read_file.read()
        stringdata = stringdata.replace("}{", ',')

        if(stringdata == ''):
            return {'':''}
        else:
            return json.loads(stringdata)

    def downloadAllFilesWget(self,list,delay):
        # Given a list, downloads all those files

        #open json to grab list of urls (to do)
        #check if file has been already downloaded (to do)

        #create json file to store urls
        self.prepareJson("downloads/{WS_downloadedurllist}.txt")
        failedList = []
        for url in list:
            time.sleep(delay)
            try:
                parsedUrl = urlparse(url)
                fileName = str(parsedUrl.path).replace('/',"{WS_FSLASH}").replace('.',"{WS_DOT}")
                wget.download(url,'downloads/' + fileName)
                # write file : url to file
                self.addToJson("downloads/{WS_downloadedurllist}.txt", url, fileName)
            except:
                print("Failed to download ", url)
                failedList.append(url)
        if(delay < 60 and len(failedList) > 0):
            self.downloadAllFilesWget(failedList,delay+5)

    def downloadAllFilesRetrieve(self,list,delay):
        # Given a list, downloads all those files

        #open json to grab list of urls (to do)
        #check if file has been already downloaded (to do)

        #create json file to store urls
        self.prepareJson("downloads/{WS_downloadedurllist}.txt")
        failedList = []
        for url in list:
            try:
                time.sleep(delay)
                parsedUrl = urlparse(url)
                fileName = str(parsedUrl.path).replace('/',"{WS_FSLASH}")
                urlretrieve(urllib.parse.quote(url, safe=':/'),'downloads/' + fileName)

                # write file : url to file
                self.addToJson("{WS_downloadedurllist}.txt", url, fileName)
            except:
                print("Failed to download ", url)
                failedList.append(url)

        if (delay < 60 and len(failedList) > 0):
            self.downloadAllFilesRetrieve(failedList, delay + 5)


    def downloadAllFilesRequestGet(self,list,delay):
        # Given a list, downloads all those files

        #open json to grab list of urls (to do)
        data = self.getFromJson("downloads/{WS_downloadedurllist}.txt")
        totalNumOfLinks = len(list)
        failedList = []
        for url in list:
            try:
                if data.get(url) == None:
                    parsedUrl = urlparse(url)
                    fileName = str(parsedUrl.path).replace('/',"{WS_FSLASH}")
                    print(""+"downloading: " + urllib.parse.quote(url, safe=':/'))
                    r = requests.get(urllib.parse.quote(url, safe=':/'),headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'},stream=True)
                    if r.status_code == 200:
                        with open('downloads/'+ fileName , 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                    # write file : url to file
                            self.addToJson("downloads/{WS_downloadedurllist}.txt", url, fileName)
            except:
                    print("Failed to download ", url)
                    failedList.append(url)

        if (delay < 60 and len(failedList) > 0):
            self.downloadAllFilesRequestGet(failedList, delay + 5)

    def start(self,domain,url,filetype,browsertype):
        #User input)
        #domain = input("Enter search domain")
        #url = input("Enter url to start search")

        #Settings
        #domain = "https://vocabs.ands.org.au" #- only click on links that contain this at the start
        #url = "https://vocabs.ands.org.au" #- start finding links on this page
        #filetype = ".rdf" #file type you are searching for
        #browsertype = "edge" #-browser type

        #-check/create downloads directory
        if not os.path.exists("downloads"):
            os.makedirs("downloads")


        print("Gathering all links within targeted domain....")
        #- starting page
        page = self.grabPage(url,browsertype)
        #- grabs all navigatable links within domain starting with page
        links = set([])
        links = self.getAllLinks(page,domain,browsertype)


        print(links)
        print(len(links))

        #- filters list of links to just filetype

        #- check if file type is one of the special flags
        # "VIDEO", "IMAGE", "AUDIO"
        tempfiletype = list()
        if("--VIDEO" in filetype):
            tempfiletype.extend(
                ['.avi', '.m1v', '.mov', '.movie', '.mp4', '.mpa', '.mpe', '.mpeg', '.mpg', '.qt', '.webm', '.3gp',
                 '.axv', '.dl', '.dif', '.dv', '.fli', '.gl', '.ts', '.ogv', '.mxu', '.flv', '.lsf', '.lsx', '.mng',
                 '.asf', '.asx', '.wm', '.wmv', '.wmx', '.wvx', '.mpv', '.mkv'])
        if ("--IMAGE" in filetype):
            tempfiletype.extend(
                [".bmp", ".gif", ".ico", ".ief", ".jpe", ".jpeg", ".jpg", ".pbm", ".pgm", ".png", ".pnm", ".ppm",
                 ".ras", ".rgb", ".svg", ".tif", ".tiff", ".xbm", ".xpm", ".xwd", ".cpt", ".jp2", ".jpg2", ".jpm",
                 ".jpx", ".jpf", ".pcx", ".svgz", ".djvu", ".djv", ".wbmp", ".cr2", ".crw", ".cdr", ".pat", ".cdt",
                 ".erf", ".art", ".jng", ".nef", ".orf", ".psd"])
        if ("--AUDIO" in filetype):
            tempfiletype.extend(
                [".aif", ".aifc", ".aiff", ".au", ".m3u", ".mp2", ".mp3", ".ra", ".ram", ".snd", ".wav", ".amr", ".awb",
                 ".axa", ".csd", ".orc", ".sco", ".flac", ".mid", ".midi", ".kar", ".mpga", ".mpega", ".m4a", ".oga",
                 ".ogg", ".opus", ".spx", ".sid", ".gsm", ".wma", ".wax", ".rm", ".pls", ".sd2"])
        filetype = tempfiletype

        print("removing non ",filetype," links....")
        links2 = self.filterLinksEndsIn(filetype, links)
        print(links2)
        print(len(links2))

        #downloads all files in links
        print("Downloading Files....")
        self.downloadAllFilesRequestGet(links2,0.1)
        print("Complete")