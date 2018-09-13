from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import PyPDF2
import re
from PDF_Keywords_Extractor import PdfOcr

from bs4 import BeautifulSoup

#-description
#-a quick hack/script to extract keywords from pdf documents
#-intended for single use

class KeywordExtract():

    def __init__(self):
        #- ToDo: will place all objects used here instead of recreating new ones every extraction
        print(None)

    def extract(self,path):
        # - ToDo: spliting out both extract functions to only return pdf text, and create a specialise function to harvest the keywords
        # -this function uses pypdf2/pdfminer(html)/pdfminer(text) to extract keywords
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

        print(path + listofkeywords[biggest])


        return listofkeywords[biggest]
    #def writeKeywordsToFile(self):

    def extract2(self,path):
        # -Uses wand and tesseract to extract text
        # Inputs:
        # -  [path : string] where the file is located
        # Output:
        # - [data : string] the extract text
        pdf2text = PdfOcr.keywordpdftotext()
        text = pdf2text.gettext(path)
        text = self.findkeywords(text)
        self.trimoutjunk(text)
        return text

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
        temptext = text.lower()
        end = []
        #special cases
        caseend = [' 22nd international congress', "\s*[0-9]*\s*.[0-9]*\s*introduction"]
        #casestart = ["keywords:\s*(\w*\s*[,;]*)*."]
        for case in caseend:
            match = re.search(case, text)
            if match:
                end.append(match.start())
        '''
        for case in casesend:
            match = re.search(case, text)
            if match:
                print(text[match.start():match.end() - 1])
        '''
        if len(end) is not 0:
            text = text[0:min(end)]

        #trim white space
        cases = ['  ', '   ', '\t', '\n']
        for case in cases:
            text.replace(case, '')

        return text





