from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, HTMLConverter, XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO, BytesIO
import PyPDF2
import os
import re
import multiprocessing
from bs4 import BeautifulSoup

#-description
#-a quick hack/script to extract keywords from pdf documents
#-intended for single use

class KeywordExtract():

    def extract(self,path):
        # -this function runs 3 pdf extraction tools to extract the keywords
        # Inputs:
        # -  [path : string] the string of the file
        # Output:
        # - [keywords : string] the longest list of keywords out of the 3 tools.

        #-A list of keywords collected via different methods
        listofkeywords = []

        #-open file
        file = open(path, 'rb')

        #-pdfminer text
        listofkeywords.append(self.findkeywords(self.pdfminer(file,"text").replace('  ',' ')))

        #-pypdf2
        listofkeywords.append(self.findkeywords(self.pypdf2(file).replace('  ',' ')))

        #-pdfminer (HTML)
        html = self.pdfminer(file,"html")
        #parse using bs4
        soup = BeautifulSoup(html, 'html5lib')
        temp = 0
        keyword = ''

        #-loops through all spans
        for span in soup.find_all('span', style=lambda x: x and ('Italic' or 'BoldItalic') in x):
            if(temp == 1 and len(span.text) > 3):
                keyword = span.text
                break
            if("keyword" in span.text.lower()):
                temp = 1
        file.close()
        listofkeywords.append(keyword)


        #-trims string
        for i in range(0, len(listofkeywords)):
            listofkeywords[i] = self.trimoutjunk(listofkeywords[i])

        #- picks the largest string [greedy]
        biggest = 0
        for i in range(1,len(listofkeywords)):
            if len(listofkeywords[biggest]) < len(listofkeywords[i]):
                biggest = i

        return listofkeywords[biggest]


    def pdfminer(self,file,type):
        # -this function uses pdf miner to extract data in pdf documents
        # Inputs:
        # -  [file : string] where the file is located
        # -  [type : string] what type of extraction to be used (text or html)
        # Output:
        # - [data : string] the extracted data in html or text format
        resourceManager = PDFResourceManager()
        codec = 'utf-8'
        retStr = BytesIO()
        laParams = LAParams()
        if type == 'html':
            device = HTMLConverter(resourceManager,retStr,codec=codec,laparams=laParams)
        else:
            device = TextConverter(resourceManager,retStr,codec=codec,laparams=laParams)
        interpreter = PDFPageInterpreter(resourceManager,device)
        password = ""
        maxPages = 1
        caching = True
        pageNos= set()

        for page in PDFPage.get_pages(file,pageNos,maxpages=maxPages, password = password, caching=caching,check_extractable= True):
            interpreter.process_page(page)
        device.close()
        data = retStr.getvalue().decode()
        retStr.close()

        return data

    def pypdf2(self,file):
        # -this function uses pypdf2 to extract data from pdf file
        # Inputs:
        # -  [file : string] where the file is located
        # Output:
        # - [data : string] the extracted data in text format
        pyPdf = PyPDF2.PdfFileReader(file)
        noPages = pyPdf.getNumPages()
        page =pyPdf.getPage(0)
        pageContent = page.extractText()
        return pageContent


    def findkeywords(self,text):
        # -this function uses finds and seperates keywords from text
        # Inputs:
        # -  [text : string] the extracted pdf text document
        # Output:
        # - [data : string] parsed text containing keywords (will require cleaning)

        #indicators to continue building keywords
        endchars = ['-', ',', ', ',  ',   ', ', ', '\t']

        #-index of the start of keywords
        startindex = text.lower().find("keywords:")

        #--string contains no keywords (detects if recursive call)
        if startindex == -1:
            startindex = 0
        else:
            startindex = startindex + 9

        #-index of end of keywords (when there is no more end chars
        keywords = text.lower()[startindex:].split("\n")[0]

        #--if the last char is one of the end chars continue building keywords, and doesnt contain a dot
        if len(keywords) is not 0 and keywords[len(keywords)-1:] in endchars and keywords[len(keywords)-3:].count('.') is not 0:
            keywords = keywords[:len(keywords)] + self.findkeywords(text[startindex + len(keywords) + 2:])
        return keywords


    def trimoutjunk(self,text):
        # -this function cleans out junk from keywords (special cases, whitespace)
        # Inputs:
        # -  [text : string] keywords to be cleaned
        # Output:
        # - [data : string] clearned keywords

        end = []
        #special cases
        cases = [' 22nd international congress', "1. Introduction", "1.0 introduction"]
        for case in cases:
            if case.lower() in text.lower():
                end.append(text.lower().find(case.lower()))

        if len(end) is not 0:
            text = text[0:min(end)]

        #trim white space
        cases = ['  ', '   ', '\t', '\n']
        for case in cases:
            text.replace(case, '')

        return text

