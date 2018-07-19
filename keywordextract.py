from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, HTMLConverter, XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO, BytesIO
import PyPDF2
import os
from bs4 import BeautifulSoup

class KeywordExtract():

    def extract(self,path):
        #open file
        file = open(path, 'rb')

        #pdfminer text
        print("pdfminer: ", repr(self.findkeywords(self.pdfminer(file,"text"))))

        #pypdf2
        print("PyPDF2: ", repr(self.findkeywords(self.pypdf2(file))))
        #pdfminer (HTML)

        html = self.pdfminer(file,"html")
        #parse using bs4
        soup = BeautifulSoup(html, 'html5lib')
        temp = 0
        keywords = ''

        #loops through all spans
        for span in soup.find_all('span', style=lambda x: x and ('Italic' or 'BoldItalic') in x):
            if(temp == 1 and len(span.text) > 3):
                keywords = span.text
                break
            if("keyword" in span.text.lower()):
                temp = 1


        file.close()
        return keywords


    def pdfminer(self,file,type):
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
        pyPdf = PyPDF2.PdfFileReader(file)
        noPages = pyPdf.getNumPages()
        page =pyPdf.getPage(0)
        pageContent = page.extractText()


        return pageContent
    #def check(self,file):

    def findkeywords(self,text):
        endchars = ['\t','\n','\r','\n\n',"\n","\n\n"]
        start = text.lower().find("keywords:") + 9
        end = min(text.lower()[start:].find(char) for char in endchars)
        return text[start:end]

#settings
folder = "downloads/"
Test = KeywordExtract()
listofpdfs = os.listdir("downloads/")#['testpdf/test.pdf',"testpdf/test2.pdf","testpdf/test3.pdf","testpdf/test4.pdf"]
#print("test4",Test.extract("test4.pdf"))
errorfiles = []
errorcount = 0
totalcount = 0
for pdf in listofpdfs:
    if ".pdf" in pdf:
        print("extracting ... " + folder + pdf)
        keywords = Test.extract(folder + pdf)
        print(pdf,keywords)
        if len(keywords) < 4:
            errorcount += 1
            errorfiles.append(pdf)
        totalcount += 1

#prints total count of keywords under 3 letters
print("Keywords < 3: ", errorcount,"/",totalcount)
print(errorfiles)