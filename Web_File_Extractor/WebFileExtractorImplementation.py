from Web_File_Extractor import WebFileExtractor

test = WebFileExtractor.WebFileExtractor()
# Settings
domain = "www.roselinebunnies.com" #- only click on links that contain this at the start
url = "http://www.roselinebunnies.com/" #- start finding links on this page
filetype = "--IMAGE" #file type you are searching for
browsertype = "edge" #-browser type

test.start(domain,url,filetype,browsertype)