def errordetect(keywords):
    # -this function determines if the keywords are correct based on basic checks
    # Inputs:
    # -  [keywords : string] the keywords to check
    # Output:
    # - [result : boolean] if it is an error or not
    #-size errors
    if len(keywords) < 4 or len(keywords) > 250:
        return True

    #-basic counting of words
    temp = keywords.split()

    #keywords vs number of words (+2 extra slack for 2 keywords)
    if len(temp) > max(keywords.count(','),keywords.count(';'))*5 + 2:
        return True

    return False

def extractpdfs(listofpdfs, extractor, errorfiles, folder):
    # -this function extracts text from a list of keywords
    # Inputs:
    # -  [listofpdfs : list[strings] - list of pdfs to extract keywords from
    # -  [extractor : KeywordExtract - extraction object
    # -  [errorfiles : multiprocess.Queue] - queue used to store files names with potential problems
    # -  [folder : string] - the folder where the pdfs are

    totalcount = 0
    sizeoflist = len(listofpdfs)
    for pdf in listofpdfs:
        # print("extracting ... " + folder + pdf)
        keywords = extractor.extract(folder + pdf)
        totalcount += 1

        #checks for error
        if errordetect(keywords):
            print("potential error in ", pdf)
            print(pdf, keywords)
            errorfiles.put(pdf + "\t" + keywords)

        #prints progress
        print("[",os.getpid(), "]:",'\t',totalcount, "/", sizeoflist)


if __name__ == '__main__':

    #-settings
    cores = 4 #number of cores to use
    folder = "downloads/" # the folder pdfs are in

    #-testing vars
    #listofpdfs2 = ['-MODSIM03-Volume_03-B02-04_Cao.pdf']
    #folder = "testpdf/"

    #-grabs files in folder
    completelistofpdfs = os.listdir(folder)

    #-clean up pdfs removing non modsim files
    listofpdfs = []

    for pdf in completelistofpdfs:
        #removes all none pdfs/ non modsim files / abstract books
        pdflower = pdf.lower()
        if ".pdf" in pdflower and "modsim" in pdflower and "abstracts" not in pdflower:
            listofpdfs.append(pdf)

    #-counter vars
    errorcount = 0
    totalcount = 0
    sizeoflist = len(listofpdfs)

    #-extract object
    Test = KeywordExtract()

    #- Process vars
    errorfiles = multiprocessing.Queue()
    processes = []

    #-split the list into sections for multiprocessing
    start = 0
    interval = int(sizeoflist/cores)
    end = interval

    #-creates the list of processes to run
    for i in range(0,cores):
        if i == cores - 1:
            processes.append(multiprocessing.Process(target=extractpdfs, args=(listofpdfs[start:], Test, errorfiles, folder)))
        else:
            processes.append(multiprocessing.Process(target=extractpdfs, args=(listofpdfs[start:end],Test, errorfiles,folder)))
            start += interval
            end += interval


    #-runs the proceses
    for p in processes:
        p.start()

    #-closes the completed processes
    for p in processes:
        p.join()

    #gets the file names with errors from the process queue
    results = [errorfiles.get() for p in processes]
    # prints total count of keywords under 3 letters and not over 150 letters
    print("Errors: ", len(results),"/",totalcount)

    #record error file
    thefile = open("error.txt",'w')
    for result in results:
        thefile.write("%s\n" % result)