from SKOS_Write_Read import SkosReaderWriter
import collections
import os

test = SkosReaderWriter.SkosReaderWriter()

mainKeywords = collections.defaultdict(lambda: collections.defaultdict(list))
extraKeywords = collections.defaultdict(lambda: collections.defaultdict(list))

# - Loads up all the Excel keywords
for path in os.listdir('excel'):
    mainKeywords.update(test.loadFromExcel("excel/"+path))

#xml
#-extract xml/rdf files
for xmlpath in os.listdir('xml'):
    xmlKeywords = test.readSkosXml("xml/"+xmlpath)
    if len(xmlKeywords) > 0:
        mainKeywords = test.mergeSkosDicts(mainKeywords, xmlKeywords)

#xml
for jsonpath in os.listdir('json'):
    jsonKeywords = test.readSkosJson("json/"+jsonpath)
    if len(jsonKeywords) > 0:
        mainKeywords = test.mergeSkosDicts(mainKeywords, jsonKeywords)

test.writeToExcel("new.xlsx", mainKeywords)
